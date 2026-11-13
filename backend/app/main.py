"""The api process: `uvicorn app.main:app --port 4100`."""

import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.registry import MODULES, load_models
from app.shared.infrastructure.config import get_settings
from app.shared.infrastructure.db import ping
from app.shared.infrastructure.storage import get_storage
from app.shared.presentation.http import install_error_handlers, ok

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app() -> FastAPI:
    settings = get_settings()
    load_models()
    app = FastAPI(title="Kidnap-children API", version="2.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)
    for module in MODULES:
        app.include_router(module.router)

    @app.get("/health")
    def health() -> dict[str, Any]:
        return ok({"status": "ok", "service": "api"})

    @app.get("/health/ready")
    def ready() -> dict[str, Any]:
        ping()
        get_storage().ping()
        return ok({"status": "ready"})

    return app


app = create_app()
