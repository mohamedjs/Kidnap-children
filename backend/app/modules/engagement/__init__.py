"""engagement — comments and likes on reports.

Public API: router, EngagementService, engagement_service(session), event_handlers
"""

from app.modules.engagement.application.service import EngagementService
from app.modules.engagement.infrastructure.factory import engagement_service
from app.modules.engagement.presentation.router import router

event_handlers: dict[str, list[object]] = {}

__all__ = ["EngagementService", "engagement_service", "event_handlers", "router"]
