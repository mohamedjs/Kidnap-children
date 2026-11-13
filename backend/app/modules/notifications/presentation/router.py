from typing import Any
from uuid import UUID

from fastapi import APIRouter, Response

from app.modules.identity import identity_service
from app.modules.notifications.infrastructure.factory import notifications_service
from app.shared.domain.paging import PageRequest
from app.shared.infrastructure.db import DbSession
from app.shared.presentation.auth import CurrentPrincipal
from app.shared.presentation.http import ok

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def list_notifications(session: DbSession, me: CurrentPrincipal, page: int = 1, per_page: int = 20) -> dict[str, Any]:
    p, unread = notifications_service(session).list(me, PageRequest.of(page, per_page))
    actors = identity_service(session).summaries([n.actor_id for n in p.items if n.actor_id])
    items = [{
        "id": str(n.id), "type": n.type, "link": n.link, "data": n.data,
        "actor": a.__dict__ if n.actor_id and (a := actors.get(str(n.actor_id))) else None,
        "read": n.read_at is not None, "created_at": n.created_at.isoformat() if n.created_at else None,
    } for n in p.items]
    return ok({"items": items, "page": p.page, "per_page": p.per_page, "total": p.total, "unread_count": unread})


@router.get("/unread-count")
def unread(session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    return ok({"unread": notifications_service(session).unread(me)})


@router.post("/read-all")
def read_all(session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    return ok({"updated": notifications_service(session).mark_all_read(me)})


@router.post("/{notification_id}/read", status_code=204)
def read_one(notification_id: UUID, session: DbSession, me: CurrentPrincipal) -> Response:
    notifications_service(session).mark_read(me, notification_id)
    return Response(status_code=204)
