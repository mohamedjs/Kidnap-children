from app.modules.media.application.service import MediaService
from app.modules.media.infrastructure.repository import SqlUploadRepository
from app.shared.infrastructure.config import get_settings
from app.shared.infrastructure.db import Session
from app.shared.infrastructure.storage import get_storage


def media_service(session: Session) -> MediaService:
    s = get_settings()
    return MediaService(SqlUploadRepository(session), get_storage(), s.upload_url_ttl_seconds, s.download_url_ttl_seconds)
