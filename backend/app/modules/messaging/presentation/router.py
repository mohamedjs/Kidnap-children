from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from app.modules.identity import identity_service
from app.modules.messaging.application.service import MessagingService
from app.modules.messaging.domain.message import Message
from app.modules.messaging.infrastructure.factory import messaging_service
from app.shared.infrastructure.db import DbSession
from app.shared.presentation.auth import CurrentPrincipal
from app.shared.presentation.http import ok

router = APIRouter(tags=["messaging"])


class MessageIn(BaseModel):
    recipient_id: UUID
    body: str | None = Field(default=None, max_length=5000)
    attachment_upload_id: UUID | None = None


def message_out(svc: MessagingService, m: Message) -> dict[str, Any]:
    a = m.attachment
    return {
        "id": str(m.id), "sender_id": str(m.sender_id), "recipient_id": str(m.recipient_id), "body": m.body,
        "attachment": {"url": svc.attachment_url(m), "content_type": a.content_type, "name": a.name, "size": a.size}
        if a else None,
        "read_at": m.read_at.isoformat() if m.read_at else None,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


@router.get("/api/conversations")
def conversations(session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    svc = messaging_service(session)
    convs = svc.conversations(me)
    users = identity_service(session).summaries([c.other_id for c in convs])
    return ok([{
        "user": u.__dict__ if (u := users.get(str(c.other_id))) else {"id": str(c.other_id), "name": "?"},
        "last_message": message_out(svc, c.last), "unread_count": c.unread,
    } for c in convs])


@router.get("/api/conversations/{user_id}/messages")
def thread(user_id: UUID, session: DbSession, me: CurrentPrincipal, before: datetime | None = None) -> dict[str, Any]:
    svc = messaging_service(session)
    other = identity_service(session).summaries([user_id]).get(str(user_id))
    return ok({"user": other.__dict__ if other else None,
               "messages": [message_out(svc, m) for m in svc.thread(me, user_id, before)]})


@router.post("/api/messages", status_code=201)
def send(body: MessageIn, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    svc = messaging_service(session)
    return ok(message_out(svc, svc.send(me, body.recipient_id, body.body, body.attachment_upload_id)))


@router.post("/api/messages/{message_id}/read", status_code=204)
def mark_read(message_id: UUID, session: DbSession, me: CurrentPrincipal) -> Response:
    messaging_service(session).mark_read(me, message_id)
    return Response(status_code=204)


@router.get("/api/messages/unread-count")
def unread(session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    return ok({"unread": messaging_service(session).unread(me)})
