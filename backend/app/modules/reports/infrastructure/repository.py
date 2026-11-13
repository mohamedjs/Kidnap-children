from uuid import UUID

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.orm import Session

from app.modules.reports.domain.report import Photo, Report, ReportRepository, SearchCriteria
from app.modules.reports.infrastructure.models import ReportPhotoRow, ReportRow
from app.shared.domain.paging import Page, PageRequest

_FIELDS = (
    "owner_id", "kind", "status", "child_name", "gender", "age", "description", "city", "area", "lat", "lng",
    "seen_on", "contact_phone", "hidden_reason", "status_before_hide", "resolved_at",
)


def _to_domain(r: ReportRow) -> Report:
    return Report(
        id=r.id, owner_id=r.owner_id, kind=r.kind, status=r.status, description=r.description, city=r.city,
        child_name=r.child_name, gender=r.gender, age=r.age, area=r.area, lat=r.lat, lng=r.lng,
        seen_on=r.seen_on, contact_phone=r.contact_phone, hidden_reason=r.hidden_reason,
        status_before_hide=r.status_before_hide,
        photos=[Photo(p.id, p.key, p.position, p.face_status) for p in r.photos],
        created_at=r.created_at, updated_at=r.updated_at, resolved_at=r.resolved_at,
    )


class SqlReportRepository(ReportRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def add(self, report: Report) -> None:
        row = ReportRow(id=report.id, **{f: getattr(report, f) for f in _FIELDS})
        row.photos = [ReportPhotoRow(id=p.id, key=p.key, position=p.position, face_status=p.face_status)
                      for p in report.photos]
        self.s.add(row)
        self.s.flush()
        self.s.refresh(row)
        report.created_at, report.updated_at = row.created_at, row.updated_at

    def get(self, report_id: UUID, lock: bool = False) -> Report | None:
        stmt = select(ReportRow).where(ReportRow.id == report_id)
        if lock:
            stmt = stmt.with_for_update()
        row = self.s.scalar(stmt)
        return _to_domain(row) if row else None

    def save(self, report: Report) -> None:
        row = self.s.get(ReportRow, report.id)
        if row is None:
            return
        for f in _FIELDS:
            setattr(row, f, getattr(report, f))
        existing = {p.id: p for p in row.photos}
        keep = {p.id for p in report.photos}
        row.photos = [p for p in row.photos if p.id in keep]
        for p in report.photos:
            if p.id in existing:
                existing[p.id].position = p.position
            else:
                row.photos.append(ReportPhotoRow(id=p.id, key=p.key, position=p.position, face_status=p.face_status))
        self.s.flush()

    def delete(self, report_id: UUID) -> None:
        self.s.execute(delete(ReportRow).where(ReportRow.id == report_id))

    def search(self, c: SearchCriteria, page: PageRequest) -> Page[Report]:
        stmt = select(ReportRow).where(ReportRow.status.in_(c.statuses))
        if c.q:
            like = f"%{c.q}%"
            stmt = stmt.where(or_(ReportRow.child_name.ilike(like), ReportRow.description.ilike(like),
                                  ReportRow.city.ilike(like), ReportRow.area.ilike(like)))
        if c.kind:
            stmt = stmt.where(ReportRow.kind == c.kind)
        if c.gender:
            stmt = stmt.where(ReportRow.gender == c.gender)
        if c.age_from is not None:
            stmt = stmt.where(ReportRow.age >= c.age_from)
        if c.age_to is not None:
            stmt = stmt.where(ReportRow.age <= c.age_to)
        if c.city:
            stmt = stmt.where(ReportRow.city.ilike(f"%{c.city}%"))
        if c.owner_id:
            stmt = stmt.where(ReportRow.owner_id == c.owner_id)
        total = self.s.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self.s.scalars(stmt.order_by(ReportRow.created_at.desc()).offset(page.offset).limit(page.per_page))
        return Page([_to_domain(r) for r in rows], page.page, page.per_page, total)

    def open_of_kind(self, kind: str, exclude_owner: UUID | None, limit: int) -> list[Report]:
        stmt = select(ReportRow).where(ReportRow.kind == kind, ReportRow.status == "open")
        if exclude_owner:
            stmt = stmt.where(ReportRow.owner_id != exclude_owner)
        return [_to_domain(r) for r in self.s.scalars(stmt.order_by(ReportRow.created_at.desc()).limit(limit))]

    def set_face_status(self, photo_id: UUID, status: str) -> None:
        self.s.execute(update(ReportPhotoRow).where(ReportPhotoRow.id == photo_id).values(face_status=status))

    def counts(self) -> dict[str, int]:
        rows = self.s.execute(select(ReportRow.kind, ReportRow.status, func.count()).group_by(ReportRow.kind,
                                                                                              ReportRow.status))
        out = {"missing_open": 0, "found_open": 0, "resolved": 0}
        for kind, status, n in rows:
            if status == "open":
                out[f"{kind}_open"] = out.get(f"{kind}_open", 0) + n
            elif status == "resolved":
                out["resolved"] += n
        return out
