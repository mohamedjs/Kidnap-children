from typing import Any
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.modules.moderation.infrastructure.factory import moderation_service
from app.modules.reports import reports_out, reports_service
from app.shared.domain.paging import PageRequest
from app.shared.infrastructure.db import DbSession
from app.shared.presentation.auth import AdminPrincipal, CurrentPrincipal
from app.shared.presentation.http import ok

router = APIRouter(tags=["moderation"])


class FlagIn(BaseModel):
    reason: str
    note: str | None = Field(default=None, max_length=300)


class HideIn(BaseModel):
    reason: str = Field(max_length=300)


@router.post("/api/reports/{report_id}/flag", status_code=201)
def flag(report_id: UUID, body: FlagIn, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    hidden = moderation_service(session).flag(me, report_id, body.reason, body.note)
    return ok({"flagged": True, "auto_hidden": hidden})


@router.get("/api/admin/flags")
def queue(session: DbSession, admin: AdminPrincipal, page: int = 1, per_page: int = 20) -> dict[str, Any]:
    p = PageRequest.of(page, per_page)
    rows, total = moderation_service(session).queue(p)
    cards = reports_out(session, reports_service(session), [r for r, _, _ in rows], admin)
    items = [{"report": c, "flags": n, "reasons": reasons} for c, (_, n, reasons) in zip(cards, rows, strict=True)]
    return ok({"items": items, "page": p.page, "per_page": p.per_page, "total": total})


@router.post("/api/admin/reports/{report_id}/hide")
def hide(report_id: UUID, body: HideIn, session: DbSession, admin: AdminPrincipal) -> dict[str, Any]:
    r = moderation_service(session).hide(report_id, body.reason)
    return ok(reports_out(session, reports_service(session), [r], admin)[0])


@router.post("/api/admin/reports/{report_id}/restore")
def restore(report_id: UUID, session: DbSession, admin: AdminPrincipal) -> dict[str, Any]:
    r = moderation_service(session).restore(report_id)
    return ok(reports_out(session, reports_service(session), [r], admin)[0])


@router.post("/api/admin/reports/{report_id}/dismiss-flags")
def dismiss(report_id: UUID, session: DbSession, _: AdminPrincipal) -> dict[str, Any]:
    return ok({"closed": moderation_service(session).dismiss_flags(report_id)})
