"""moderation — flags on reports, admin review queue, hide / restore (new in v2).

Public API: router, ModerationService, moderation_service(session), event_handlers
"""

from app.modules.moderation.application.service import ModerationService
from app.modules.moderation.infrastructure.factory import moderation_service
from app.modules.moderation.presentation.router import router

event_handlers: dict[str, list[object]] = {}

__all__ = ["ModerationService", "event_handlers", "moderation_service", "router"]
