"""messaging — private 1:1 messages with optional file attachments (presigned).

Public API: router, MessagingService, messaging_service(session), event_handlers
"""

from app.modules.messaging.application.service import MessagingService
from app.modules.messaging.infrastructure.factory import messaging_service
from app.modules.messaging.presentation.router import router

event_handlers: dict[str, list[object]] = {}

__all__ = ["MessagingService", "event_handlers", "messaging_service", "router"]
