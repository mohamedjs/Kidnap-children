"""geo — optional reverse geocoding for map pins (Google, key from env).

Public API: router, event_handlers
"""

from app.modules.geo.presentation.router import router

event_handlers: dict[str, list[object]] = {}

__all__ = ["event_handlers", "router"]
