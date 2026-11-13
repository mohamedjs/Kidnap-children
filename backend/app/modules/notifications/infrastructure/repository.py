from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.modules.notifications.domain.notification import (
    NewNotification,
    Notification,
    NotificationRepository,
)
from app.modules.notifications.infrastructure.models import NotificationRow


class SqlNotificationRepository(NotificationRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def add_many(self, items: list[NewNotification]) -> None:
        for n in items:
            self.s.add(NotificationRow(id=uuid4(), user_id=UUID(n.user_id),
                                       actor_id=UUID(n.actor_id) if n.actor_id else None,
                                       type=n.type, link=n.link, data=n.data))
        self.s.flush()

    def for_user(self, user_id: UUID, offset: int, limit: int) -> tuple[list[Notification], int]:
        base = select(NotificationRow).where(NotificationRow.user_id == user_id)
        total = self.s.scalar(select(func.count()).select_from(base.subquery())) or 0
        rows = self.s.scalars(base.order_by(NotificationRow.created_at.desc()).offset(offset).limit(limit))
        return [Notification(r.id, r.user_id, r.type, r.link, r.actor_id, dict(r.data or {}), r.read_at,
                             r.created_at) for r in rows], total

    def unread(self, user_id: UUID) -> int:
        return self.s.scalar(select(func.count()).select_from(NotificationRow).where(
            NotificationRow.user_id == user_id, NotificationRow.read_at.is_(None))) or 0

    def mark_read(self, user_id: UUID, notification_id: UUID, when: datetime) -> bool:
        r = self.s.get(NotificationRow, notification_id)
        if r is None or r.user_id != user_id:
            return False
        if r.read_at is None:
            r.read_at = when
        return True

    def mark_all_read(self, user_id: UUID, when: datetime) -> int:
        res = self.s.execute(update(NotificationRow).where(NotificationRow.user_id == user_id,
                                                           NotificationRow.read_at.is_(None)).values(read_at=when))
        return int(getattr(res, "rowcount", 0) or 0)
