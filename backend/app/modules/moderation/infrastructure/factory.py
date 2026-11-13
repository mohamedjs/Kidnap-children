from app.modules.moderation.application.service import ModerationService
from app.modules.moderation.infrastructure.repository import SqlFlagRepository
from app.modules.reports import reports_service
from app.shared.infrastructure.db import Session


def moderation_service(session: Session) -> ModerationService:
    return ModerationService(SqlFlagRepository(session), reports_service(session))
