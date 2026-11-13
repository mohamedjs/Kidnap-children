"""Object storage port. The S3 adapter lives in shared/infrastructure/storage.py."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ObjectInfo:
    size: int
    content_type: str


class ObjectStorage(Protocol):
    def presign_put(self, key: str, content_type: str, ttl_seconds: int) -> str: ...

    def presign_get(self, key: str, ttl_seconds: int, download_name: str | None = None) -> str: ...

    def head(self, key: str) -> ObjectInfo | None: ...

    def delete(self, key: str) -> None: ...

    def read(self, key: str, max_bytes: int) -> bytes:
        """Worker-only: the api never reads file bytes."""
        ...
