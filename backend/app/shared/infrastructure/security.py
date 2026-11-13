"""Password hashing (argon2id) and access tokens (HS256 JWT)."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.shared.domain.errors import Unauthorized
from app.shared.domain.principal import Principal
from app.shared.infrastructure.config import get_settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def issue_token(user_id: UUID, role: str, token_version: int) -> tuple[str, int]:
    s = get_settings()
    ttl = s.jwt_ttl_minutes * 60
    now = datetime.now(UTC)
    payload = {"sub": str(user_id), "role": role, "tv": token_version, "iat": now, "exp": now + timedelta(seconds=ttl)}
    return jwt.encode(payload, s.jwt_secret, algorithm="HS256"), ttl


def decode_token(token: str) -> tuple[Principal, int]:
    try:
        data = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
        return Principal(user_id=UUID(data["sub"]), role=str(data.get("role", "user"))), int(data.get("tv", 0))
    except (jwt.PyJWTError, KeyError, ValueError) as e:
        raise Unauthorized("Invalid or expired token") from e


def new_secret_token() -> tuple[str, str]:
    """Returns (token for the user, sha256 hash to store)."""
    token = secrets.token_urlsafe(32)
    return token, sha256(token)


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
