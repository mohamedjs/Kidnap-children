"""Demo seed. Invented people, invented reports, generated silhouette pictures - no real data.

    python -m scripts.seed [--reset] [--api http://127.0.0.1:4100]

Needs the api running (uploads go through the real presigned flow). The worker is run
in-process at the end so matches and notifications exist straight away.
All demo accounts use ADMIN_SEED_PASSWORD from .env (never printed).
"""

import argparse
import sys
from datetime import date, timedelta
from typing import Any

from sqlalchemy import text

from app.registry import load_models
from app.shared.infrastructure.config import get_settings
from app.shared.infrastructure.db import new_session
from app.shared.infrastructure.storage import get_storage
from app.worker import drain
from scripts.api_client import Api, ApiError
from scripts.placeholders import avatar, cover, silhouette

TODAY = date.today()


def d(days_ago: int) -> str:
    return (TODAY - timedelta(days=days_ago)).isoformat()


USERS = [
    ("mona", "منى سالم", "القاهرة", "+20 100 000 0101"),
    ("karim", "كريم عادل", "القاهرة", "+20 100 000 0102"),
    ("heba", "هبة فاروق", "الجيزة", "+20 100 000 0103"),
    ("tarek", "طارق نبيل", "الإسكندرية", "+20 100 000 0104"),
    ("sara", "سارة مجدي", "المنصورة", "+20 100 000 0105"),
    ("omar", "عمر حسين", "طنطا", "+20 100 000 0106"),
]

# (owner, kind, child_name, gender, age, city, area, lat, lng, days_ago, description, photos, resolve)
REPORTS: list[tuple[Any, ...]] = [
    ("mona", "missing", "يوسف", "male", 6, "القاهرة", "شبرا", 30.0711, 31.2459, 16,
     "بلاغ تجريبي: خرج من المدرسة ولم يعد. كان يرتدي سويتر أزرق وبنطلون جينز وحذاء رياضي أبيض.", 2, False),
    ("heba", "missing", "مريم", "female", 9, "الجيزة", "الهرم", 29.9870, 31.1310, 11,
     "بلاغ تجريبي: تاهت في سوق الهرم مساءً. شعرها طويل مربوط، ترتدي فستانًا ورديًا وحقيبة ظهر بنفسجية.", 2, False),
    ("tarek", "missing", "آدم", "male", 4, "الإسكندرية", "سموحة", 31.2156, 29.9553, 58,
     "بلاغ تجريبي: فُقد في حديقة عامة يوم الجمعة. يتكلم قليلًا، يعرف اسمه واسم والدته فقط.", 1, False),
    ("sara", "missing", "ليلى", "female", 12, "المنصورة", "توريل", 31.0409, 31.3785, 5,
     "بلاغ تجريبي: لم تعد من درس خصوصي. ترتدي نظارة طبية وجاكيت أخضر.", 1, False),
    ("omar", "missing", "علي", "male", 8, "أسيوط", "الوليدية", 27.1783, 31.1859, 140,
     "بلاغ تجريبي: تم العثور عليه وعاد لأسرته بفضل مشاركات المتطوعين. شكرًا لكل من ساعد.", 1, True),
    ("karim", "found", None, "male", 6, "القاهرة", "روض الفرج", 30.0860, 31.2440, 14,
     "بلاغ تجريبي: وجدنا طفلًا تائهًا بجوار محطة المترو، عمره حوالي ست سنوات، يرتدي سويتر أزرق. موجود الآن في قسم الشرطة.", 2, False),
    ("mona", "found", "تقول اسمها مريم", "female", 9, "الجيزة", "فيصل", 30.0010, 31.1500, 9,
     "بلاغ تجريبي: طفلة وصلت لجمعية أهلية في فيصل، تقول إن اسمها مريم وإنها من منطقة الهرم.", 1, False),
    ("tarek", "found", None, "female", 3, "الإسكندرية", "محرم بك", 31.1950, 29.9200, 3,
     "بلاغ تجريبي: طفلة صغيرة وُجدت أمام مخبز، لا تستطيع ذكر اسم أهلها. ترتدي جاكيت أصفر.", 1, False),
    ("omar", "found", None, "male", 13, "طنطا", "سيجر", 30.7865, 31.0004, 2,
     "بلاغ تجريبي: ولد في الثالثة عشرة تقريبًا، يبدو أنه جاء بالقطار من محافظة أخرى. في رعاية دار أيتام.", 1, False),
]


def reset() -> None:
    with new_session() as s:
        tables = ["report_flags", "notifications", "messages", "likes", "comments", "face_embeddings", "matches",
                  "report_photos", "reports", "uploads", "password_resets", "outbox_events", "users"]
        s.execute(text("TRUNCATE " + ", ".join(tables) + " CASCADE"))
        s.commit()
    st = get_storage()
    paginator = st.internal.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=st.bucket):
        for obj in page.get("Contents", []):
            st.delete(obj["Key"])
    print("reset: tables truncated, bucket emptied")


