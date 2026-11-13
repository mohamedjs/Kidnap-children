from app.modules.matching.application.service import MatchingService
from app.modules.matching.infrastructure.face import OpenCvDctFaceAnalyzer
from app.modules.matching.infrastructure.repository import SqlEmbeddingRepository, SqlMatchRepository
from app.modules.reports import reports_service
from app.shared.infrastructure.db import Session
from app.shared.infrastructure.outbox import SqlOutbox
from app.shared.infrastructure.storage import get_storage


def matching_service(session: Session, with_faces: bool = False) -> MatchingService:
    return MatchingService(
        SqlMatchRepository(session), SqlEmbeddingRepository(session), reports_service(session), SqlOutbox(session),
        storage=get_storage() if with_faces else None, analyzer=OpenCvDctFaceAnalyzer() if with_faces else None,
    )
