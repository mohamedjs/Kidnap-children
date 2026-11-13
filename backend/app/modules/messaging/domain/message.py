from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.shared.domain.errors import Invalid


@dataclass
class Attachment:
    key: str
    content_type: str
    name: str | None
    size: int


@dataclass
class Message:
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    body: str | None
    attachment: Attachment | None = None
    read_at: datetime | None = None
    created_at: datetime | None = None


def check_message(sender: UUID, recipient: UUID, body: str | None, has_attachment: bool) -> str | None:
    """v1 rules: no messages to yourself; v2: a text or an attachment is required."""
    if sender == recipient:
        raise Invalid("You cannot send a message to yourself", "recipient")
    text = (body or "").strip() or None
    if text is None and not has_attachment:
        raise Invalid("Write a message or attach a file", "body")
    if text and len(text) > 5000:
        raise Invalid("Messages are limited to 5000 characters", "body")
    return text


@dataclass(frozen=True)
class Conversation:
    other_id: UUID
    last: Message
    unread: int


class MessageRepository(Protocol):
    def add(self, m: Message) -> None: ...

    def get(self, message_id: UUID) -> Message | None: ...

    def thread(self, a: UUID, b: UUID, before: datetime | None, limit: int) -> list[Message]: ...

    def mark_thread_read(self, reader: UUID, other: UUID, when: datetime) -> int: ...

    def mark_read(self, message_id: UUID, reader: UUID, when: datetime) -> bool: ...

    def conversations(self, user_id: UUID, limit: int) -> list[Conversation]: ...

    def unread_total(self, user_id: UUID) -> int: ...
