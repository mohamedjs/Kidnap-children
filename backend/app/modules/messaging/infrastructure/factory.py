from app.modules.identity import identity_service
from app.modules.media import media_service
from app.modules.messaging.application.service import MessagingService
from app.modules.messaging.infrastructure.repository import SqlMessageRepository
from app.shared.infrastructure.db import Session
from app.shared.infrastructure.outbox import SqlOutbox


def messaging_service(session: Session) -> MessagingService:
    return MessagingService(SqlMessageRepository(session), identity_service(session), media_service(session),
                            SqlOutbox(session))
