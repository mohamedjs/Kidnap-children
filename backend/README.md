# Kidnap-children backend (v2)

FastAPI modular monolith. One codebase, two processes:

| Process | Command | Does |
| --- | --- | --- |
| api | `uvicorn app.main:app --host 127.0.0.1 --port 4100` | REST `/api/*`, presigned URLs |
| worker | `python -m app.worker` | outbox delivery: matching + face analysis, notifications, media cleanup, dev mailer, optional n8n |

```bash
cd backend
uv venv .venv && uv pip install --python .venv/bin/python -e '.[dev]'
.venv/bin/alembic upgrade head          # schema
.venv/bin/python -m scripts.init_storage   # private bucket
.venv/bin/python -m scripts.seed --reset   # demo data (api must be running)
.venv/bin/python -m scripts.smoke          # 19 end-to-end checks (api must be running)
.venv/bin/pytest && .venv/bin/mypy && .venv/bin/ruff check app
```

Config comes from the repository root `.env` (see `.env.example`). Layout and rules: [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).
