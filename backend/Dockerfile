# One image, two processes:
#   api:     uvicorn app.main:app            (default CMD)
#   worker:  python -m app.worker
#   migrate: alembic upgrade head && python -m scripts.init_storage
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Pinned dependencies first (cached layer), then the code.
COPY requirements.lock ./
RUN pip install -r requirements.lock

COPY pyproject.toml alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts
RUN pip install --no-deps . \
 && useradd --system --uid 10001 --home /app kc \
 && chown -R kc /app

USER kc
EXPOSE 4100

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
  CMD ["python", "-m", "scripts.healthcheck", "api"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4100", "--proxy-headers", "--forwarded-allow-ips", "*", "--workers", "2"]
