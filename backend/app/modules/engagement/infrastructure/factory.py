from app.modules.engagement.application.service import EngagementService
from app.modules.engagement.infrastructure.repository import SqlCommentRepository, SqlLikeRepository
from app.modules.reports import reports_service
from app.shared.infrastructure.db import Session
from app.shared.infrastructure.outbox import SqlOutbox


def engagement_service(session: Session) -> EngagementService:
    return EngagementService(SqlCommentRepository(session), SqlLikeRepository(session), reports_service(session),
                             SqlOutbox(session))
