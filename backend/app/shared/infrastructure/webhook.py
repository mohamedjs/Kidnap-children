"""Optional n8n forwarding (v1 shipped n8n workflow blueprints). Off unless N8N_WEBHOOK_URL is set."""

import hashlib
import hmac
import json
import logging
from typing import Any

import httpx

from app.shared.infrastructure.config import get_settings

log = logging.getLogger("webhook")
FORWARDED = {"report.published", "report.resolved", "match.suggested", "match.confirmed"}


def forward_to_n8n(event_type: str, payload: dict[str, Any]) -> None:
    s = get_settings()
    if not s.n8n_webhook_url or event_type not in FORWARDED:
        return
    body = json.dumps({"type": event_type, "payload": payload}).encode()
    headers = {"Content-Type": "application/json"}
    if s.n8n_webhook_secret:
        sig = hmac.new(s.n8n_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        headers["X-Signature-256"] = f"sha256={sig}"
    res = httpx.post(s.n8n_webhook_url, content=body, headers=headers, timeout=10)
    res.raise_for_status()
