from typing import Any
from uuid import UUID

from fastapi import APIRouter

from app.modules.matching.domain.match import Match
from app.modules.matching.infrastructure.factory import matching_service
from app.modules.reports import reports_out, reports_service
from app.shared.domain.principal import Principal
from app.shared.infrastructure.db import DbSession, Session
from app.shared.presentation.auth import CurrentPrincipal
from app.shared.presentation.http import ok

router = APIRouter(tags=["matching"])


def matches_out(session: Session, items: list[Match], viewer: Principal) -> list[dict[str, Any]]:
    svc = reports_service(session)
    ids = {i for m in items for i in (m.missing_report_id, m.found_report_id)}
    reports = [r for r in (svc.snapshot(i) for i in ids) if r is not None]
    cards = {c["id"]: c for c in reports_out(session, svc, reports, viewer)}
    out = []
    for m in items:
        missing, found = cards.get(str(m.missing_report_id)), cards.get(str(m.found_report_id))
        if missing is None or found is None:
            continue
        out.append({
            "id": str(m.id), "score": m.score, "attribute_score": m.attribute_score, "face_score": m.face_score,
            "reasons": m.reasons, "status": m.status, "missing": missing, "found": found,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
    return out


@router.get("/api/matches")
def my_matches(session: DbSession, me: CurrentPrincipal, status: str | None = None) -> dict[str, Any]:
    return ok(matches_out(session, matching_service(session).mine(me, status), me))


@router.get("/api/reports/{report_id}/matches")
def report_matches(report_id: UUID, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    return ok(matches_out(session, matching_service(session).for_report(me, report_id), me))


@router.post("/api/matches/{match_id}/confirm")
def confirm(match_id: UUID, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    return ok(matches_out(session, [matching_service(session).decide(me, match_id, True)], me)[0])


@router.post("/api/matches/{match_id}/dismiss")
def dismiss(match_id: UUID, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    return ok(matches_out(session, [matching_service(session).decide(me, match_id, False)], me)[0])
