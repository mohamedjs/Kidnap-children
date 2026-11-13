from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from app.modules.media import MediaService
from app.modules.reports.domain.report import (
    FOUND,
    MISSING,
    Photo,
    Report,
    ReportDraft,
    ReportRepository,
    SearchCriteria,
    validate_draft,
)
from app.shared.domain.errors import NotFound
from app.shared.domain.events import (
    REPORT_DELETED,
    REPORT_PUBLISHED,
    REPORT_REMATCH_REQUESTED,
    REPORT_RESOLVED,
    REPORT_UPDATED,
    UPLOAD_ORPHANED,
    DomainEvent,
    EventSink,
)
from app.shared.domain.paging import Page, PageRequest
from app.shared.domain.principal import Principal

PHOTO_PURPOSE = "report_photo"


@dataclass(frozen=True)
class ReportChanges:
    draft: ReportDraft | None = None
    add_photo_upload_ids: tuple[UUID, ...] = ()
    remove_photo_ids: tuple[UUID, ...] = ()


class ReportsService:
    def __init__(self, repo: ReportRepository, media: MediaService, events: EventSink) -> None:
        self.repo, self.media, self.events = repo, media, events

    def create(self, who: Principal, draft: ReportDraft, photo_upload_ids: list[UUID]) -> Report:
        d = validate_draft(draft, date.today())
        report = Report(
            id=uuid4(), owner_id=who.user_id, kind=d.kind, status="open", description=d.description, city=d.city,
        )
        report.apply(d)
        report.add_photos(self._claim(who.user_id, photo_upload_ids))
        self.repo.add(report)
        self.events.add(DomainEvent(REPORT_PUBLISHED, self._event(report)))
        return report

    def update(self, who: Principal, report_id: UUID, ch: ReportChanges) -> Report:
        report = self._get(report_id, lock=True)
        report.require_editor(who)
        if ch.draft is not None:
            report.apply(validate_draft(ch.draft, date.today()))
        removed = report.remove_photos(set(ch.remove_photo_ids)) if ch.remove_photo_ids else []
        if ch.add_photo_upload_ids:
            report.add_photos(self._claim(who.user_id, list(ch.add_photo_upload_ids)))
        self.repo.save(report)
        if removed:
            self.events.add(DomainEvent(UPLOAD_ORPHANED, {"keys": removed}))
        self.events.add(DomainEvent(REPORT_UPDATED, self._event(report)))
        return report

    def delete(self, who: Principal, report_id: UUID) -> None:
        report = self._get(report_id, lock=True)
        report.require_editor(who)
        keys = [p.key for p in report.photos]
        self.repo.delete(report.id)
        self.events.add(DomainEvent(REPORT_DELETED, {"report_id": str(report.id), "keys": keys}))

    def resolve(self, who: Principal, report_id: UUID) -> Report:
        report = self._get(report_id, lock=True)
        report.require_editor(who)
        report.resolve(datetime.now(UTC))
        self.repo.save(report)
        self.events.add(DomainEvent(REPORT_RESOLVED, self._event(report)))
        return report

    def reopen(self, who: Principal, report_id: UUID) -> Report:
        report = self._get(report_id, lock=True)
        report.require_editor(who)
        report.reopen()
        self.repo.save(report)
        self.events.add(DomainEvent(REPORT_UPDATED, self._event(report)))
        return report

    def request_rematch(self, who: Principal, report_id: UUID) -> Report:
        """v1: POST /posts/{id}/process-ai."""
        report = self._get(report_id)
        report.require_editor(who)
        self.events.add(DomainEvent(REPORT_REMATCH_REQUESTED, self._event(report)))
        return report

    def get(self, who: Principal | None, report_id: UUID) -> Report:
        report = self._get(report_id)
        if not report.visible_to(who):
            raise NotFound("Report not found")
        return report

    def search(self, criteria: SearchCriteria, page: PageRequest) -> Page[Report]:
        return self.repo.search(criteria, page)

    def stats(self) -> dict[str, int]:
        return self.repo.counts()

    # ── moderation (admin) ──
    def hide(self, report_id: UUID, reason: str) -> Report:
        report = self._get(report_id, lock=True)
        report.hide(reason)
        self.repo.save(report)
        return report

    def unhide(self, report_id: UUID) -> Report:
        report = self._get(report_id, lock=True)
        report.unhide()
        self.repo.save(report)
        return report

    # ── facade for matching ──
    def snapshot(self, report_id: UUID) -> Report | None:
        return self.repo.get(report_id)

    def candidates(self, report: Report, limit: int = 500) -> list[Report]:
        other = FOUND if report.kind == MISSING else MISSING
        return self.repo.open_of_kind(other, exclude_owner=None, limit=limit)

    def set_face_status(self, photo_id: UUID, status: str) -> None:
        self.repo.set_face_status(photo_id, status)

    def photo_url(self, key: str) -> str:
        return self.media.url(key)

    # ── helpers ──
    def _claim(self, uploader: UUID, upload_ids: list[UUID]) -> list[Photo]:
        """Uploads must have been made (and confirmed) by the person attaching them."""
        files = self.media.claim(uploader, upload_ids, PHOTO_PURPOSE)
        return [Photo(id=uuid4(), key=f.key, position=0) for f in files]

    def _get(self, report_id: UUID, lock: bool = False) -> Report:
        report = self.repo.get(report_id, lock=lock)
        if report is None:
            raise NotFound("Report not found")
        return report

    @staticmethod
    def _event(r: Report) -> dict[str, object]:
        return {"report_id": str(r.id), "owner_id": str(r.owner_id), "kind": r.kind, "status": r.status,
                "city": r.city}
