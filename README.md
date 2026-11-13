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

## Production checklist

- An S3-compatible bucket (private, no public policy), CORS allowing `PUT, GET` from the web origin; set `S3_ENDPOINT` (empty for AWS), `S3_PUBLIC_ENDPOINT`, `S3_REGION`, `S3_BUCKET`, keys.
- Managed PostgreSQL; `alembic upgrade head`.
- A long random `JWT_SECRET`; HTTPS in front of api and web.
- A real mail provider for password-reset mails (dev only logs the link in the worker log).
- Optional: `N8N_WEBHOOK_URL` (+ `N8N_WEBHOOK_SECRET`), `GOOGLE_MAPS_API_KEY` (new, restricted key).
