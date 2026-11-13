from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.modules.media.domain.policy import (
    MB,
    PENDING,
    READY,
    REJECTED,
    Upload,
    object_key,
    policy_for,
)
from app.shared.domain.errors import Conflict, Forbidden, Invalid

NOW = datetime(2026, 11, 13, 12, 0, tzinfo=UTC)


def upload(**kw: object) -> Upload:
    base: dict[str, object] = dict(id=uuid4(), owner_id=uuid4(), key="k", purpose="report_photo",
                                   content_type="image/jpeg", declared_size=1000, status=PENDING,
                                   expires_at=NOW + timedelta(minutes=5))
    base.update(kw)
    return Upload(**base)  # type: ignore[arg-type]


def test_allows_images_for_report_photos() -> None:
    assert policy_for("report_photo", "image/jpeg", 2 * MB).max_bytes == 8 * MB
    assert policy_for("report_photo", "IMAGE/PNG; charset=binary", 10).max_bytes == 8 * MB


@pytest.mark.parametrize(("purpose", "ctype", "size", "code"), [
    ("report_photo", "application/pdf", 10, "upload_type"),
    ("report_photo", "image/svg+xml", 10, "upload_type"),
    ("report_photo", "image/jpeg", 9 * MB, "upload_size"),
    ("avatar", "image/jpeg", 6 * MB, "upload_size"),
    ("avatar", "image/jpeg", 0, "upload_size"),
    ("profile_video", "video/mp4", 10, "upload_purpose"),
])
def test_rejects_bad_requests(purpose: str, ctype: str, size: int, code: str) -> None:
    with pytest.raises(Invalid) as e:
        policy_for(purpose, ctype, size)
    assert e.value.code == code


def test_pdf_only_for_message_attachments() -> None:
    assert policy_for("message_attachment", "application/pdf", MB)


def test_key_is_server_chosen_under_owner_prefix() -> None:
    owner, uid = uuid4(), uuid4()
    assert object_key("avatar", owner, uid, "image/webp") == f"avatar/{owner}/{uid}.webp"


def test_confirm_only_by_owner_and_before_expiry() -> None:
    u = upload()
    with pytest.raises(Forbidden):
        u.check_confirmable(uuid4(), NOW)
    with pytest.raises(Invalid) as e:
        u.check_confirmable(u.owner_id, NOW + timedelta(minutes=6))
    assert e.value.code == "upload_expired"
    u.check_confirmable(u.owner_id, NOW)
    with pytest.raises(Conflict):
        upload(owner_id=u.owner_id, status=REJECTED).check_confirmable(u.owner_id, NOW)


@pytest.mark.parametrize(("size", "ctype", "reason"), [
    (None, None, "missing"),
    (9 * MB, "image/jpeg", "too_large"),
    (999, "image/jpeg", "size_mismatch"),
    (1000, "image/png", "type_mismatch"),
    (1000, "image/jpeg", None),
])
def test_verdict_checks_the_stored_object(size: int | None, ctype: str | None, reason: str | None) -> None:
    assert upload().verdict(size, ctype) == reason


def test_attach_rules() -> None:
    u = upload(status=READY)
    with pytest.raises(Forbidden):
        u.check_attachable(uuid4(), "report_photo")
    with pytest.raises(Invalid):
        u.check_attachable(u.owner_id, "avatar")
    with pytest.raises(Invalid):
        upload(owner_id=u.owner_id).check_attachable(u.owner_id, "report_photo")  # still pending
    with pytest.raises(Conflict):
        upload(owner_id=u.owner_id, status=READY, attached=True).check_attachable(u.owner_id, "report_photo")
    u.check_attachable(u.owner_id, "report_photo")
