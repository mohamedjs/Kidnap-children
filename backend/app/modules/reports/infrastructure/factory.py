from app.modules.media import media_service
from app.modules.reports.application.service import ReportsService
from app.modules.reports.infrastructure.repository import SqlReportRepository
from app.shared.infrastructure.db import Session
from app.shared.infrastructure.outbox import SqlOutbox


def reports_service(session: Session) -> ReportsService:
    return ReportsService(SqlReportRepository(session), media_service(session), SqlOutbox(session))
