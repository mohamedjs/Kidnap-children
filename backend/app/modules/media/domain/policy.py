"""Upload rules: what may be uploaded for which purpose, how big, and when an uploaded
object is accepted. Pure Python, unit-tested in tests/unit/test_media_policy.py."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.shared.domain.errors import Conflict, Forbidden, Invalid

MB = 1024 * 1024
IMAGES = frozenset({"image/jpeg", "image/png", "image/webp"})
EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "application/pdf": "pdf"}


@dataclass(frozen=True)
class Policy:
    content_types: frozenset[str]
    max_bytes: int


POLICIES: dict[str, Policy] = {
    "report_photo": Policy(IMAGES, 8 * MB),
    "avatar": Policy(IMAGES, 5 * MB),
    "cover": Policy(IMAGES, 8 * MB),
    "message_attachment": Policy(IMAGES | {"application/pdf"}, 10 * MB),
}

PENDING, READY, REJECTED = "pending", "ready", "rejected"


def normalize_type(content_type: str) -> str:
    return content_type.split(";")[0].strip().lower()


def policy_for(purpose: str, content_type: str, size: int) -> Policy:
    policy = POLICIES.get(purpose)
    if policy is None:
        raise Invalid(f"Unknown upload purpose '{purpose}'", "upload_purpose")
    ct = normalize_type(content_type)
    if ct not in policy.content_types:
        raise Invalid(f"Content type '{ct}' is not allowed for {purpose}", "upload_type")
    if size <= 0:
        raise Invalid("File is empty", "upload_size")
    if size > policy.max_bytes:
        raise Invalid(f"File is larger than {policy.max_bytes // MB} MB", "upload_size")
    return policy


def object_key(purpose: str, owner_id: UUID, upload_id: UUID, content_type: str) -> str:
    """Server-chosen key under a per-owner prefix; the client never picks a key."""
    return f"{purpose}/{owner_id}/{upload_id}.{EXTENSIONS[normalize_type(content_type)]}"


@dataclass
class Upload:
    id: UUID
    owner_id: UUID
    key: str
    purpose: str
    content_type: str
    declared_size: int
    status: str
    expires_at: datetime
    original_name: str | None = None
    size: int | None = None
    attached: bool = False

    def check_confirmable(self, caller: UUID, now: datetime) -> None:
        if self.owner_id != caller:
            raise Forbidden("This upload belongs to someone else", "upload_owner")
        if self.status == REJECTED:
            raise Conflict("This upload was rejected", "upload_rejected")
        if self.status == PENDING and now > self.expires_at:
            raise Invalid("The upload URL expired; request a new one", "upload_expired")

    def verdict(self, size: int | None, content_type: str | None) -> str | None:
        """None when the stored object is acceptable, otherwise the reason it is rejected."""
        if size is None:
            return "missing"
        policy = POLICIES[self.purpose]
        if size > policy.max_bytes:
            return "too_large"
        if size != self.declared_size:
            return "size_mismatch"
        if normalize_type(content_type or "") != normalize_type(self.content_type):
            return "type_mismatch"
        return None

    def check_attachable(self, caller: UUID, purpose: str) -> None:
        if self.owner_id != caller:
            raise Forbidden("This file belongs to someone else", "upload_owner")
        if self.status != READY:
            raise Invalid("The file upload was not confirmed", "upload_not_ready")
        if self.purpose != purpose:
            raise Invalid(f"This file was uploaded for {self.purpose}, not {purpose}", "upload_purpose")
        if self.attached:
            raise Conflict("This file is already attached", "upload_attached")


class UploadRepository(Protocol):
    def add(self, upload: Upload) -> None: ...

    def get(self, upload_id: UUID) -> Upload | None: ...

    def get_many(self, upload_ids: list[UUID]) -> list[Upload]: ...

    def save(self, upload: Upload) -> None: ...

    def expired_pending(self, now: datetime, limit: int) -> list[Upload]: ...

    def delete(self, upload_id: UUID) -> None: ...

    def delete_by_keys(self, keys: list[str]) -> None: ...
