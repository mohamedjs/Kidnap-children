from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from app.modules.identity import identity_service
from app.modules.reports.application.service import ReportChanges, ReportsService
from app.modules.reports.domain.report import Report, ReportDraft, build_criteria
from app.modules.reports.infrastructure.factory import reports_service
from app.shared.domain.paging import PageRequest
from app.shared.domain.principal import Principal
from app.shared.infrastructure.db import DbSession, Session
from app.shared.presentation.auth import CurrentPrincipal, MaybePrincipal
from app.shared.presentation.http import ok, page_out

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportIn(BaseModel):
    kind: str = Field(examples=["missing"])
    description: str = Field(max_length=4000)
    city: str = Field(max_length=80)
    child_name: str | None = Field(default=None, max_length=80)
    gender: str | None = None
    age: int | None = None
    area: str | None = Field(default=None, max_length=80)
    lat: float | None = None
    lng: float | None = None
    seen_on: date | None = None
    contact_phone: str | None = Field(default=None, max_length=30)


class ReportCreate(ReportIn):
    photo_upload_ids: list[UUID] = Field(default_factory=list, max_length=6)


class ReportUpdate(BaseModel):
    report: ReportIn | None = None
    add_photo_upload_ids: list[UUID] = Field(default_factory=list, max_length=6)
    remove_photo_ids: list[UUID] = Field(default_factory=list, max_length=6)


def report_out(svc: ReportsService, r: Report, owners: dict[str, Any], viewer: Principal | None) -> dict[str, Any]:
    owner = owners.get(str(r.owner_id))
    editor = r.can_edit(viewer)
    return {
        "id": str(r.id),
        "kind": r.kind,
        "status": r.status,
        "child_name": r.child_name,
        "gender": r.gender,
        "age": r.age,
        "description": r.description,
        "city": r.city,
        "area": r.area,
        "lat": r.lat,
        "lng": r.lng,
        "seen_on": r.seen_on.isoformat() if r.seen_on else None,
        # the contact phone is shown to signed-in users only (v1 showed everything to everyone)
        "contact_phone": r.contact_phone if viewer else None,
        "hidden_reason": r.hidden_reason if editor else None,
        "photos": [{"id": str(p.id), "url": svc.photo_url(p.key), "face_status": p.face_status} for p in r.photos],
        "owner": owner.__dict__ if owner else None,
        "can_edit": editor,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
    }


def reports_out(session: Session, svc: ReportsService, items: list[Report], viewer: Principal | None) -> list[Any]:
    owners = identity_service(session).summaries([r.owner_id for r in items])
    return [report_out(svc, r, owners, viewer) for r in items]


def _draft(b: ReportIn) -> ReportDraft:
    return ReportDraft(**b.model_dump(include=set(ReportIn.model_fields)))


@router.get("")
def search(
    session: DbSession,
    viewer: MaybePrincipal,
    q: str | None = None,
    kind: str | None = None,
    type: str | None = None,  # v1 name: missed | founded
    gender: str | None = None,
    age: int | None = None,
    age_from: int | None = None,
    age_to: int | None = None,
    city: str | None = None,
    owner_id: UUID | None = None,
    user_id: UUID | None = None,  # v1 name
    status: str | None = None,
    page: int = 1,
    per_page: int = 15,
) -> dict[str, Any]:
    svc = reports_service(session)
    criteria = build_criteria(
        q=q, kind=kind or type, gender=gender, age=age, age_from=age_from, age_to=age_to, city=city,
        owner_id=owner_id or user_id, status=status, viewer=viewer,
    )
    p = svc.search(criteria, PageRequest.of(page, per_page))
    return page_out(p, reports_out(session, svc, p.items, viewer))


@router.get("/stats")
def stats(session: DbSession) -> dict[str, Any]:
    return ok(reports_service(session).stats())


@router.post("", status_code=201)
def create(body: ReportCreate, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    svc = reports_service(session)
    r = svc.create(me, _draft(body), body.photo_upload_ids)
    return ok(reports_out(session, svc, [r], me)[0])


@router.get("/{report_id}")
def get(report_id: UUID, session: DbSession, viewer: MaybePrincipal) -> dict[str, Any]:
    svc = reports_service(session)
    return ok(reports_out(session, svc, [svc.get(viewer, report_id)], viewer)[0])


@router.patch("/{report_id}")
def update(report_id: UUID, body: ReportUpdate, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    svc = reports_service(session)
    ch = ReportChanges(
        draft=_draft(body.report) if body.report else None,
        add_photo_upload_ids=tuple(body.add_photo_upload_ids),
        remove_photo_ids=tuple(body.remove_photo_ids),
    )
    return ok(reports_out(session, svc, [svc.update(me, report_id, ch)], me)[0])


@router.delete("/{report_id}", status_code=204)
def delete(report_id: UUID, session: DbSession, me: CurrentPrincipal) -> Response:
    reports_service(session).delete(me, report_id)
    return Response(status_code=204)


@router.post("/{report_id}/resolve")
def resolve(report_id: UUID, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    svc = reports_service(session)
    return ok(reports_out(session, svc, [svc.resolve(me, report_id)], me)[0])


@router.post("/{report_id}/reopen")
def reopen(report_id: UUID, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    svc = reports_service(session)
    return ok(reports_out(session, svc, [svc.reopen(me, report_id)], me)[0])


@router.post("/{report_id}/rematch", status_code=202)
def rematch(report_id: UUID, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    reports_service(session).request_rematch(me, report_id)
    return ok({"queued": True})
