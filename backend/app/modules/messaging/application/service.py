from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.modules.identity import IdentityService
from app.modules.media import MediaService
from app.modules.messaging.domain.message import (
    Attachment,
    Conversation,
    Message,
    MessageRepository,
    check_message,
)
from app.shared.domain.errors import NotFound
from app.shared.domain.events import MESSAGE_SENT, DomainEvent, EventSink
from app.shared.domain.principal import Principal


class MessagingService:
    def __init__(self, repo: MessageRepository, identity: IdentityService, media: MediaService,
                 events: EventSink) -> None:
        self.repo, self.identity, self.media, self.events = repo, identity, media, events

    def send(self, who: Principal, recipient_id: UUID, body: str | None, attachment_upload_id: UUID | None) -> Message:
        text = check_message(who.user_id, recipient_id, body, attachment_upload_id is not None)
        self.identity.public(recipient_id)  # 404 when missing / blocked
        attachment = None
        if attachment_upload_id:
            f = self.media.claim(who.user_id, [attachment_upload_id], "message_attachment")[0]
            attachment = Attachment(f.key, f.content_type, f.name, f.size)
        m = Message(uuid4(), who.user_id, recipient_id, text, attachment)
        self.repo.add(m)
        self.events.add(DomainEvent(MESSAGE_SENT, {
            "message_id": str(m.id), "sender_id": str(who.user_id), "recipient_id": str(recipient_id),
            "preview": (text or "📎")[:60],
        }))
        return m

    def thread(self, who: Principal, other_id: UUID, before: datetime | None) -> list[Message]:
        self.identity.public(other_id)
        self.repo.mark_thread_read(who.user_id, other_id, datetime.now(UTC))  # v1: opening marks seen
        return self.repo.thread(who.user_id, other_id, before, 50)

    def mark_read(self, who: Principal, message_id: UUID) -> None:
        if not self.repo.mark_read(message_id, who.user_id, datetime.now(UTC)):
            raise NotFound("Message not found")

    def conversations(self, who: Principal) -> list[Conversation]:
        return self.repo.conversations(who.user_id, 50)

    def unread(self, who: Principal) -> int:
        return self.repo.unread_total(who.user_id)

    def attachment_url(self, m: Message) -> str | None:
        if m.attachment is None:
            return None
        if m.attachment.content_type.startswith("image/"):
            return self.media.url(m.attachment.key)
        return self.media.download_url(m.attachment.key, m.attachment.name)
