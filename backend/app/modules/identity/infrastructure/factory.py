from uuid import UUID

from app.modules.identity.application.ports import Passwords, Tokens
from app.modules.identity.application.service import IdentityService
from app.modules.identity.infrastructure.repository import SqlResetTokenRepository, SqlUserRepository
from app.modules.media import media_service
from app.shared.infrastructure import security
from app.shared.infrastructure.db import Session
from app.shared.infrastructure.outbox import SqlOutbox


class Argon2Passwords(Passwords):
    def hash(self, password: str) -> str:
        return security.hash_password(password)

    def verify(self, password_hash: str, password: str) -> bool:
        return security.verify_password(password_hash, password)


class JwtTokens(Tokens):
    def issue(self, user_id: UUID, role: str, token_version: int) -> tuple[str, int]:
        return security.issue_token(user_id, role, token_version)

    def reset_token(self) -> tuple[str, str]:
        return security.new_secret_token()

    def hash(self, token: str) -> str:
        return security.sha256(token)


def identity_service(session: Session) -> IdentityService:
    return IdentityService(
        SqlUserRepository(session), SqlResetTokenRepository(session), Argon2Passwords(), JwtTokens(),
        media_service(session), SqlOutbox(session),
    )
