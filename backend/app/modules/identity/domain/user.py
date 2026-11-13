"""Accounts and profile rules."""

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from app.shared.domain.errors import Invalid
from app.shared.domain.principal import ROLE_ADMIN, ROLE_USER

GENDERS = {"male", "female"}
ROLES = {ROLE_USER, ROLE_ADMIN}
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE = re.compile(r"^\+?[0-9 ()-]{6,20}$")


def normalize_email(email: str) -> str:
    value = email.strip().lower()
    if not _EMAIL.match(value) or len(value) > 254:
        raise Invalid("Enter a valid e-mail address", "email")
    return value


def check_password(password: str) -> None:
    if len(password) < 8:
        raise Invalid("Password must be at least 8 characters", "password")
    if len(password) > 128:
        raise Invalid("Password is too long", "password")
    if password.isdigit() or password.isalpha():
        raise Invalid("Use letters and numbers in the password", "password")


def clean_name(name: str) -> str:
    value = " ".join(name.split())
    if not 2 <= len(value) <= 80:
        raise Invalid("Name must be 2-80 characters", "name")
    return value


def clean_phone(phone: str | None) -> str | None:
    if phone is None or not phone.strip():
        return None
    value = phone.strip()
    if not _PHONE.match(value):
        raise Invalid("Enter a valid phone number", "phone")
    return value


def clean_gender(gender: str | None) -> str | None:
    if gender in (None, ""):
        return None
    if gender not in GENDERS:
        raise Invalid("Gender must be male or female", "gender")
    return gender


def clean_birth_date(value: date | None, today: date) -> date | None:
    if value is None:
        return None
    if value > today or value.year < today.year - 120:
        raise Invalid("Birth date is not plausible", "birth_date")
    return value


@dataclass
class User:
    id: UUID
    email: str
    name: str
    password_hash: str
    role: str = ROLE_USER
    is_active: bool = True
    token_version: int = 0
    phone: str | None = None
    city: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    bio: str | None = None
    avatar_key: str | None = None
    cover_key: str | None = None
    created_at: datetime | None = None
    extra: dict[str, str] = field(default_factory=dict)

    def revoke_sessions(self) -> None:
        self.token_version += 1

    def block(self) -> None:
        self.is_active = False
        self.revoke_sessions()

    def set_role(self, role: str) -> None:
        if role not in ROLES:
            raise Invalid("Unknown role", "role")
        self.role = role
        self.revoke_sessions()


@dataclass(frozen=True)
class ResetToken:
    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = None

    def usable(self, now: datetime) -> bool:
        return self.used_at is None and now < self.expires_at


class UserRepository(Protocol):
    def add(self, user: User) -> None: ...

    def get(self, user_id: UUID) -> User | None: ...

    def by_email(self, email: str) -> User | None: ...

    def save(self, user: User) -> None: ...

    def many(self, ids: list[UUID]) -> list[User]: ...

    def search(self, q: str | None, offset: int, limit: int) -> tuple[list[User], int]: ...


class ResetTokenRepository(Protocol):
    def add(self, token: ResetToken) -> None: ...

    def by_hash(self, token_hash: str) -> ResetToken | None: ...

    def mark_used(self, token_id: UUID, when: datetime) -> None: ...
