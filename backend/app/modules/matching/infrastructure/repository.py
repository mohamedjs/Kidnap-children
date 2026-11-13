from collections import defaultdict
from uuid import UUID, uuid4

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.modules.matching.domain.match import Embedding, EmbeddingRepository, Match, MatchRepository
from app.modules.matching.infrastructure.models import FaceEmbeddingRow, MatchRow

_FIELDS = ("missing_report_id", "found_report_id", "missing_owner_id", "found_owner_id", "score",
           "attribute_score", "face_score", "reasons", "status", "decided_by")


def _to_domain(r: MatchRow) -> Match:
    return Match(
        id=r.id, missing_report_id=r.missing_report_id, found_report_id=r.found_report_id,
        missing_owner_id=r.missing_owner_id, found_owner_id=r.found_owner_id, score=r.score,
        attribute_score=r.attribute_score, face_score=r.face_score, reasons=list(r.reasons or []),
        status=r.status, decided_by=r.decided_by, created_at=r.created_at, updated_at=r.updated_at,
    )


class SqlMatchRepository(MatchRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def find(self, missing_id: UUID, found_id: UUID) -> Match | None:
        r = self.s.scalar(select(MatchRow).where(MatchRow.missing_report_id == missing_id,
                                                 MatchRow.found_report_id == found_id))
        return _to_domain(r) if r else None

    def get(self, match_id: UUID) -> Match | None:
        r = self.s.get(MatchRow, match_id)
        return _to_domain(r) if r else None

    def add(self, match: Match) -> None:
        self.s.add(MatchRow(id=match.id, **{f: getattr(match, f) for f in _FIELDS}))
        self.s.flush()

    def save(self, match: Match) -> None:
        r = self.s.get(MatchRow, match.id)
        if r:
            for f in _FIELDS:
                setattr(r, f, getattr(match, f))
            self.s.flush()

    def for_user(self, user_id: UUID, status: str | None) -> list[Match]:
        stmt = select(MatchRow).where(or_(MatchRow.missing_owner_id == user_id, MatchRow.found_owner_id == user_id))
        if status:
            stmt = stmt.where(MatchRow.status == status)
        return [_to_domain(r) for r in self.s.scalars(stmt.order_by(MatchRow.score.desc()).limit(100))]

    def for_report(self, report_id: UUID) -> list[Match]:
        stmt = select(MatchRow).where(or_(MatchRow.missing_report_id == report_id,
                                          MatchRow.found_report_id == report_id))
        return [_to_domain(r) for r in self.s.scalars(stmt.order_by(MatchRow.score.desc()))]

    def delete_for_report(self, report_id: UUID) -> None:
        self.s.execute(delete(MatchRow).where(or_(MatchRow.missing_report_id == report_id,
                                                  MatchRow.found_report_id == report_id)))


class SqlEmbeddingRepository(EmbeddingRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def for_reports(self, report_ids: list[UUID]) -> dict[UUID, list[list[float]]]:
        out: dict[UUID, list[list[float]]] = defaultdict(list)
        if report_ids:
            for r in self.s.scalars(select(FaceEmbeddingRow).where(FaceEmbeddingRow.report_id.in_(report_ids))):
                out[r.report_id].append(list(r.vector))
        return out

    def replace_for_photo(self, emb: list[Embedding], photo_id: UUID) -> None:
        self.s.execute(delete(FaceEmbeddingRow).where(FaceEmbeddingRow.photo_id == photo_id))
        for e in emb:
            self.s.add(FaceEmbeddingRow(id=uuid4(), report_id=e.report_id, photo_id=e.photo_id,
                                        vector=e.vector, model=e.model))
        self.s.flush()

    def delete_for_report(self, report_id: UUID) -> None:
        self.s.execute(delete(FaceEmbeddingRow).where(FaceEmbeddingRow.report_id == report_id))
