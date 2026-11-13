#!/usr/bin/env bash
# Starts the whole dev stack: infra, migrations, bucket, api (:4100), worker, web (:3100).
# Logs go to .data/logs/. Ctrl-C stops api, worker and web (infra keeps running).
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || python3 scripts/gen-dev-env.py
mkdir -p .data/logs
docker compose up -d --wait postgres
docker compose up -d s3
(cd backend && .venv/bin/alembic upgrade head && .venv/bin/python -m scripts.init_storage)

(cd backend && exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 4100 --reload --reload-dir app) > .data/logs/api.log 2>&1 &
API=$!
(cd backend && exec .venv/bin/python -m app.worker) > .data/logs/worker.log 2>&1 &
WORKER=$!
(cd web && exec npx vite --port 3100 --strictPort) > .data/logs/web.log 2>&1 &
WEB=$!
trap 'kill $API $WORKER $WEB 2>/dev/null' EXIT INT TERM
echo "api http://127.0.0.1:4100/api/docs · web http://localhost:3100 · logs in .data/logs/"
wait
