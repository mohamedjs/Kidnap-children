"""Domain events. Use cases record them; they are written to the outbox in the same
transaction and delivered to other modules by the worker."""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class DomainEvent:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventSink(Protocol):
    def add(self, event: DomainEvent) -> None: ...


# Event names (the contract between modules).
REPORT_PUBLISHED = "report.published"
REPORT_UPDATED = "report.updated"
REPORT_RESOLVED = "report.resolved"
REPORT_DELETED = "report.deleted"
REPORT_REMATCH_REQUESTED = "report.rematch_requested"
MATCH_SUGGESTED = "match.suggested"
MATCH_CONFIRMED = "match.confirmed"
COMMENT_ADDED = "comment.added"
LIKE_ADDED = "like.added"
MESSAGE_SENT = "message.sent"
PASSWORD_RESET_REQUESTED = "identity.password_reset_requested"
UPLOAD_ORPHANED = "media.upload_orphaned"
