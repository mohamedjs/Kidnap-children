from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.shared.domain.errors import Invalid
from app.shared.domain.principal import Principal


def clean_comment(body: str) -> str:
    text = body.strip()
    if not text:
        raise Invalid("Write a comment first", "comment")
    if len(text) > 1000:
        raise Invalid("Comments are limited to 1000 characters", "comment")
    return text


@dataclass
class Comment:
    id: UUID
    report_id: UUID
    author_id: UUID
    body: str
    created_at: datetime | None = None

    def can_delete(self, who: Principal | None, report_owner_id: UUID) -> bool:
        """v1 CommentPolicy: the author or the report owner (v2 adds admins)."""
        return who is not None and (who.user_id in (self.author_id, report_owner_id) or who.is_admin)


@dataclass(frozen=True)
class Counts:
    comments: int = 0
    likes: int = 0
    liked: bool = False


class CommentRepository(Protocol):
    def add(self, c: Comment) -> None: ...

    def get(self, comment_id: UUID) -> Comment | None: ...

    def delete(self, comment_id: UUID) -> None: ...

    def for_report(self, report_id: UUID, offset: int, limit: int) -> tuple[list[Comment], int]: ...

    def counts(self, report_ids: list[UUID]) -> dict[UUID, int]: ...


class LikeRepository(Protocol):
    def exists(self, report_id: UUID, user_id: UUID) -> bool: ...

    def add(self, report_id: UUID, user_id: UUID) -> None: ...

    def remove(self, report_id: UUID, user_id: UUID) -> None: ...

    def users(self, report_id: UUID, limit: int) -> list[UUID]: ...

    def counts(self, report_ids: list[UUID]) -> dict[UUID, int]: ...

    def liked_by(self, report_ids: list[UUID], user_id: UUID) -> set[UUID]: ...
