"""media — presigned uploads to S3-compatible storage and short-lived download URLs.

Public API (the only names other modules may import):
    router, MediaService, StoredFile, media_service(session), event_handlers, periodic_tasks
"""

from typing import Any

from app.modules.media.application.service import MediaService, StoredFile
from app.modules.media.infrastructure.factory import media_service
from app.modules.media.presentation.router import router
from app.shared.domain.events import REPORT_DELETED, UPLOAD_ORPHANED
from app.shared.infrastructure.db import Session


def _discard_keys(session: Session, payload: dict[str, Any]) -> None:
    keys = [str(k) for k in payload.get("keys", [])]
    if keys:
        media_service(session).discard(keys)


def _sweep(session: Session) -> None:
    media_service(session).sweep_expired()


event_handlers = {REPORT_DELETED: [_discard_keys], UPLOAD_ORPHANED: [_discard_keys]}
periodic_tasks = [(_sweep, 300.0)]

__all__ = ["MediaService", "StoredFile", "event_handlers", "media_service", "periodic_tasks", "router"]
