from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.modules.notifications.domain.notification import (
    Notification,
    NotificationRepository,
    notifications_for,
)
from app.shared.domain.errors import NotFound
from app.shared.domain.paging import Page, PageRequest
from app.shared.domain.principal import Principal


class NotificationsService:
    def __init__(self, repo: NotificationRepository) -> None:
        self.repo = repo

    def on_event(self, event_type: str, payload: dict[str, Any]) -> int:
        items = notifications_for(event_type, payload)
        if items:
            self.repo.add_many(items)
        return len(items)

    def list(self, who: Principal, page: PageRequest) -> tuple[Page[Notification], int]:
        items, total = self.repo.for_user(who.user_id, page.offset, page.per_page)
        return Page(items, page.page, page.per_page, total), self.repo.unread(who.user_id)

    def unread(self, who: Principal) -> int:
        return self.repo.unread(who.user_id)

    def mark_read(self, who: Principal, notification_id: UUID) -> None:
        if not self.repo.mark_read(who.user_id, notification_id, datetime.now(UTC)):
            raise NotFound("Notification not found")

    def mark_all_read(self, who: Principal) -> int:
        return self.repo.mark_all_read(who.user_id, datetime.now(UTC))
