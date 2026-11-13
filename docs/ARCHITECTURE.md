# Architecture (v2)

```
Browser (Vue 3, :3100) ──/api──► api (FastAPI, :4100) ──► PostgreSQL 17 (:5435)
   │                                  │  └── outbox_events (same transaction as the change)
   └── PUT / GET on presigned URLs ──►│  S3-compatible bucket (:9010 in dev, private)
                                      ▼
worker (same codebase) ── polls outbox ──► module handlers: matching + face analysis,
                                           notifications, media cleanup, dev mailer, n8n
```

## Modular monolith

`backend/app/modules/<module>/` with four layers:

| Layer | May import | Must not import |
| --- | --- | --- |
| `domain/` | stdlib, `app.shared.domain` | FastAPI, Pydantic, SQLAlchemy, boto3, httpx, OpenCV, numpy, other modules, other layers |
| `application/` | its domain, `app.shared.domain`, `app.shared.application`, other modules' public API | frameworks, SQLAlchemy, its own infrastructure/presentation |
| `infrastructure/` | SQLAlchemy, boto3, httpx, OpenCV, its application/domain | — |
| `presentation/` | FastAPI, Pydantic, factories | SQLAlchemy directly |

- A module is used by others **only through its `__init__.py`** (`from app.modules import reports` / `from app.modules.reports import ReportsService`), which declares `__all__`.
- Only `infrastructure/` (module or `app/shared/infrastructure`) touches SQLAlchemy, psycopg, boto3, httpx, OpenCV.
- Module dependencies are acyclic.
- `backend/tests/test_architecture.py` checks all of this with an AST walk on every test run.

| Module | Owns | Depends on |
| --- | --- | --- |
| `media` | uploads, presigned PUT/GET, object cleanup | — |
| `identity` | accounts, argon2id + JWT, logout (token version), password reset, profiles, admin user mgmt | media |
| `reports` | missing / found reports, photos, status lifecycle, search | media, identity (presentation) |
| `matching` | attribute scoring, face pipeline (worker), match decisions | reports |
| `engagement` | comments, likes | reports, identity |
| `messaging` | 1:1 messages + attachments | identity, media |
| `notifications` | in-app notifications from events | identity |
| `moderation` | flags, auto-hide, admin hide/restore | reports |
| `geo` | optional reverse geocoding (Google key from env) | — |

Cross-module side effects are **domain events** written to `outbox_events` in the same
transaction, delivered by the worker (`SELECT … FOR UPDATE SKIP LOCKED`, retries with
back-off, sensitive payloads redacted after delivery). Event names live in
`app/shared/domain/events.py`.

## Files: presigned URLs

1. `POST /api/uploads {purpose, content_type, size}` → policy check (type allowlist, size cap
   per purpose), server-chosen key `purpose/<owner>/<uuid>.<ext>`, pending row with expiry,
   presigned **PUT** (Content-Type is signed).
2. Browser PUTs the bytes straight to the bucket.
3. `POST /api/uploads/{id}/confirm` → owner + expiry check, `HEAD` the object; size must
   equal the declared size and stay under the cap, type must match. Otherwise the object is
   deleted and the upload marked rejected.
4. Other modules `claim` ready uploads (owner + purpose + not attached yet).
5. Reads: every response mints a fresh presigned **GET** (300 s). Nothing stores URLs; the
   bucket has no public access. File bytes never pass through the api (the worker reads
   photos only for face analysis).
6. Deleting a report or replacing an avatar emits an event; the worker deletes the objects.
   Pending uploads that were never confirmed are swept hourly.

Dev uses SeaweedFS's S3 gateway (the `minio/minio` image is no longer on Docker Hub).
Prod: any S3-compatible bucket via `S3_*` env (`S3_ENDPOINT` empty for AWS).

## Matching

`matching/domain/scoring.py` (unit-tested): impossible pairs are excluded (different gender,
age gap > 4 after accounting for time passed, child found > 30 days before going missing);
otherwise gender 25 + age 30 + place 25 (haversine, or same normalised city) + time 20.
Face similarity, when both sides have embeddings, is blended 60/40. Suggestions ≥ 60.

The face pipeline (v1 `ai_service`) is a `FaceAnalyzer` port. The default adapter is OpenCV
Haar detection + a DCT descriptor: deterministic, finds re-posted/near-duplicate photos, **not**
an age-invariant recogniser. v1's "ArcFace" net had random weights. A trained model can be
added as another adapter.

## Frontend

`web/` — Vue 3 + Vite + vue-router, presentation only. Arabic RTL by default, English LTR
toggle (`app-locale`), dark by default with light toggle (`app-theme`), logical CSS only,
all strings via `t(key)` in `src/lib/i18n.ts`. Counters poll every 20 s (v1 used Pusher).

## API contract

`{ "success": true, "data": … }` / `{ "success": false, "error": { "code", "message" } }`,
snake_case, ISO dates. OpenAPI at `/api/docs`.
