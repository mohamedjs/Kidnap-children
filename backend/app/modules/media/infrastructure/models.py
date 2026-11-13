from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.db import Base


class UploadRow(Base):
    __tablename__ = "uploads"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(300), unique=True)
    purpose: Mapped[str] = mapped_column(String(40))
    content_type: Mapped[str] = mapped_column(String(100))
    declared_size: Mapped[int] = mapped_column(BigInteger)
    size: Mapped[int | None] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(20), index=True)
    original_name: Mapped[str | None] = mapped_column(String(200))
    attached: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
