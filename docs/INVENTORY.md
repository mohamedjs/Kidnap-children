# Kidnap-children — Inventory of the v1 project

Written 2026-11-13, before the v2 rebuild. It describes the repository as it was at
tag **`v1-laravel`** (commit `b1b5b791`, branch `feature/ai-image`). The v1 code is
kept unchanged under `legacy/v1-laravel/` and at that tag.

## 1. What the project is

A social platform for finding missing children. Families and the public post
**reports** of a missing child or of a child that was found, with photos. Other
users comment, like, and message the poster privately. The system tries to
**match** missing reports with found reports (the original idea: face similarity
that survives age changes) and notifies both owners.

## 2. Stack as found

| Part | Technology | State |
| --- | --- | --- |
| Web + API | Laravel (PHP 7.x era, 2019; patched for Composer 2 in 2026-07) | Two parallel controller sets: `Frontend/*` (Blade + session) and `Api/*` (Passport tokens) |
| Frontend | Blade layouts + **Vue 2** components (Laravel Mix 4, webpack, jQuery, Bootstrap 4 RTL, vee-validate 2, laravel-echo + pusher) | 8 components in `resources/js/components/` (~3.4k lines) |
| DB | MySQL (migrations in `database/migrations`, plus an older dump `gb.sql`) | |
| Queue | Laravel database queue (`jobs`, `failed_jobs`) | `ProcessImageWithAIService` job |
| Realtime | Laravel broadcasting (Echo/Pusher) — events `PostEvent`, `CommentPost`, `LikePost`, `ChatMessageSent`, `Notification`, `AiMatchFound` | needs a Pusher account; no config committed |
| AI | `ai_service/`: Python **FastAPI** + PyTorch + OpenCV + FAISS | see §5 — matching never actually worked |
| Automation | `n8n/workflows/*.json` (5 blueprints: post alert, AI-match alert, CRM/partner syndication, social broadcast, partner GeoJSON feed) | not wired to the app; need external accounts |
| Docker | `docker-compose.yml`: app (php-fpm), nginx :8080, ai_service :8000, queue, scheduler, mysql :33066, redis :6379 | |

## 3. Features (from routes, controllers, Vue components, README)

| Feature | v1 behaviour |
| --- | --- |
| Auth | register, login, logout, `me` (Passport); web login/register/password reset/email verification (Laravel `Auth::routes()`) |
| Profile | view public profile, update own info (name, phone, address, gender, birth date), upload avatar and background image, "found persons" / "missed persons" lists per user |
| Reports (`posts`) | create / update / delete (owner only via `PostPolicy`), multiple images per report, fields: name, gender, age, birth date, description, lat/lng, type `missed` \| `founded` |
| Search | text over name + description, filters type, gender, exact age, age range `from`/`to`, `user_id`; paginated 15 |
| Comments | list, add, delete (author or report owner via `CommentPolicy`) |
| Likes | toggle, list |
| Private messages | conversations with last message + unread count, thread (opening marks seen), send (not to yourself), mark read; v1 web chat also sent images (`images/chat` paths), `gb.sql` has `message_type` |
| Notifications | list with unread count, mark one / all read; created on new post, chat message, AI match |
| Matching | after image upload a queued job sends each image to the AI service (`/api/v1/index`, `/api/v1/compare`), stores `ai_matches` (confidence 0–100, `face_detected`, status `matched` / `no_face` / `failed`), syncs legacy `post_results`, notifies both owners; manual re-process endpoint; `AiMatchComparison.vue` side-by-side view |
| Geocoding | `GET /address/{lat}/{lng}/{lang}` calls Google Geocoding from the server |
| Localisation | `SetLocaleLanguage` middleware (locale prefix in URL); UI mostly English with an RTL stylesheet |
| Admin | **none.** No role column, no admin routes or policies. The README says "Admin Tools (if enabled)". Any admin/moderation in v2 is **new**. |

## 4. Data model

### 4.1 Migrations (the schema the code used)

- `users` (id, name, email unique, email_verified_at, password, address, phone, gender, birth_date, image, background_image, remember_token, timestamps)
- `posts` (id, user_id → users, name, gender default `male`, age, birth_date, description, lat, lng (strings), type default `missed`, timestamps)
- `post_images` (id, image path, post_id → posts)
- `comments` (id, user_id, post_id, comment varchar)
- `likes` (id, user_id, post_id) — no unique constraint
- `notifications` (id, title, content, notification_url, type, seen int, send_id, receive_id)
- `post_results` (post_id, result_id → posts) — old "related reports" list
- `chats` (sender_id, reciever_id [sic], message, seen)
- `ai_matches` (source_post_id, matched_post_id, confidence, face_detected, status, raw_response)
- `password_resets`, `jobs`, `failed_jobs`; Passport `oauth_*` tables

