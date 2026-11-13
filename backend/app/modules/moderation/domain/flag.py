"""Moderation (new in v2 - v1 had no admin). Anyone signed in can flag a report; admins
review flags and hide or restore reports. Enough distinct flags hide a report until review."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.shared.domain.errors import Invalid

REASONS = {"fake", "privacy", "abuse", "duplicate", "other"}
AUTO_HIDE_FLAGS = 3
OPEN, CLOSED = "open", "closed"


def check_reason(reason: str, note: str | None) -> tuple[str, str | None]:
    if reason not in REASONS:
        raise Invalid("Unknown reason", "reason")
    text = (note or "").strip()[:300] or None
    if reason == "other" and not text:
        raise Invalid("Explain the problem", "note")
    return reason, text


def should_auto_hide(open_flaggers: int, already_hidden: bool) -> bool:
    return not already_hidden and open_flaggers >= AUTO_HIDE_FLAGS


@dataclass
class Flag:
    id: UUID
    report_id: UUID
    reporter_id: UUID
    reason: str
    note: str | None
    status: str = OPEN
    created_at: datetime | None = None


class FlagRepository(Protocol):
    def add(self, flag: Flag) -> None: ...

    def has_open(self, report_id: UUID, reporter_id: UUID) -> bool: ...

    def open_count(self, report_id: UUID) -> int: ...

    def queue(self, offset: int, limit: int) -> tuple[list[tuple[UUID, int, list[str]]], int]:
        """(report_id, open flag count, reasons) for reports with open flags."""
        ...

    def close_for_report(self, report_id: UUID) -> int: ...
