from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.db import Base


class ReportRow(Base):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(10), default="open")
    child_name: Mapped[str | None] = mapped_column(String(80))
    gender: Mapped[str | None] = mapped_column(String(10))
    age: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(80))
    area: Mapped[str | None] = mapped_column(String(80))
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    seen_on: Mapped[date | None] = mapped_column(Date)
    contact_phone: Mapped[str | None] = mapped_column(String(30))
    hidden_reason: Mapped[str | None] = mapped_column(String(300))
    status_before_hide: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    photos: Mapped[list["ReportPhotoRow"]] = relationship(
        back_populates="report", cascade="all, delete-orphan", order_by="ReportPhotoRow.position", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_reports_kind_status_created", "kind", "status", "created_at"),
    )


class ReportPhotoRow(Base):
    __tablename__ = "report_photos"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    report_id: Mapped[UUID] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(300), unique=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    face_status: Mapped[str] = mapped_column(String(10), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report: Mapped[ReportRow] = relationship(back_populates="photos")
