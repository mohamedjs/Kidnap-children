from typing import Any
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.modules.media.application.service import UploadRejected
from app.modules.media.infrastructure.factory import media_service
from app.shared.infrastructure.db import DbSession
from app.shared.presentation.auth import CurrentPrincipal
from app.shared.presentation.http import ok

router = APIRouter(prefix="/api/uploads", tags=["media"])


class UploadRequest(BaseModel):
    purpose: str = Field(examples=["report_photo"])
    content_type: str = Field(examples=["image/jpeg"])
    size: int = Field(gt=0, description="Exact size in bytes of the file that will be PUT")
    filename: str | None = Field(default=None, max_length=200)


@router.post("", status_code=201)
def request_upload(body: UploadRequest, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    """Returns a presigned PUT URL. Upload the bytes there with the given headers, then confirm."""
    t = media_service(session).request_upload(me.user_id, body.purpose, body.content_type, body.size, body.filename)
    return ok(
        {
            "upload_id": str(t.upload_id),
            "key": t.key,
            "method": t.method,
            "url": t.url,
            "headers": t.headers,
            "expires_at": t.expires_at.isoformat(),
            "max_bytes": t.max_bytes,
        }
    )


@router.post("/{upload_id}/confirm")
def confirm_upload(upload_id: UUID, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    try:
        stored, url = media_service(session).confirm(me.user_id, upload_id)
    except UploadRejected:
        session.commit()  # keep the 'rejected' status; the object is already deleted
        raise
    return ok(
        {
            "upload_id": str(stored.upload_id),
            "key": stored.key,
            "content_type": stored.content_type,
            "size": stored.size,
            "url": url,
        }
    )
