from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from app.modules.identity.application.service import IdentityService, ProfileChanges
from app.modules.identity.domain.user import User
from app.modules.identity.infrastructure.factory import identity_service
from app.shared.domain.paging import PageRequest
from app.shared.infrastructure.db import DbSession
from app.shared.presentation.auth import AdminPrincipal, CurrentPrincipal
from app.shared.presentation.http import ok, page_out

router = APIRouter(tags=["identity"])


def user_out(svc: IdentityService, u: User, private: bool = False) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": str(u.id),
        "name": u.name,
        "city": u.city,
        "bio": u.bio,
        "gender": u.gender,
        "avatar_url": svc.avatar_url(u),
        "cover_url": svc.cover_url(u),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }
    if private:
        data |= {
            "email": u.email, "phone": u.phone, "role": u.role, "is_active": u.is_active,
            "birth_date": u.birth_date.isoformat() if u.birth_date else None,
        }
    return data


class RegisterIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)
    name: str = Field(max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    city: str | None = Field(default=None, max_length=80)


class LoginIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class ForgotIn(BaseModel):
    email: str = Field(max_length=254)


class ResetIn(BaseModel):
    token: str = Field(max_length=200)
    password: str = Field(max_length=128)


class ProfileIn(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    city: str | None = Field(default=None, max_length=80)
    gender: str | None = None
    birth_date: date | None = None
    bio: str | None = Field(default=None, max_length=500)
    avatar_upload_id: UUID | None = None
    cover_upload_id: UUID | None = None


class RoleIn(BaseModel):
    role: str


def _session_out(svc: IdentityService, user: User) -> dict[str, Any]:
    token, ttl = svc.token_for(user)
    return ok({"token": token, "expires_in": ttl, "user": user_out(svc, user, private=True)})


@router.post("/api/auth/register", status_code=201)
def register(body: RegisterIn, session: DbSession) -> dict[str, Any]:
    svc = identity_service(session)
    return _session_out(svc, svc.register(body.email, body.password, body.name, body.phone, body.city))


@router.post("/api/auth/login")
def login(body: LoginIn, session: DbSession) -> dict[str, Any]:
    svc = identity_service(session)
    return _session_out(svc, svc.login(body.email, body.password))


@router.post("/api/auth/logout", status_code=204)
def logout(session: DbSession, me: CurrentPrincipal) -> Response:
    identity_service(session).logout(me)
    return Response(status_code=204)


@router.get("/api/auth/me")
def me(session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    svc = identity_service(session)
    return ok(user_out(svc, svc.me(me), private=True))


@router.post("/api/auth/password/forgot", status_code=202)
def forgot(body: ForgotIn, session: DbSession) -> dict[str, Any]:
    identity_service(session).forgot_password(body.email)
    return ok({"sent": True})


@router.post("/api/auth/password/reset")
def reset(body: ResetIn, session: DbSession) -> dict[str, Any]:
    identity_service(session).reset_password(body.token, body.password)
    return ok({"reset": True})


@router.patch("/api/profile")
def update_profile(body: ProfileIn, session: DbSession, me: CurrentPrincipal) -> dict[str, Any]:
    svc = identity_service(session)
    changes = ProfileChanges(**body.model_dump(), fields_set=frozenset(body.model_fields_set))
    return ok(user_out(svc, svc.update_profile(me, changes), private=True))


@router.get("/api/users/{user_id}")
def public_profile(user_id: UUID, session: DbSession) -> dict[str, Any]:
    svc = identity_service(session)
    return ok(user_out(svc, svc.public(user_id)))


# ── admin (new in v2: v1 had no admin) ──
@router.get("/api/admin/users")
def admin_users(
    session: DbSession, _: AdminPrincipal, q: str | None = None, page: int = 1, per_page: int = 20
) -> dict[str, Any]:
    svc = identity_service(session)
    p = svc.list_users(q, PageRequest.of(page, per_page))
    return page_out(p, [user_out(svc, u, private=True) for u in p.items])


@router.post("/api/admin/users/{user_id}/block")
def admin_block(user_id: UUID, session: DbSession, admin: AdminPrincipal) -> dict[str, Any]:
    svc = identity_service(session)
    return ok(user_out(svc, svc.set_active(admin, user_id, False), private=True))


@router.post("/api/admin/users/{user_id}/unblock")
def admin_unblock(user_id: UUID, session: DbSession, admin: AdminPrincipal) -> dict[str, Any]:
    svc = identity_service(session)
    return ok(user_out(svc, svc.set_active(admin, user_id, True), private=True))


@router.post("/api/admin/users/{user_id}/role")
def admin_role(user_id: UUID, body: RoleIn, session: DbSession, admin: AdminPrincipal) -> dict[str, Any]:
    svc = identity_service(session)
    return ok(user_out(svc, svc.set_role(admin, user_id, body.role), private=True))
