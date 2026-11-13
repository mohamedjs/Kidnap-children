"""Which event notifies whom. Texts are rendered by the frontend from `type` + `data`
(so they follow the reader's language), the link is a frontend route."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID


@dataclass(frozen=True)
class NewNotification:
    user_id: str
    type: str
    link: str
    actor_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Notification:
    id: UUID
    user_id: UUID
    type: str
    link: str
    actor_id: UUID | None
    data: dict[str, Any]
    read_at: datetime | None = None
    created_at: datetime | None = None


def notifications_for(event_type: str, p: dict[str, Any]) -> list[NewNotification]:
    s = lambda k: str(p.get(k) or "")  # noqa: E731
    if event_type == "comment.added" and s("author_id") != s("report_owner_id"):
        return [NewNotification(s("report_owner_id"), "comment", f"/reports/{s('report_id')}", s("author_id"),
                                {"preview": p.get("preview", "")})]
    if event_type == "like.added":
        return [NewNotification(s("report_owner_id"), "like", f"/reports/{s('report_id')}", s("user_id"))]
    if event_type == "message.sent":
        return [NewNotification(s("recipient_id"), "message", f"/messages/{s('sender_id')}", s("sender_id"),
                                {"preview": p.get("preview", "")})]
    if event_type == "match.suggested":
        data = {"score": p.get("score"), "match_id": s("match_id")}
        owners = {s("missing_owner_id"), s("found_owner_id")}
        return [NewNotification(o, "match", "/matches", None, data) for o in sorted(owners) if o]
    if event_type == "match.confirmed":
        by = s("by")
        data = {"match_id": s("match_id")}
        return [NewNotification(o, "match_confirmed", "/matches", by, data)
                for o in sorted({s("missing_owner_id"), s("found_owner_id")}) if o and o != by]
    return []


class NotificationRepository(Protocol):
    def add_many(self, items: list[NewNotification]) -> None: ...

    def for_user(self, user_id: UUID, offset: int, limit: int) -> tuple[list[Notification], int]: ...

    def unread(self, user_id: UUID) -> int: ...

    def mark_read(self, user_id: UUID, notification_id: UUID, when: datetime) -> bool: ...

    def mark_all_read(self, user_id: UUID, when: datetime) -> int: ...
