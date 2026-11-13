from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.db import Base


class MatchRow(Base):
    """v1 `ai_matches` + `post_results` in one table."""

    __tablename__ = "matches"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    missing_report_id: Mapped[UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    found_report_id: Mapped[UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    missing_owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    found_owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Float)
    attribute_score: Mapped[float] = mapped_column(Float)
    face_score: Mapped[float | None] = mapped_column(Float)
    reasons: Mapped[list[str]] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(12), default="suggested")
    decided_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("missing_report_id", "found_report_id", name="uq_matches_pair"),)


class FaceEmbeddingRow(Base):
    __tablename__ = "face_embeddings"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    report_id: Mapped[UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    photo_id: Mapped[UUID] = mapped_column(ForeignKey("report_photos.id", ondelete="CASCADE"), index=True)
    vector: Mapped[list[float]] = mapped_column(ARRAY(Float))
    model: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
