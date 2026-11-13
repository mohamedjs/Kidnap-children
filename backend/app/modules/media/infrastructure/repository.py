from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.media.domain.policy import PENDING, Upload, UploadRepository
from app.modules.media.infrastructure.models import UploadRow


def _to_domain(r: UploadRow) -> Upload:
    return Upload(
        r.id, r.owner_id, r.key, r.purpose, r.content_type, r.declared_size, r.status,
        r.expires_at, r.original_name, r.size, r.attached,
    )


class SqlUploadRepository(UploadRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def add(self, upload: Upload) -> None:
        self.s.add(
            UploadRow(
                id=upload.id, owner_id=upload.owner_id, key=upload.key, purpose=upload.purpose,
                content_type=upload.content_type, declared_size=upload.declared_size, size=upload.size,
                status=upload.status, original_name=upload.original_name, attached=upload.attached,
                expires_at=upload.expires_at,
            )
        )
        self.s.flush()

    def get(self, upload_id: UUID) -> Upload | None:
        row = self.s.get(UploadRow, upload_id)
        return _to_domain(row) if row else None

    def get_many(self, upload_ids: list[UUID]) -> list[Upload]:
        rows = self.s.scalars(select(UploadRow).where(UploadRow.id.in_(upload_ids)).with_for_update())
        return [_to_domain(r) for r in rows]

    def save(self, upload: Upload) -> None:
        row = self.s.get(UploadRow, upload.id)
        if row is None:
            return
        row.status, row.size, row.attached = upload.status, upload.size, upload.attached
        self.s.flush()

    def expired_pending(self, now: datetime, limit: int) -> list[Upload]:
        rows = self.s.scalars(
            select(UploadRow).where(UploadRow.status == PENDING, UploadRow.expires_at < now).limit(limit)
        )
        return [_to_domain(r) for r in rows]

    def delete(self, upload_id: UUID) -> None:
        self.s.execute(delete(UploadRow).where(UploadRow.id == upload_id))

    def delete_by_keys(self, keys: list[str]) -> None:
        if keys:
            self.s.execute(delete(UploadRow).where(UploadRow.key.in_(keys)))
