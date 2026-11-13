# أنا فين؟ — Kidnap-children v2

A community platform for reports of missing children and of children who were found.
Families and finders post reports with photos; the platform matches missing reports with
found reports and alerts both sides; the community comments, supports and messages.

v2 rebuild (2026-11): FastAPI modular monolith + PostgreSQL + S3 presigned uploads +
Vue 3. The original Laravel app is kept in [`legacy/v1-laravel/`](legacy/v1-laravel/) and at tag `v1-laravel`.

## Run locally

Requirements: Docker, Python 3.12 with [uv](https://github.com/astral-sh/uv), Node 22.

```bash
python3 scripts/gen-dev-env.py     # writes .env with random dev secrets (gitignored)
docker compose up -d               # postgres 127.0.0.1:5435, S3 127.0.0.1:9010
(cd backend && uv venv .venv && uv pip install --python .venv/bin/python -e '.[dev]')
(cd web && npm install)
scripts/dev.sh                     # migrations, bucket, api :4100, worker, web :3100
(cd backend && .venv/bin/python -m scripts.seed --reset)   # demo data (generated)
```

Open http://localhost:3100. Demo accounts (`mona@demo.local`, `karim@demo.local`, …,
admin `admin@demo.local`) use `ADMIN_SEED_PASSWORD` from your `.env`.

| Service | Port |
| --- | --- |
| web (Vite) | 3100 |
| api (FastAPI, docs at `/api/docs`) | 4100 |
| PostgreSQL | 5435 |
| S3 (SeaweedFS gateway) | 9010 |
| landing site preview (`python3 -m http.server 4190 -d site`) | 4190 |

Docs: [AGENTS.md](AGENTS.md) · [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/INVENTORY.md](docs/INVENTORY.md)

## Deploy (Docker, one server)

Needs a server with Docker, two DNS names pointing at it (the app and the file host, e.g.
`app.example.org` and `files.example.org`) and ports 80/443 open.

```bash
git clone git@github.com:mohamedjs/Kidnap-children.git && cd Kidnap-children
python3 scripts/gen-prod-env.py app.example.org files.example.org   # writes .env.production with random secrets
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

| Service | Image | Role |
| --- | --- | --- |
| `caddy` | `caddy:2.10-alpine` | automatic HTTPS; `/api`, `/health` → api, everything else → web; file host → s3 |
| `web` | built from `web/Dockerfile` | the Vue build served by Caddy (SPA fallback) |
| `api` | built from `backend/Dockerfile` | FastAPI (2 uvicorn workers) |
| `worker` | same image | outbox delivery, matching, face analysis, cleanup |
| `migrate` | same image | one-shot `alembic upgrade head` + bucket creation |
| `postgres` | `postgres:17-alpine` | database (volume `pgdata`) |
| `s3` | `chrislusf/seaweedfs:4.50` | bundled private S3 store (profile `bundled-s3`, volume `s3data`) |

Every service has a healthcheck; `api` and `worker` start only after `migrate` succeeds.
Every variable is documented in [`.env.production.example`](.env.production.example).

- **External bucket instead** (AWS S3, R2, Wasabi, MinIO): set `COMPOSE_PROFILES=` (empty), point `S3_ENDPOINT` / `S3_PUBLIC_ENDPOINT` at the provider, keep the bucket private and allow `PUT, GET, HEAD` from `PUBLIC_WEB_URL` in its CORS.
- **Update:** `git pull && docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build`; migrations run automatically.
- **Backups:** `docker compose -f docker-compose.prod.yml --env-file .env.production exec postgres pg_dump -U kidnap kidnap > backup.sql`, plus the `s3data` volume (or the external bucket).
- **Still to configure:** a mail provider for password-reset mails (today the worker logs the link), and optionally `N8N_WEBHOOK_URL` and a new, restricted `GOOGLE_MAPS_API_KEY`.
