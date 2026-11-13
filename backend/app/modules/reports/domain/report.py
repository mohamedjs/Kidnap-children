"""A report of a missing child or of a child that was found.

v1 called these "posts" with type `missed` / `founded`; v2 uses kind `missing` / `found`.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from app.shared.domain.errors import Forbidden, Invalid
from app.shared.domain.paging import Page, PageRequest
from app.shared.domain.principal import Principal

MISSING, FOUND = "missing", "found"
KINDS = {MISSING, FOUND}
OPEN, RESOLVED, HIDDEN = "open", "resolved", "hidden"
STATUSES = {OPEN, RESOLVED, HIDDEN}
LEGACY_KIND = {"missed": MISSING, "founded": FOUND}
MAX_PHOTOS = 6
MAX_CHILD_AGE = 17

FACE_PENDING, FACE_FOUND, FACE_NONE, FACE_FAILED = "pending", "face", "no_face", "failed"


@dataclass
class Photo:
    id: UUID
    key: str
    position: int
    face_status: str = FACE_PENDING


@dataclass
class ReportDraft:
    kind: str
    description: str
    city: str
    child_name: str | None = None
    gender: str | None = None
    age: int | None = None
    area: str | None = None
    lat: float | None = None
    lng: float | None = None
    seen_on: date | None = None
    contact_phone: str | None = None


def normalize_kind(kind: str) -> str:
    k = LEGACY_KIND.get(kind, kind)
    if k not in KINDS:
        raise Invalid("Kind must be 'missing' or 'found'", "kind")
    return k


def validate_draft(d: ReportDraft, today: date) -> ReportDraft:
    kind = normalize_kind(d.kind)
    name = " ".join((d.child_name or "").split()) or None
    if kind == MISSING and not name:
        raise Invalid("A missing-child report needs the child's name", "child_name")
    if name and not 2 <= len(name) <= 80:
        raise Invalid("Name must be 2-80 characters", "child_name")
    if d.gender not in (None, "male", "female"):
        raise Invalid("Gender must be male or female", "gender")
    if d.age is not None and not 0 <= d.age <= MAX_CHILD_AGE:
        raise Invalid(f"Age must be between 0 and {MAX_CHILD_AGE}", "age")
    description = d.description.strip()
    if len(description) < 10:
        raise Invalid("Describe the child and the circumstances (at least 10 characters)", "description")
    if len(description) > 4000:
        raise Invalid("Description is too long", "description")
    city = " ".join(d.city.split())
    if not 2 <= len(city) <= 80:
        raise Invalid("City is required", "city")
    if (d.lat is None) != (d.lng is None):
        raise Invalid("Send both latitude and longitude, or neither", "location")
    if d.lat is not None and d.lng is not None and not (-90 <= d.lat <= 90 and -180 <= d.lng <= 180):
        raise Invalid("Location is out of range", "location")
    if d.seen_on is not None and (d.seen_on > today or d.seen_on.year < today.year - 30):
        raise Invalid("The date is not plausible", "seen_on")
    return ReportDraft(
        kind=kind, description=description, city=city, child_name=name, gender=d.gender, age=d.age,
        area=" ".join((d.area or "").split())[:80] or None, lat=d.lat, lng=d.lng, seen_on=d.seen_on,
        contact_phone=(d.contact_phone or "").strip()[:30] or None,
    )


@dataclass
class Report:
    id: UUID
    owner_id: UUID
    kind: str
    status: str
    description: str
    city: str
    child_name: str | None = None
    gender: str | None = None
    age: int | None = None
    area: str | None = None
    lat: float | None = None
    lng: float | None = None
    seen_on: date | None = None
    contact_phone: str | None = None
    hidden_reason: str | None = None
    status_before_hide: str | None = None
    photos: list[Photo] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    resolved_at: datetime | None = None

    # ── permissions ──
    def can_edit(self, who: Principal | None) -> bool:
        return who is not None and (who.user_id == self.owner_id or who.is_admin)

    def visible_to(self, who: Principal | None) -> bool:
        return self.status != HIDDEN or self.can_edit(who)

    def require_editor(self, who: Principal | None) -> None:
        if not self.can_edit(who):
            raise Forbidden("Only the reporter can change this report")

    # ── changes ──
    def apply(self, d: ReportDraft) -> None:
        if d.kind != self.kind:
            raise Invalid("The kind of a report cannot change; create a new report", "kind")
        for f in ("description", "city", "child_name", "gender", "age", "area", "lat", "lng", "seen_on",
                  "contact_phone"):
            setattr(self, f, getattr(d, f))

    def add_photos(self, photos: list[Photo]) -> None:
        if len(self.photos) + len(photos) > MAX_PHOTOS:
            raise Invalid(f"A report can have at most {MAX_PHOTOS} photos", "photos")
        start = max((p.position for p in self.photos), default=-1) + 1
        for i, p in enumerate(photos):
            p.position = start + i
            self.photos.append(p)

    def remove_photos(self, photo_ids: set[UUID]) -> list[str]:
        removed = [p.key for p in self.photos if p.id in photo_ids]
        self.photos = [p for p in self.photos if p.id not in photo_ids]
        return removed

    def resolve(self, now: datetime) -> None:
        if self.status != OPEN:
            raise Invalid("Only an open report can be marked as resolved", "status")
        self.status, self.resolved_at = RESOLVED, now

    def reopen(self) -> None:
        if self.status != RESOLVED:
            raise Invalid("Only a resolved report can be reopened", "status")
        self.status, self.resolved_at = OPEN, None

    def hide(self, reason: str) -> None:
        if self.status == HIDDEN:
            return
        if not reason.strip():
            raise Invalid("Give a reason for hiding the report", "reason")
        self.status_before_hide, self.status, self.hidden_reason = self.status, HIDDEN, reason.strip()[:300]

    def unhide(self) -> None:
        if self.status != HIDDEN:
            return
        self.status, self.hidden_reason = self.status_before_hide or OPEN, None
        self.status_before_hide = None

    @property
    def matchable(self) -> bool:
        return self.status == OPEN


@dataclass(frozen=True)
class SearchCriteria:
    q: str | None = None
    kind: str | None = None
    gender: str | None = None
    age_from: int | None = None
    age_to: int | None = None
    city: str | None = None
    owner_id: UUID | None = None
    statuses: tuple[str, ...] = (OPEN, RESOLVED)


def build_criteria(
    *, q: str | None = None, kind: str | None = None, gender: str | None = None, age: int | None = None,
    age_from: int | None = None, age_to: int | None = None, city: str | None = None,
    owner_id: UUID | None = None, status: str | None = None, viewer: Principal | None = None,
) -> SearchCriteria:
    """v1 filters: text, type, gender, exact age, age range from/to, user_id."""
    if age is not None:
        age_from = age_to = age
    clamp = lambda v: None if v is None else max(0, min(MAX_CHILD_AGE, v))  # noqa: E731
    lo, hi = clamp(age_from), clamp(age_to)
    if lo is not None and hi is not None and lo > hi:
        lo, hi = hi, lo
    statuses: tuple[str, ...] = (OPEN, RESOLVED)
    if status:
        if status not in STATUSES:
            raise Invalid("Unknown status", "status")
        if status == HIDDEN and not (viewer and viewer.is_admin):
            raise Forbidden("Only admins can list hidden reports")
        statuses = (status,)
    text = " ".join((q or "").split())[:100] or None
    return SearchCriteria(
        q=text, kind=normalize_kind(kind) if kind else None,
        gender=gender if gender in ("male", "female") else None,
        age_from=lo, age_to=hi, city=(city or "").strip() or None, owner_id=owner_id, statuses=statuses,
    )


class ReportRepository(Protocol):
    def add(self, report: Report) -> None: ...

    def get(self, report_id: UUID, lock: bool = False) -> Report | None: ...

    def save(self, report: Report) -> None: ...

    def delete(self, report_id: UUID) -> None: ...

    def search(self, c: SearchCriteria, page: PageRequest) -> Page[Report]: ...

    def open_of_kind(self, kind: str, exclude_owner: UUID | None, limit: int) -> list[Report]: ...

    def set_face_status(self, photo_id: UUID, status: str) -> None: ...

    def counts(self) -> dict[str, int]: ...
