"""End-to-end smoke test against a running api + bucket (+ worker, or drains in-process).

    python -m scripts.smoke [--api http://127.0.0.1:4100]

Happy path: register -> presigned upload of a photo -> report -> listed and searched ->
photo read through a presigned GET. Negative checks prove the bucket is private and the
upload rules are enforced. Exit code 1 on any failure.
"""

import argparse
import sys
import time
import uuid
from collections.abc import Callable
from urllib.parse import urlsplit, urlunsplit

import httpx

from app.registry import load_models
from app.shared.infrastructure.config import get_settings
from app.shared.infrastructure.storage import get_storage
from app.worker import drain
from scripts.api_client import Api, ApiError
from scripts.placeholders import silhouette

results: list[tuple[bool, str]] = []


def check(name: str, fn: Callable[[], object]) -> None:
    try:
        ok = fn()
        results.append((ok is not False, name))
    except Exception as e:  # noqa: BLE001
        results.append((False, f"{name} ({type(e).__name__}: {str(e)[:160]})"))


def status_of(fn: Callable[[], object]) -> int:
    try:
        fn()
        return 200
    except ApiError as e:
        return e.status


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default=f"http://127.0.0.1:{get_settings().api_port}")
    args = ap.parse_args()
    load_models()
    api = Api(args.api)
    tag = uuid.uuid4().hex[:8]
    pw = f"Smoke-{uuid.uuid4().hex[:10]}1"

    def register(handle: str) -> Api:
        api.call("POST", "/api/auth/register", {"email": f"{handle}-{tag}@smoke.local", "password": pw,
                                                "name": f"Smoke {handle}", "city": "Cairo"})
        return api.login(f"{handle}-{tag}@smoke.local", pw)

    a, b = register("alice"), register("bob")
    photo = silhouette(7)
    state: dict[str, object] = {}

    # ── happy path ──
    def presigned_upload() -> bool:
        ticket = a.request_upload(photo, "image/jpeg", "report_photo")
        assert ticket["method"] == "PUT" and "X-Amz-Signature" in ticket["url"]
        put = Api.put(ticket, photo)
        assert put.status_code in (200, 201, 204), put.status_code
        confirmed = a.call("POST", f"/api/uploads/{ticket['upload_id']}/confirm")
        assert confirmed["size"] == len(photo) and confirmed["content_type"] == "image/jpeg"
        state["upload_id"], state["key"] = ticket["upload_id"], ticket["key"]
        return True

    def create_report() -> bool:
        r = a.call("POST", "/api/reports", {
            "kind": "missing", "child_name": f"Smoke{tag}", "gender": "male", "age": 7, "city": "Cairo",
            "description": f"Smoke test report {tag}: blue jacket, last seen near the station.",
            "photo_upload_ids": [state["upload_id"]], "seen_on": time.strftime("%Y-%m-%d"),
        }, expect=201)
        state["report"] = r
        return len(r["photos"]) == 1 and r["can_edit"] is True

    def listed() -> bool:
        page = api.call("GET", "/api/reports", params={"kind": "missing", "per_page": 50})
        return any(i["id"] == state["report"]["id"] for i in page["items"])  # type: ignore[index]

    def searched() -> bool:
        hit = api.call("GET", "/api/reports", params={"q": tag})
        miss = api.call("GET", "/api/reports", params={"q": tag, "age_from": 10, "age_to": 12})
        legacy = api.call("GET", "/api/reports", params={"q": tag, "type": "missed", "gender": "male", "age": 7})
        return hit["total"] == 1 and miss["total"] == 0 and legacy["total"] == 1

    def presigned_get() -> bool:
        r = api.call("GET", f"/api/reports/{state['report']['id']}")  # type: ignore[index]
        url = r["photos"][0]["url"]
        state["photo_url"] = url
        assert "X-Amz-Expires=" in url
        res = httpx.get(url, timeout=20)
        return res.status_code == 200 and res.content == photo

    check("presigned PUT upload + confirm", presigned_upload)
    check("create report with the photo", create_report)
    check("report is listed", listed)
    check("report is found by search (text, age range, v1 filters)", searched)
    check("photo readable through presigned GET (same bytes)", presigned_get)

    # ── negative checks ──
    def unsigned_get_denied() -> bool:
        parts = urlsplit(str(state["photo_url"]))
        plain = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        return httpx.get(plain, timeout=10).status_code == 403

    def tampered_get_denied() -> bool:
        url = str(state["photo_url"]).replace(".jpg?", "x.jpg?")
        return httpx.get(url, timeout=10).status_code in (403, 404)

    def expired_get_denied() -> bool:
        url = get_storage().presign_get(str(state["key"]), ttl_seconds=1)
        time.sleep(2.5)
        return httpx.get(url, timeout=10).status_code == 403

    def other_user_cannot_confirm() -> bool:
        ticket = a.request_upload(photo, "image/jpeg", "report_photo")
        Api.put(ticket, photo)
        return status_of(lambda: b.call("POST", f"/api/uploads/{ticket['upload_id']}/confirm")) == 403

    def confirm_before_upload() -> bool:
        ticket = a.request_upload(photo, "image/jpeg", "report_photo")
        return status_of(lambda: a.call("POST", f"/api/uploads/{ticket['upload_id']}/confirm")) == 409

    def size_mismatch_rejected_and_deleted() -> bool:
        ticket = a.request_upload(photo, "image/jpeg", "report_photo", declared=1000)
        put = Api.put(ticket, photo)  # real size != declared size
        code = status_of(lambda: a.call("POST", f"/api/uploads/{ticket['upload_id']}/confirm"))
        gone = get_storage().head(ticket["key"]) is None
        again = status_of(lambda: a.call("POST", f"/api/uploads/{ticket['upload_id']}/confirm"))
        return put.status_code in (200, 204) and code == 422 and gone and again == 409

    def wrong_content_type_put_denied() -> bool:
        ticket = a.request_upload(photo, "image/jpeg", "report_photo")
        return Api.put(ticket, photo, content_type="text/html").status_code == 403

    def disallowed_requests() -> bool:
        too_big = status_of(lambda: a.request_upload(b"x", "image/jpeg", "report_photo", declared=9 * 1024 * 1024))
        bad_type = status_of(lambda: a.request_upload(b"x", "application/pdf", "report_photo"))
        svg = status_of(lambda: a.request_upload(b"x", "image/svg+xml", "avatar"))
        anon = status_of(lambda: api.request_upload(b"x", "image/jpeg", "report_photo"))
        return (too_big, bad_type, svg, anon) == (422, 422, 422, 401)

    def cannot_attach_someone_elses_file() -> bool:
        uid = a.upload(photo)
        code = status_of(lambda: b.call("POST", "/api/reports", {
            "kind": "found", "gender": "male", "age": 7, "city": "Cairo",
            "description": "Trying to attach somebody else's upload.", "photo_upload_ids": [uid]}))
        return code == 403

    def cannot_attach_twice() -> bool:
        return status_of(lambda: a.call("POST", "/api/reports", {
            "kind": "missing", "child_name": "Twice", "city": "Cairo", "description": "Reusing an attached upload.",
            "photo_upload_ids": [state["upload_id"]]})) == 409

    def stranger_cannot_edit() -> bool:
        rid = state["report"]["id"]  # type: ignore[index]
        return status_of(lambda: b.call("POST", f"/api/reports/{rid}/resolve")) == 403

    check("unsigned GET on the bucket is denied (private bucket)", unsigned_get_denied)
    check("tampered presigned GET is denied", tampered_get_denied)
    check("expired presigned GET is denied", expired_get_denied)
    check("another user cannot confirm my upload", other_user_cannot_confirm)
    check("confirm before upload -> 409", confirm_before_upload)
    check("size mismatch -> 422, object deleted, upload stays rejected", size_mismatch_rejected_and_deleted)
    check("PUT with another Content-Type is refused by the bucket", wrong_content_type_put_denied)
    check("too big / wrong type / svg / anonymous upload requests refused", disallowed_requests)
    check("cannot attach another user's upload", cannot_attach_someone_elses_file)
    check("cannot attach the same upload twice", cannot_attach_twice)
    check("stranger cannot change a report", stranger_cannot_edit)

    # ── worker: matching + notifications ──
    def matching_runs() -> bool:
        f_ticket = b.upload(silhouette(8))
        b.call("POST", "/api/reports", {
            "kind": "found", "gender": "male", "age": 7, "city": "Cairo", "seen_on": time.strftime("%Y-%m-%d"),
            "description": f"Smoke found child {tag} near the station.", "photo_upload_ids": [f_ticket]})
        deadline = time.time() + 20
        while time.time() < deadline:
            drain(20)
            mine = a.call("GET", "/api/matches")
            if any(m["missing"]["id"] == state["report"]["id"] for m in mine):  # type: ignore[index]
                return True
            time.sleep(0.5)
        return False

    def notified() -> bool:
        return a.call("GET", "/api/notifications/unread-count")["unread"] >= 1

    def delete_cleans_objects() -> bool:
        rid = state["report"]["id"]  # type: ignore[index]
        a.call("DELETE", f"/api/reports/{rid}", expect=204)
        deadline = time.time() + 15
        while time.time() < deadline:
            drain(20)
            if get_storage().head(str(state["key"])) is None:
                return True
            time.sleep(0.5)
        return False

    check("worker suggests a match for the new found report", matching_runs)
    check("both reporters get a notification", notified)
    check("deleting a report deletes its objects from the bucket", delete_cleans_objects)

    width = max(len(n) for _, n in results)
    for ok, name in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name.ljust(width)}")
    failed = sum(1 for ok, _ in results if not ok)
    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
