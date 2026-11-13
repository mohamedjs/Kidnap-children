from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.modules.identity.domain.user import ResetToken, ResetTokenRepository, User, UserRepository
from app.modules.identity.infrastructure.models import PasswordResetRow, UserRow

_FIELDS = (
    "email", "name", "password_hash", "role", "is_active", "token_version", "phone", "city",
    "gender", "birth_date", "bio", "avatar_key", "cover_key",
)


def _to_domain(r: UserRow) -> User:
    return User(
        id=r.id, email=r.email, name=r.name, password_hash=r.password_hash, role=r.role, is_active=r.is_active,
        token_version=r.token_version, phone=r.phone, city=r.city, gender=r.gender, birth_date=r.birth_date,
        bio=r.bio, avatar_key=r.avatar_key, cover_key=r.cover_key, created_at=r.created_at,
    )


class SqlUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def add(self, user: User) -> None:
        self.s.add(UserRow(id=user.id, **{f: getattr(user, f) for f in _FIELDS}))
        self.s.flush()

    def get(self, user_id: UUID) -> User | None:
        row = self.s.get(UserRow, user_id)
        return _to_domain(row) if row else None

    def by_email(self, email: str) -> User | None:
        row = self.s.scalar(select(UserRow).where(UserRow.email == email))
        return _to_domain(row) if row else None

    def save(self, user: User) -> None:
        row = self.s.get(UserRow, user.id)
        if row is None:
            return
        for f in _FIELDS:
            setattr(row, f, getattr(user, f))
        self.s.flush()

    def many(self, ids: list[UUID]) -> list[User]:
        return [_to_domain(r) for r in self.s.scalars(select(UserRow).where(UserRow.id.in_(ids)))]

    def search(self, q: str | None, offset: int, limit: int) -> tuple[list[User], int]:
        stmt = select(UserRow)
        if q:
            like = f"%{q.strip()}%"
            stmt = stmt.where(or_(UserRow.name.ilike(like), UserRow.email.ilike(like)))
        total = self.s.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self.s.scalars(stmt.order_by(UserRow.created_at.desc()).offset(offset).limit(limit))
        return [_to_domain(r) for r in rows], total


class SqlResetTokenRepository(ResetTokenRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def add(self, token: ResetToken) -> None:
        self.s.add(PasswordResetRow(id=token.id, user_id=token.user_id, token_hash=token.token_hash,
                                    expires_at=token.expires_at))
        self.s.flush()

    def by_hash(self, token_hash: str) -> ResetToken | None:
        r = self.s.scalar(select(PasswordResetRow).where(PasswordResetRow.token_hash == token_hash))
        return ResetToken(r.id, r.user_id, r.token_hash, r.expires_at, r.used_at) if r else None

    def mark_used(self, token_id: UUID, when: datetime) -> None:
        self.s.execute(update(PasswordResetRow).where(PasswordResetRow.id == token_id).values(used_at=when))
