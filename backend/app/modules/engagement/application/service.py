from uuid import UUID, uuid4

from app.modules.engagement.domain.engagement import (
    Comment,
    CommentRepository,
    Counts,
    LikeRepository,
    clean_comment,
)
from app.modules.reports import ReportsService
from app.shared.domain.errors import Forbidden, NotFound
from app.shared.domain.events import COMMENT_ADDED, LIKE_ADDED, DomainEvent, EventSink
from app.shared.domain.paging import Page, PageRequest
from app.shared.domain.principal import Principal


class EngagementService:
    def __init__(self, comments: CommentRepository, likes: LikeRepository, reports: ReportsService,
                 events: EventSink) -> None:
        self.comments, self.likes, self.reports, self.events = comments, likes, reports, events

    def list_comments(self, viewer: Principal | None, report_id: UUID, page: PageRequest) -> Page[Comment]:
        self.reports.get(viewer, report_id)
        items, total = self.comments.for_report(report_id, page.offset, page.per_page)
        return Page(items, page.page, page.per_page, total)

    def add_comment(self, who: Principal, report_id: UUID, body: str) -> Comment:
        report = self.reports.get(who, report_id)
        c = Comment(uuid4(), report.id, who.user_id, clean_comment(body))
        self.comments.add(c)
        self.events.add(DomainEvent(COMMENT_ADDED, {
            "comment_id": str(c.id), "report_id": str(report.id), "report_owner_id": str(report.owner_id),
            "author_id": str(who.user_id), "preview": c.body[:80],
        }))
        return c

    def delete_comment(self, who: Principal, comment_id: UUID) -> None:
        c = self.comments.get(comment_id)
        if c is None:
            raise NotFound("Comment not found")
        report = self.reports.snapshot(c.report_id)
        if report is None or not c.can_delete(who, report.owner_id):
            raise Forbidden("You cannot delete this comment")
        self.comments.delete(comment_id)

    def toggle_like(self, who: Principal, report_id: UUID) -> Counts:
        report = self.reports.get(who, report_id)
        if self.likes.exists(report.id, who.user_id):
            self.likes.remove(report.id, who.user_id)
        else:
            self.likes.add(report.id, who.user_id)
            if report.owner_id != who.user_id:
                self.events.add(DomainEvent(LIKE_ADDED, {
                    "report_id": str(report.id), "report_owner_id": str(report.owner_id),
                    "user_id": str(who.user_id),
                }))
        return self.counts([report.id], who)[report.id]

    def likers(self, viewer: Principal | None, report_id: UUID) -> list[UUID]:
        self.reports.get(viewer, report_id)
        return self.likes.users(report_id, 100)

    def counts(self, report_ids: list[UUID], viewer: Principal | None) -> dict[UUID, Counts]:
        c, likes = self.comments.counts(report_ids), self.likes.counts(report_ids)
        liked = self.likes.liked_by(report_ids, viewer.user_id) if viewer else set()
        return {i: Counts(c.get(i, 0), likes.get(i, 0), i in liked) for i in report_ids}
