"""The worker process: `python -m app.worker`.

Delivers outbox events to module handlers (matching + face analysis, notifications, media
cleanup, dev mailer, optional n8n forwarding) and runs periodic jobs. One event is handled in
one transaction with all its handlers; on failure the transaction rolls back and the event is
retried with back-off, up to MAX_ATTEMPTS.
"""

import logging
import signal
import time
from typing import Any

from app.registry import event_handlers, load_models, periodic_tasks
from app.shared.infrastructure.config import get_settings
from app.shared.infrastructure.db import new_session
from app.shared.infrastructure.relay import deliver_next

log = logging.getLogger("worker")
BATCH = 20
_running = True


def _stop(*_: Any) -> None:
    global _running
    _running = False


def process_batch() -> int:
    handlers = event_handlers()
    done = 0
    while done < BATCH and deliver_next(handlers):
        done += 1
    return done


def run_periodic(last_run: dict[int, float]) -> None:
    now = time.monotonic()
    for i, (task, every) in enumerate(periodic_tasks()):
        if now - last_run.get(i, 0) < every:
            continue
        last_run[i] = now
        with new_session() as session:
            try:
                task(session)
                session.commit()
            except Exception:
                session.rollback()
                log.exception("periodic task %s failed", getattr(task, "__name__", task))


def drain(max_rounds: int = 50) -> int:
    """Process until no event is due (used by the seed and tests)."""
    total = 0
    for _ in range(max_rounds):
        n = process_batch()
        total += n
        if n == 0:
            break
    return total


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    load_models()
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    poll = get_settings().worker_poll_seconds
    log.info("worker started")
    last: dict[int, float] = {}
    while _running:
        n = process_batch()
        run_periodic(last)
        if n == 0:
            time.sleep(poll)
    log.info("worker stopped")


if __name__ == "__main__":
    main()
