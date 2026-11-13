"""Presigned upload flow and the facade other modules use to attach and read files.

1. request_upload: validate type/size, pick the key, store a pending row, return a presigned PUT.
2. The browser PUTs the bytes straight to the bucket.
3. confirm: HEAD the object; accept it only if size and type match the declaration,
   otherwise delete it and reject. The api never sees the bytes.
4. Other modules `claim` ready uploads and mint short-lived GET URLs on every read.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.modules.media.domain.policy import (
    PENDING,
    READY,
    REJECTED,
    Upload,
    UploadRepository,
    normalize_type,
    object_key,
    policy_for,
)
from app.shared.application.storage import ObjectStorage
from app.shared.domain.errors import Conflict, Invalid, NotFound


class UploadRejected(Invalid):
    """The stored object failed validation and was deleted."""


@dataclass(frozen=True)
class UploadTicket:
    upload_id: UUID
    key: str
    method: str
    url: str
    headers: dict[str, str]
    expires_at: datetime
    max_bytes: int


@dataclass(frozen=True)
class StoredFile:
    upload_id: UUID
    key: str
    content_type: str
    size: int
    name: str | None


class MediaService:
    def __init__(self, repo: UploadRepository, storage: ObjectStorage, put_ttl: int, get_ttl: int) -> None:
        self.repo = repo
        self.storage = storage
        self.put_ttl = put_ttl
        self.get_ttl = get_ttl

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    def request_upload(
        self, owner: UUID, purpose: str, content_type: str, size: int, name: str | None
    ) -> UploadTicket:
        policy = policy_for(purpose, content_type, size)
        ct = normalize_type(content_type)
        upload_id = uuid4()
        key = object_key(purpose, owner, upload_id, ct)
        expires = self._now() + timedelta(seconds=self.put_ttl)
        self.repo.add(Upload(upload_id, owner, key, purpose, ct, size, PENDING, expires, (name or "")[:200] or None))
        url = self.storage.presign_put(key, ct, self.put_ttl)
        return UploadTicket(upload_id, key, "PUT", url, {"Content-Type": ct}, expires, policy.max_bytes)

    def confirm(self, owner: UUID, upload_id: UUID) -> tuple[StoredFile, str]:
        upload = self.repo.get(upload_id)
        if upload is None:
            raise NotFound("Upload not found")
        upload.check_confirmable(owner, self._now())
        if upload.status != READY:
            info = self.storage.head(upload.key)
            reason = upload.verdict(info.size if info else None, info.content_type if info else None)
            if reason == "missing":
                raise Conflict("The file has not been uploaded yet", "upload_missing")
            if reason:
                self.storage.delete(upload.key)
                upload.status = REJECTED
                self.repo.save(upload)
                raise UploadRejected(f"Uploaded file rejected: {reason}", f"upload_{reason}")
            assert info is not None
            upload.status, upload.size = READY, info.size
            self.repo.save(upload)
        return self._stored(upload), self.url(upload.key)

    # ── facade used by other modules ──
    def claim(self, owner: UUID, upload_ids: list[UUID], purpose: str) -> list[StoredFile]:
        """Mark confirmed uploads as attached to a record owned by `owner`."""
        if not upload_ids:
            return []
        if len(set(upload_ids)) != len(upload_ids):
            raise Invalid("The same file was sent twice")
        found = {u.id: u for u in self.repo.get_many(upload_ids)}
        out: list[StoredFile] = []
        for uid in upload_ids:
            upload = found.get(uid)
            if upload is None:
                raise NotFound(f"Upload {uid} not found")
            upload.check_attachable(owner, purpose)
            upload.attached = True
            self.repo.save(upload)
            out.append(self._stored(upload))
        return out

    def url(self, key: str) -> str:
        return self.storage.presign_get(key, self.get_ttl)

    def download_url(self, key: str, name: str | None) -> str:
        return self.storage.presign_get(key, self.get_ttl, name)

    def discard(self, keys: list[str]) -> None:
        """Delete stored objects (record deleted, photo removed)."""
        for key in keys:
            self.storage.delete(key)
        self.repo.delete_by_keys(keys)

    def sweep_expired(self, limit: int = 100) -> int:
        """Worker job: drop pending uploads whose PUT URL expired an hour ago."""
        stale = self.repo.expired_pending(self._now() - timedelta(hours=1), limit)
        for upload in stale:
            self.storage.delete(upload.key)
            self.repo.delete(upload.id)
        return len(stale)

    @staticmethod
    def _stored(u: Upload) -> StoredFile:
        return StoredFile(u.id, u.key, u.content_type, u.size or u.declared_size, u.original_name)
