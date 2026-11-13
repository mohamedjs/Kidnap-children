"""Container healthchecks (no curl in the slim image).

    python -m scripts.healthcheck api      # /health/ready: database + bucket reachable
    python -m scripts.healthcheck worker   # database reachable and no outbox event stuck > 2 min
"""

import sys
import urllib.request
from datetime import UTC, datetime, timedelta


def api() -> None:
    with urllib.request.urlopen("http://127.0.0.1:4100/health/ready", timeout=4) as res:
        if res.status != 200:
            sys.exit(1)


def worker() -> None:
    from sqlalchemy import func, select

    from app.shared.infrastructure.db import new_session
    from app.shared.infrastructure.outbox import OutboxEvent

    cutoff = datetime.now(UTC) - timedelta(minutes=2)
    with new_session() as s:
        stuck = s.scalar(select(func.count()).select_from(OutboxEvent).where(
            OutboxEvent.processed_at.is_(None), OutboxEvent.attempts == 0, OutboxEvent.created_at < cutoff))
    if stuck:
        print(f"{stuck} outbox events waiting for more than 2 minutes")
        sys.exit(1)


if __name__ == "__main__":
    {"api": api, "worker": worker}[sys.argv[1] if len(sys.argv) > 1 else "api"]()
