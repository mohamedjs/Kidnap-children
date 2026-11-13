"""identity — accounts, login (argon2id + JWT), password reset, profiles, admin user management.

Public API: router, IdentityService, UserSummary, identity_service(session), event_handlers
"""

import logging
from typing import Any

from app.modules.identity.application.service import IdentityService, UserSummary
from app.modules.identity.infrastructure.factory import identity_service
from app.modules.identity.presentation.router import router
from app.shared.domain.events import PASSWORD_RESET_REQUESTED
from app.shared.domain.principal import Principal
from app.shared.infrastructure.config import get_settings
from app.shared.infrastructure.db import Session
from app.shared.presentation.auth import register_principal_check

log = logging.getLogger("mailer")


def _check(session: Session, principal: Principal, token_version: int) -> Principal | None:
    return identity_service(session).check_principal(principal, token_version)


register_principal_check(_check)


def _send_reset_mail(_: Session, payload: dict[str, Any]) -> None:
    # Dev mailer: no mail provider is configured, so the link goes to the worker log.
    link = f"{get_settings().public_web_url}/reset-password?token={payload.get('token', '')}"
    log.warning("DEV MAILER - password reset for %s: %s", payload.get("email"), link)


event_handlers = {PASSWORD_RESET_REQUESTED: [_send_reset_mail]}

__all__ = ["IdentityService", "UserSummary", "event_handlers", "identity_service", "router"]
