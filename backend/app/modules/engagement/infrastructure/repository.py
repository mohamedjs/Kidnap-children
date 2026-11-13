from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.engagement.domain.engagement import Comment, CommentRepository, LikeRepository
from app.modules.engagement.infrastructure.models import CommentRow, LikeRow


class SqlCommentRepository(CommentRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def add(self, c: Comment) -> None:
        row = CommentRow(id=c.id, report_id=c.report_id, author_id=c.author_id, body=c.body)
        self.s.add(row)
        self.s.flush()
        self.s.refresh(row)
        c.created_at = row.created_at

    def get(self, comment_id: UUID) -> Comment | None:
        r = self.s.get(CommentRow, comment_id)
        return Comment(r.id, r.report_id, r.author_id, r.body, r.created_at) if r else None

    def delete(self, comment_id: UUID) -> None:
        self.s.execute(delete(CommentRow).where(CommentRow.id == comment_id))

    def for_report(self, report_id: UUID, offset: int, limit: int) -> tuple[list[Comment], int]:
        base = select(CommentRow).where(CommentRow.report_id == report_id)
        total = self.s.scalar(select(func.count()).select_from(base.subquery())) or 0
        rows = self.s.scalars(base.order_by(CommentRow.created_at.asc()).offset(offset).limit(limit))
        return [Comment(r.id, r.report_id, r.author_id, r.body, r.created_at) for r in rows], total

    def counts(self, report_ids: list[UUID]) -> dict[UUID, int]:
        if not report_ids:
            return {}
        rows = self.s.execute(select(CommentRow.report_id, func.count()).where(CommentRow.report_id.in_(report_ids))
                              .group_by(CommentRow.report_id))
        return {rid: n for rid, n in rows}


class SqlLikeRepository(LikeRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def exists(self, report_id: UUID, user_id: UUID) -> bool:
        return self.s.get(LikeRow, (report_id, user_id)) is not None

    def add(self, report_id: UUID, user_id: UUID) -> None:
        self.s.execute(insert(LikeRow).values(report_id=report_id, user_id=user_id).on_conflict_do_nothing())

    def remove(self, report_id: UUID, user_id: UUID) -> None:
        self.s.execute(delete(LikeRow).where(LikeRow.report_id == report_id, LikeRow.user_id == user_id))

    def users(self, report_id: UUID, limit: int) -> list[UUID]:
        return list(self.s.scalars(select(LikeRow.user_id).where(LikeRow.report_id == report_id)
                                   .order_by(LikeRow.created_at.desc()).limit(limit)))

    def counts(self, report_ids: list[UUID]) -> dict[UUID, int]:
        if not report_ids:
            return {}
        rows = self.s.execute(select(LikeRow.report_id, func.count()).where(LikeRow.report_id.in_(report_ids))
                              .group_by(LikeRow.report_id))
        return {rid: n for rid, n in rows}

    def liked_by(self, report_ids: list[UUID], user_id: UUID) -> set[UUID]:
        if not report_ids:
            return set()
        return set(self.s.scalars(select(LikeRow.report_id).where(LikeRow.report_id.in_(report_ids),
                                                                  LikeRow.user_id == user_id)))
