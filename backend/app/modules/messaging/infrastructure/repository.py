from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, case, func, or_, select, update
from sqlalchemy.orm import Session

from app.modules.messaging.domain.message import Attachment, Conversation, Message, MessageRepository
from app.modules.messaging.infrastructure.models import MessageRow


def _to_domain(r: MessageRow) -> Message:
    att = None
    if r.attachment_key:
        att = Attachment(r.attachment_key, r.attachment_type or "", r.attachment_name, r.attachment_size or 0)
    return Message(r.id, r.sender_id, r.recipient_id, r.body, att, r.read_at, r.created_at)


def _pair(a: UUID, b: UUID):  # type: ignore[no-untyped-def]
    return or_(and_(MessageRow.sender_id == a, MessageRow.recipient_id == b),
               and_(MessageRow.sender_id == b, MessageRow.recipient_id == a))


class SqlMessageRepository(MessageRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def add(self, m: Message) -> None:
        a = m.attachment
        row = MessageRow(
            id=m.id, sender_id=m.sender_id, recipient_id=m.recipient_id, body=m.body,
            attachment_key=a.key if a else None, attachment_type=a.content_type if a else None,
            attachment_name=a.name if a else None, attachment_size=a.size if a else None,
        )
        self.s.add(row)
        self.s.flush()
        self.s.refresh(row)
        m.created_at = row.created_at

    def get(self, message_id: UUID) -> Message | None:
        r = self.s.get(MessageRow, message_id)
        return _to_domain(r) if r else None

    def thread(self, a: UUID, b: UUID, before: datetime | None, limit: int) -> list[Message]:
        stmt = select(MessageRow).where(_pair(a, b))
        if before:
            stmt = stmt.where(MessageRow.created_at < before)
        rows = list(self.s.scalars(stmt.order_by(MessageRow.created_at.desc()).limit(limit)))
        return [_to_domain(r) for r in reversed(rows)]

    def mark_thread_read(self, reader: UUID, other: UUID, when: datetime) -> int:
        res = self.s.execute(update(MessageRow).where(MessageRow.recipient_id == reader, MessageRow.sender_id == other,
                                                      MessageRow.read_at.is_(None)).values(read_at=when))
        return int(getattr(res, "rowcount", 0) or 0)

    def mark_read(self, message_id: UUID, reader: UUID, when: datetime) -> bool:
        r = self.s.get(MessageRow, message_id)
        if r is None or r.recipient_id != reader:
            return False
        if r.read_at is None:
            r.read_at = when
        return True

    def conversations(self, user_id: UUID, limit: int) -> list[Conversation]:
        other = case((MessageRow.sender_id == user_id, MessageRow.recipient_id), else_=MessageRow.sender_id)
        latest = self.s.execute(
            select(other.label("other_id"), func.max(MessageRow.created_at).label("last_at"))
            .where(or_(MessageRow.sender_id == user_id, MessageRow.recipient_id == user_id))
            .group_by(other).order_by(func.max(MessageRow.created_at).desc()).limit(limit)
        ).all()
        unread: dict[UUID, int] = {sid: int(n) for sid, n in self.s.execute(
            select(MessageRow.sender_id, func.count()).where(MessageRow.recipient_id == user_id,
                                                             MessageRow.read_at.is_(None))
            .group_by(MessageRow.sender_id)
        ).all()}
        out = []
        for other_id, _ in latest:
            last = self.s.scalar(select(MessageRow).where(_pair(user_id, other_id))
                                 .order_by(MessageRow.created_at.desc()).limit(1))
            if last:
                out.append(Conversation(other_id, _to_domain(last), int(unread.get(other_id, 0))))
        return out

    def unread_total(self, user_id: UUID) -> int:
        return self.s.scalar(select(func.count()).select_from(MessageRow).where(
            MessageRow.recipient_id == user_id, MessageRow.read_at.is_(None))) or 0
