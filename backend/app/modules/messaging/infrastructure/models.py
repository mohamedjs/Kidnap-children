from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.db import Base


class MessageRow(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    recipient_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str | None] = mapped_column(Text)
    attachment_key: Mapped[str | None] = mapped_column(String(300))
    attachment_type: Mapped[str | None] = mapped_column(String(100))
    attachment_name: Mapped[str | None] = mapped_column(String(200))
    attachment_size: Mapped[int | None] = mapped_column(BigInteger)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_messages_pair_created", "sender_id", "recipient_id", "created_at"),
        Index("ix_messages_recipient_unread", "recipient_id", "read_at"),
    )
