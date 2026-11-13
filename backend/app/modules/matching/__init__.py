"""matching — pairs missing and found reports (attribute rules + face embeddings) and lets
the two reporters confirm or dismiss a suggestion. Heavy work runs in the worker.

Public API: router, MatchingService, matching_service(session), event_handlers
"""

from typing import Any
from uuid import UUID

from app.modules.matching.application.service import MatchingService
from app.modules.matching.infrastructure.factory import matching_service
from app.modules.matching.presentation.router import router
from app.shared.domain.events import (
    REPORT_DELETED,
    REPORT_PUBLISHED,
    REPORT_REMATCH_REQUESTED,
    REPORT_UPDATED,
)
from app.shared.infrastructure.db import Session


def _process(session: Session, payload: dict[str, Any]) -> None:
    matching_service(session, with_faces=True).process_report(UUID(str(payload["report_id"])))


def _rematch(session: Session, payload: dict[str, Any]) -> None:
    matching_service(session, with_faces=True).process_report(UUID(str(payload["report_id"])), force_faces=True)


def _forget(session: Session, payload: dict[str, Any]) -> None:
    matching_service(session).forget_report(UUID(str(payload["report_id"])))


event_handlers = {
    REPORT_PUBLISHED: [_process],
    REPORT_UPDATED: [_process],
    REPORT_REMATCH_REQUESTED: [_rematch],
    REPORT_DELETED: [_forget],
}

__all__ = ["MatchingService", "event_handlers", "matching_service", "router"]
