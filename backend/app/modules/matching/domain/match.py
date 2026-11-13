from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.shared.domain.errors import Forbidden, Invalid

SUGGESTED, CONFIRMED, DISMISSED = "suggested", "confirmed", "dismissed"


@dataclass
class Match:
    id: UUID
    missing_report_id: UUID
    found_report_id: UUID
    missing_owner_id: UUID
    found_owner_id: UUID
    score: float
    attribute_score: float
    face_score: float | None
    reasons: list[str]
    status: str = SUGGESTED
    decided_by: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def involves(self, user_id: UUID) -> bool:
        return user_id in (self.missing_owner_id, self.found_owner_id)

    def decide(self, user_id: UUID, is_admin: bool, confirm: bool) -> None:
        if not (self.involves(user_id) or is_admin):
            raise Forbidden("Only the two reporters can decide on this match")
        if self.status != SUGGESTED:
            raise Invalid("This match was already decided", "match_status")
        self.status = CONFIRMED if confirm else DISMISSED
        self.decided_by = user_id

    def refresh(self, score: float, attribute_score: float, face_score: float | None, reasons: list[str]) -> None:
        """Re-scoring never revives a dismissed match or changes a decided one's status."""
        self.score, self.attribute_score, self.face_score, self.reasons = score, attribute_score, face_score, reasons


@dataclass(frozen=True)
class Embedding:
    photo_id: UUID
    report_id: UUID
    vector: list[float]
    model: str


class MatchRepository(Protocol):
    def find(self, missing_id: UUID, found_id: UUID) -> Match | None: ...

    def get(self, match_id: UUID) -> Match | None: ...

    def add(self, match: Match) -> None: ...

    def save(self, match: Match) -> None: ...

    def for_user(self, user_id: UUID, status: str | None) -> list[Match]: ...

    def for_report(self, report_id: UUID) -> list[Match]: ...

    def delete_for_report(self, report_id: UUID) -> None: ...


class EmbeddingRepository(Protocol):
    def for_reports(self, report_ids: list[UUID]) -> dict[UUID, list[list[float]]]: ...

    def replace_for_photo(self, emb: list[Embedding], photo_id: UUID) -> None: ...

    def delete_for_report(self, report_id: UUID) -> None: ...


class FaceAnalyzer(Protocol):
    """Detects faces in image bytes and returns one embedding per face ([] when none)."""

    model: str

    def embed(self, image: bytes) -> list[list[float]]: ...
