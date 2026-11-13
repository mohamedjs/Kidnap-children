from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query, Response
from pydantic import BaseModel, Field

from app.modules.engagement.domain.engagement import Comment
from app.modules.engagement.infrastructure.factory import engagement_service
from app.modules.identity import identity_service
from app.shared.domain.errors import Invalid
from app.shared.domain.paging import PageRequest
from app.shared.infrastructure.db import DbSession, Session
from app.shared.presentation.auth import CurrentPrincipal, MaybePrincipal
from app.shared.presentation.http import ok, page_out

router = APIRouter(tags=["engagement"])


class CommentIn(BaseModel):
    body: str = Field(max_length=1000)


def comments_out(session: Session, items: list[Comment]) -> list[dict[str, Any]]:
    authors = identity_service(session).summaries([c.author_id for c in items])
    return [{
        "id": str(c.id), "report_id": str(c.report_id), "body": c.body,
        "author": a.__dict__ if (a := authors.get(str(c.author_id))) else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    } for c in items]


@router.get("/api/reports/{report_id}/comments")
def list_comments(report_id: UUID, session: DbSession, viewer: MaybePrincipal, page: int = 1,
                  per_page: int = 30) -> dict[str, Any]:
    p = engagement_service(session).list_comments(viewer, report_id, PageRequest.of(page, per_page, 100))
    return page_out(p, comments_out(session, p.items))


@router.post("/api/reports/{report_id}/comments", status_code=201)
def add_comment(report_id: UUID, body: CommentIn, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    c = engagement_service(session).add_comment(me, report_id, body.body)
    return ok(comments_out(session, [c])[0])


@router.delete("/api/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: UUID, session: DbSession, me: CurrentPrincipal) -> Response:
    engagement_service(session).delete_comment(me, comment_id)
    return Response(status_code=204)


@router.post("/api/reports/{report_id}/like")
def toggle_like(report_id: UUID, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    c = engagement_service(session).toggle_like(me, report_id)
    return ok({"likes": c.likes, "liked": c.liked, "comments": c.comments})


@router.get("/api/reports/{report_id}/likes")
def likers(report_id: UUID, session: DbSession, viewer: MaybePrincipal) -> dict[str, Any]:
    ids = engagement_service(session).likers(viewer, report_id)
    users = identity_service(session).summaries(ids)
    return ok([users[str(i)].__dict__ for i in ids if str(i) in users])


@router.get("/api/engagement")
def summary(session: DbSession, viewer: MaybePrincipal, report_ids: str = Query(max_length=2000)) -> dict[str, Any]:
    """Counts for a page of report cards: ?report_ids=a,b,c"""
    try:
        ids = [UUID(x) for x in report_ids.split(",") if x.strip()][:50]
    except ValueError as e:
        raise Invalid("report_ids must be UUIDs") from e
    counts = engagement_service(session).counts(ids, viewer)
    return ok({str(k): {"comments": v.comments, "likes": v.likes, "liked": v.liked} for k, v in counts.items()})