def make_admin(email: str) -> None:
    with new_session() as s:
        s.execute(text("UPDATE users SET role='admin', token_version=token_version+1 WHERE email=:e"), {"e": email})
        s.commit()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--api", default=f"http://127.0.0.1:{get_settings().api_port}")
    args = ap.parse_args()
    load_models()
    settings = get_settings()
    password = settings.admin_seed_password
    if not password:
        sys.exit("ADMIN_SEED_PASSWORD is not set (run scripts/gen-dev-env.py)")
    if args.reset:
        reset()
    api = Api(args.api)

    def account(email: str, name: str, city: str, phone: str | None) -> Api:
        try:
            api.call("POST", "/api/auth/register", {"email": email, "password": password, "name": name,
                                                    "city": city, "phone": phone})
        except ApiError as e:
            if e.status != 409:
                raise
            return api.login(email, password)  # already seeded
        return api.login(email, password)

    try:
        api.call("POST", "/api/auth/login", {"email": settings.admin_seed_email, "password": password})
        print("demo data already present - use --reset to rebuild")
        return
    except ApiError:
        pass

    account(settings.admin_seed_email, "مشرف المنصة", "القاهرة", None)
    make_admin(settings.admin_seed_email)
    admin = api.login(settings.admin_seed_email, password)

    users: dict[str, Api] = {}
    for i, (handle, name, city, phone) in enumerate(USERS):
        u = account(f"{handle}@demo.local", name, city, phone)
        u.call("PATCH", "/api/profile", {
            "bio": "حساب تجريبي لعرض المنصة.",
            "avatar_upload_id": u.upload(avatar(i), purpose="avatar", name="avatar.jpg"),
            "cover_upload_id": u.upload(cover(i), purpose="cover", name="cover.jpg"),
        })
        users[handle] = u

    ids: list[str] = []
    for n, (owner, kind, child, gender, age, city, area, lat, lng, ago, desc, photos, resolve) in enumerate(REPORTS):
        u = users[owner]
        uploads = [u.upload(silhouette(n * 3 + k, hair=gender == "female"), name=f"photo{k}.jpg")
                   for k in range(photos)]
        r = u.call("POST", "/api/reports", {
            "kind": kind, "child_name": child, "gender": gender, "age": age, "city": city, "area": area,
            "lat": lat, "lng": lng, "seen_on": d(ago), "description": desc,
            "contact_phone": USERS[[x[0] for x in USERS].index(owner)][3], "photo_upload_ids": uploads,
        })
        ids.append(r["id"])
        if resolve:
            u.call("POST", f"/api/reports/{r['id']}/resolve")

    # community activity
    users["sara"].call("POST", f"/api/reports/{ids[0]}/comments", {"body": "شاركت البلاغ في جروب الحي، ربنا يرجعه بالسلامة."})
    users["omar"].call("POST", f"/api/reports/{ids[0]}/comments", {"body": "في طفل شبهه في بلاغ روض الفرج، راجعوا التطابقات."})
    users["karim"].call("POST", f"/api/reports/{ids[5]}/comments", {"body": "الطفل بخير وموجود مع الشرطة النسائية."})
    users["tarek"].call("POST", f"/api/reports/{ids[1]}/comments", {"body": "نشرتها على صفحة المنطقة."})
    users["heba"].call("POST", f"/api/reports/{ids[4]}/comments", {"body": "الحمد لله على السلامة 🤍"})
    for handle in ("karim", "heba", "sara", "omar"):
        users[handle].call("POST", f"/api/reports/{ids[0]}/like")
    for handle in ("mona", "tarek"):
        users[handle].call("POST", f"/api/reports/{ids[1]}/like")
    users["mona"].call("POST", f"/api/reports/{ids[5]}/like")

    karim_id = users["karim"].call("GET", "/api/auth/me")["id"]
    mona_id = users["mona"].call("GET", "/api/auth/me")["id"]
    users["mona"].call("POST", "/api/messages", {"recipient_id": karim_id,
                                                 "body": "السلام عليكم، شفت بلاغك عن الطفل في روض الفرج. ممكن صورة أوضح؟"})
    users["karim"].call("POST", "/api/messages", {"recipient_id": mona_id,
                                                  "body": "وعليكم السلام، أكيد. هو في قسم روض الفرج دلوقتي.",
                                                  "attachment_upload_id": users["karim"].upload(silhouette(40), purpose="message_attachment", name="photo.jpg")})
    users["mona"].call("POST", "/api/messages", {"recipient_id": karim_id, "body": "جاية حالًا، شكرًا جدًا 🙏"})

    users["omar"].call("POST", f"/api/reports/{ids[7]}/flag", {"reason": "duplicate", "note": "يبدو مكررًا"})

    n = drain(200)
    stats = admin.call("GET", "/api/reports/stats")
    matches = users["mona"].call("GET", "/api/matches")
    print(f"seeded {len(USERS) + 1} accounts, {len(ids)} reports; worker handled {n} events; "
          f"stats={stats}; matches for mona={len(matches)}")


if __name__ == "__main__":
    main()
