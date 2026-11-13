"""Outbox relay: hands one due outbox event at a time to the module handlers."""

import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import or_, select, update

from app.shared.infrastructure.db import new_session
from app.shared.infrastructure.outbox import OutboxEvent
from app.shared.infrastructure.webhook import forward_to_n8n

log = logging.getLogger("relay")
MAX_ATTEMPTS = 5
Handlers = dict[str, list[Callable[[Any, dict[str, Any]], None]]]


def deliver_next(handlers: Handlers) -> bool:
    """Lock one due event, run all its handlers in the same transaction, mark it processed.
    The row lock (SKIP LOCKED) is held until commit, so several workers can run safely."""
    now = datetime.now(UTC)
    with new_session() as session:
        row = session.scalar(
            select(OutboxEvent)
            .where(OutboxEvent.processed_at.is_(None), OutboxEvent.attempts < MAX_ATTEMPTS,
                   or_(OutboxEvent.next_attempt_at.is_(None), OutboxEvent.next_attempt_at <= now))
            .order_by(OutboxEvent.id).limit(1).with_for_update(skip_locked=True)
        )
        if row is None:
            return False
        event_id, event_type, payload = row.id, row.type, dict(row.payload or {})
        try:
            for handler in handlers.get(event_type, []):
                handler(session, payload)
            forward_to_n8n(event_type, payload)
            row.processed_at, row.last_error = datetime.now(UTC), None
            if payload.get("_sensitive"):
                row.payload = {"redacted": True}
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            log.exception("event %s (%s) failed", event_id, event_type)
            error = str(e)[:1000]
    with new_session() as s2:
        attempts = (s2.scalar(select(OutboxEvent.attempts).where(OutboxEvent.id == event_id)) or 0) + 1
        s2.execute(update(OutboxEvent).where(OutboxEvent.id == event_id).values(
            attempts=attempts, last_error=error, next_attempt_at=datetime.now(UTC) + timedelta(seconds=2 ** attempts)))
        s2.commit()
    return True
