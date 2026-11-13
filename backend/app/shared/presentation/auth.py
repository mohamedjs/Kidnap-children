"""Bearer-token dependencies shared by every module.

Tokens are decoded here; whether the account is still active and the token not revoked
is answered by a checker that the identity module registers at import time. This keeps
modules free of a dependency on identity just to authenticate a request.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request

from app.shared.domain.errors import Forbidden, Unauthorized
from app.shared.domain.principal import Principal
from app.shared.infrastructure.db import Session, get_session
from app.shared.infrastructure.security import decode_token

PrincipalCheck = Callable[[Session, Principal, int], Principal | None]
_checks: list[PrincipalCheck] = []


def register_principal_check(check: PrincipalCheck) -> None:
    _checks.append(check)


def _bearer(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip() or None
    return None


def optional_principal(request: Request, session: Session = Depends(get_session)) -> Principal | None:
    token = _bearer(request)
    if not token:
        return None
    principal, version = decode_token(token)
    for check in _checks:
        checked = check(session, principal, version)
        if checked is None:
            raise Unauthorized("Session is no longer valid")
        principal = checked
    return principal


def require_principal(principal: Principal | None = Depends(optional_principal)) -> Principal:
    if principal is None:
        raise Unauthorized("Login required")
    return principal


def require_admin(principal: Principal = Depends(require_principal)) -> Principal:
    if not principal.is_admin:
        raise Forbidden("Admins only")
    return principal


CurrentPrincipal = Annotated[Principal, Depends(require_principal)]
MaybePrincipal = Annotated[Principal | None, Depends(optional_principal)]
AdminPrincipal = Annotated[Principal, Depends(require_admin)]