### 4.2 `gb.sql` (2019 phpMyAdmin dump, older schema)

Differs from the migrations. Extra tables `countries`, `cities`, `regions`
(geo hierarchy with one Egypt / one city / one region row), `histories`
(user_id, info), `suggest_users` (user_id, suggest_id, priority); `chats` uses
`send_id/receive_id` + `message_type`; `posts` has `desc`, `lang` (longitude),
`found` flag, `region_id`, numeric gender; `users` has `job`, `region_id`, `online`.

**Carried into v2:** users, reports (posts), report photos, comments, likes,
messages (with attachments), notifications, matches (ai_matches + post_results
merged into one `matches` table), a free-text `city`/`area` on reports instead of
the 3-table geo hierarchy, the `found`/resolved idea as a report **status**.
**Dropped:** `histories`, `suggest_users` (no code used them), Passport tables,
`password_resets` (replaced), `jobs` (replaced by an outbox).

### 4.3 Value mapping v1 → v2

| v1 | v2 |
| --- | --- |
| `type = missed` | `kind = missing` |
| `type = founded` | `kind = found` |
| `posts.found = 1` (gb.sql) | `status = resolved` |
| `chats.reciever_id` | `messages.recipient_id` |
| `ai_matches.confidence` (0–100) | `matches.score` (0–100, same meaning) |

## 5. The AI part — what it really does

- `ai_service/app/extractor.py` defines an "ArcFace" CNN and **instantiates it with
  random weights; no checkpoint is ever loaded.** Its embeddings are noise, so
  similarity scores between two different photos carry no meaning.
- Face *detection* (OpenCV Haar cascade) works. When no face is found and the
  image is roughly square, the whole image is treated as a face.
- FAISS `IndexFlatIP` stores vectors in a local file; post ids are kept in a JSON list.
- Tests in `ai_service/tests` exercise the API shape, not recognition quality.

**Conclusion:** face matching never worked in v1. v2 keeps the AI pipeline
(detect → embed → cosine search) as a module, makes the embedder a swappable port,
and makes **attribute matching** (kind, gender, age, place, time) the reliable,
tested core. A trained face model is an owner decision (§8).

## 6. Uploads and "presigned URLs"

There is **no presigned-URL code** in v1. `config/filesystems.php` only has
Laravel's default S3 block. Uploads were multipart POSTs to the PHP app, written
to `public/uploads/*` or `front/uploads/*`. The last open issue (`description.md`)
was HTTP 422 errors on those multipart uploads. v2 replaces that path with
presigned PUT/GET against S3-compatible storage, so there is no conflicting
meaning to follow.

## 7. What worked, what did not

| Works (per the 2026-07 reports, not re-run here) | Broken / missing |
| --- | --- |
| `php artisan migrate:fresh --seed`; 13 API feature tests (AUDIT_REPORT.md) | face matching (random weights) |
| Mix build of the Vue 2 bundle (verification_report.md) | realtime needs a Pusher account |
| | two duplicated controller stacks (web + API) |
| | n8n workflows never connected |
| | uploads to local disk; 422 errors on multipart |

## 8. Security and privacy findings (values deliberately not reproduced)

1. **A Google Maps API key is hard-coded** in `routes/web.php` (reverse-geocode route). It is in git history. **Owner: rotate/restrict it.**
2. **`.env.docker` is tracked** in git and holds database/mail credentials. **Owner: rotate them.**
3. `storage/oauth-*.key` exist locally (gitignored, not tracked).
4. `gb.sql` contains a user row with a real-looking e-mail, phone number and password hash.
5. Tracked image folders `front/uploads/*` (≈95 files), `public/front/uploads/*` (88), `public/images/*.jpg`, `front/images/lost-people`, `front/images/friends` may contain **real photos of people/children**. None of them is used by v2 (seed, screenshots, site use generated silhouettes). **Owner: review, and consider purging them from history before the repo is made public.**

## 9. Git

- Default branch `master`; working branch `feature/ai-image` (latest work, 2026-07-28/29).
- Remote branches: `master`, `feature/ai-image`, three dependabot branches.
- 18 commits from 2019 to 2026. v2 work: branch `feature/v2-fastapi-vue`, cut from `feature/ai-image`.
