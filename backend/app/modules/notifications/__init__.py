"""notifications — in-app notifications created from domain events by the worker.

Public API: router, NotificationsService, notifications_service(session), event_handlers
"""

from collections.abc import Callable
from typing import Any

from app.modules.notifications.application.service import NotificationsService
from app.modules.notifications.infrastructure.factory import notifications_service
from app.modules.notifications.presentation.router import router
from app.shared.domain.events import COMMENT_ADDED, LIKE_ADDED, MATCH_CONFIRMED, MATCH_SUGGESTED, MESSAGE_SENT
from app.shared.infrastructure.db import Session


def _handler(event_type: str) -> Callable[[Session, dict[str, Any]], None]:
    def handle(session: Session, payload: dict[str, Any]) -> None:
        notifications_service(session).on_event(event_type, payload)

    return handle


event_handlers = {t: [_handler(t)] for t in (COMMENT_ADDED, LIKE_ADDED, MESSAGE_SENT, MATCH_SUGGESTED,
                                              MATCH_CONFIRMED)}

__all__ = ["NotificationsService", "event_handlers", "notifications_service", "router"]
