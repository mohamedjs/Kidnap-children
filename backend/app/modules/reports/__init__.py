"""reports — missing / found child reports, their photos, status lifecycle and search.

Public API: router, Report, Photo, ReportsService, reports_service(session), reports_out(...),
            constants MISSING, FOUND, OPEN, FACE_* (photo face-analysis states)
"""

from app.modules.reports.application.service import ReportsService
from app.modules.reports.domain.report import (
    FACE_FAILED,
    FACE_FOUND,
    FACE_NONE,
    FACE_PENDING,
    FOUND,
    MISSING,
    OPEN,
    Photo,
    Report,
)
from app.modules.reports.infrastructure.factory import reports_service
from app.modules.reports.presentation.router import reports_out, router

event_handlers: dict[str, list[object]] = {}

__all__ = [
    "FACE_FAILED", "FACE_FOUND", "FACE_NONE", "FACE_PENDING", "FOUND", "MISSING", "OPEN", "Photo", "Report",
    "ReportsService", "event_handlers", "reports_out", "reports_service", "router",
]
