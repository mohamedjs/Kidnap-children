"""Composition root: the list of modules. Used by the api, the worker and Alembic."""

from collections import defaultdict
from collections.abc import Callable
from types import ModuleType
from typing import Any

from app.modules import (
    engagement,
    geo,
    identity,
    matching,
    media,
    messaging,
    moderation,
    notifications,
    reports,
)
from app.shared.infrastructure import outbox as _outbox  # noqa: F401  (outbox_events table)

MODULES: list[ModuleType] = [identity, media, reports, matching, engagement, messaging, notifications, moderation, geo]

Handler = Callable[[Any, dict[str, Any]], None]


def event_handlers() -> dict[str, list[Handler]]:
    out: dict[str, list[Handler]] = defaultdict(list)
    for m in MODULES:
        for event_type, handlers in getattr(m, "event_handlers", {}).items():
            out[event_type].extend(handlers)
    return out


def periodic_tasks() -> list[tuple[Callable[[Any], None], float]]:
    return [t for m in MODULES for t in getattr(m, "periodic_tasks", [])]


def load_models() -> None:
    """Import every module's ORM models so Base.metadata is complete."""
    import importlib

    for m in MODULES:
        try:
            importlib.import_module(f"{m.__name__}.infrastructure.models")
        except ModuleNotFoundError:
            pass
