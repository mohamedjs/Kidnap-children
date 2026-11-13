"""Matching use cases. `process_report` runs in the worker (it reads image bytes from the
bucket for face analysis); the api only lists and decides matches."""

import logging
from datetime import date
from uuid import UUID, uuid4

from app.modules.matching.domain.match import (
    CONFIRMED,
    SUGGESTED,
    Embedding,
    EmbeddingRepository,
    FaceAnalyzer,
    Match,
    MatchRepository,
)
from app.modules.matching.domain.scoring import Profile, best_face_confidence, combine
from app.modules.reports import (
    FACE_FAILED,
    FACE_FOUND,
    FACE_NONE,
    FACE_PENDING,
    MISSING,
    Report,
    ReportsService,
)
from app.shared.application.storage import ObjectStorage
from app.shared.domain.errors import Forbidden, NotFound
from app.shared.domain.events import MATCH_CONFIRMED, MATCH_SUGGESTED, DomainEvent, EventSink
from app.shared.domain.principal import Principal

log = logging.getLogger("matching")
MAX_IMAGE_BYTES = 10 * 1024 * 1024


def profile(r: Report) -> Profile:
    return Profile(kind=r.kind, gender=r.gender, age=r.age, city=r.city, lat=r.lat, lng=r.lng, seen_on=r.seen_on)


class MatchingService:
    def __init__(
        self,
        matches: MatchRepository,
        embeddings: EmbeddingRepository,
        reports: ReportsService,
        events: EventSink,
        storage: ObjectStorage | None = None,
        analyzer: FaceAnalyzer | None = None,
    ) -> None:
        self.matches, self.embeddings, self.reports, self.events = matches, embeddings, reports, events
        self.storage, self.analyzer = storage, analyzer

    # ── worker ──
    def analyze_photos(self, report: Report, force: bool = False) -> None:
        if self.storage is None or self.analyzer is None:
            return
        for photo in report.photos:
            if photo.face_status != FACE_PENDING and not force:
                continue
            try:
                vectors = self.analyzer.embed(self.storage.read(photo.key, MAX_IMAGE_BYTES))
                status = FACE_FOUND if vectors else FACE_NONE
            except Exception as e:  # undecodable or unreadable file
                log.warning("face analysis failed for photo %s: %s", photo.id, e)
                vectors, status = [], FACE_FAILED
            self.embeddings.replace_for_photo(
                [Embedding(photo.id, report.id, v, self.analyzer.model) for v in vectors], photo.id
            )
            self.reports.set_face_status(photo.id, status)
            photo.face_status = status

    def process_report(self, report_id: UUID, force_faces: bool = False) -> int:
        """Analyse new photos, then score the report against every open report of the other kind.
        Returns the number of new suggestions."""
        report = self.reports.snapshot(report_id)
        if report is None:
            return 0
        self.analyze_photos(report, force_faces)
        if not report.matchable:
            return 0
        candidates = self.reports.candidates(report)
        vectors = self.embeddings.for_reports([report.id] + [c.id for c in candidates])
        today, new = date.today(), 0
        for other in candidates:
            if other.owner_id == report.owner_id:
                continue
            missing, found = (report, other) if report.kind == MISSING else (other, report)
            face = best_face_confidence(vectors.get(missing.id, []), vectors.get(found.id, []))
            score = combine(profile(missing), profile(found), face, today)
            existing = self.matches.find(missing.id, found.id)
            if score is None or not score.suggest:
                continue
            if existing:
                existing.refresh(score.total, score.attributes, score.face, list(score.reasons))
                self.matches.save(existing)
                continue
            m = Match(
                id=uuid4(), missing_report_id=missing.id, found_report_id=found.id,
                missing_owner_id=missing.owner_id, found_owner_id=found.owner_id, score=score.total,
                attribute_score=score.attributes, face_score=score.face, reasons=list(score.reasons),
            )
            self.matches.add(m)
            new += 1
            self.events.add(DomainEvent(MATCH_SUGGESTED, self._event(m)))
        return new

    def forget_report(self, report_id: UUID) -> None:
        self.matches.delete_for_report(report_id)
        self.embeddings.delete_for_report(report_id)

    # ── api ──
    def mine(self, who: Principal, status: str | None) -> list[Match]:
        return self.matches.for_user(who.user_id, status)

    def for_report(self, who: Principal, report_id: UUID) -> list[Match]:
        report = self.reports.snapshot(report_id)
        if report is None:
            raise NotFound("Report not found")
        if not report.can_edit(who):
            raise Forbidden("Only the reporter can see the matches of this report")
        return self.matches.for_report(report_id)

    def decide(self, who: Principal, match_id: UUID, confirm: bool) -> Match:
        m = self.matches.get(match_id)
        if m is None or not (m.involves(who.user_id) or who.is_admin):
            raise NotFound("Match not found")
        m.decide(who.user_id, who.is_admin, confirm)
        self.matches.save(m)
        if m.status == CONFIRMED:
            self.events.add(DomainEvent(MATCH_CONFIRMED, self._event(m) | {"by": str(who.user_id)}))
        return m

    @staticmethod
    def _event(m: Match) -> dict[str, object]:
        return {
            "match_id": str(m.id), "missing_report_id": str(m.missing_report_id),
            "found_report_id": str(m.found_report_id), "missing_owner_id": str(m.missing_owner_id),
            "found_owner_id": str(m.found_owner_id), "score": m.score, "status": m.status or SUGGESTED,
        }
