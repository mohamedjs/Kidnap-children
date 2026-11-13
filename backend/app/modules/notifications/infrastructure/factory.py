from app.modules.notifications.application.service import NotificationsService
from app.modules.notifications.infrastructure.repository import SqlNotificationRepository
from app.shared.infrastructure.db import Session


def notifications_service(session: Session) -> NotificationsService:
    return NotificationsService(SqlNotificationRepository(session))
