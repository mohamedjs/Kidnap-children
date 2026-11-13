from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

from app.modules.identity.application.ports import Passwords, Tokens
from app.modules.identity.domain.user import (
    ResetToken,
    ResetTokenRepository,
    User,
    UserRepository,
    check_password,
    clean_birth_date,
    clean_gender,
    clean_name,
    clean_phone,
    normalize_email,
)
from app.modules.media import MediaService
from app.shared.domain.errors import Conflict, Invalid, NotFound, Unauthorized
from app.shared.domain.events import PASSWORD_RESET_REQUESTED, UPLOAD_ORPHANED, DomainEvent, EventSink
from app.shared.domain.paging import Page, PageRequest
from app.shared.domain.principal import Principal


@dataclass(frozen=True)
class UserSummary:
    id: str
    name: str
    city: str | None
    avatar_url: str | None


@dataclass(frozen=True)
class ProfileChanges:
    name: str | None = None
    phone: str | None = None
    city: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    bio: str | None = None
    avatar_upload_id: UUID | None = None
    cover_upload_id: UUID | None = None
    fields_set: frozenset[str] = frozenset()


class IdentityService:
    def __init__(
        self,
        users: UserRepository,
        resets: ResetTokenRepository,
        passwords: Passwords,
        tokens: Tokens,
        media: MediaService,
        events: EventSink,
    ) -> None:
        self.users, self.resets, self.passwords, self.tokens = users, resets, passwords, tokens
        self.media, self.events = media, events

    # ── auth ──
    def register(self, email: str, password: str, name: str, phone: str | None, city: str | None) -> User:
        email = normalize_email(email)
        check_password(password)
        if self.users.by_email(email):
            raise Conflict("An account with this e-mail already exists", "email_taken")
        user = User(
            id=uuid4(), email=email, name=clean_name(name), password_hash=self.passwords.hash(password),
            phone=clean_phone(phone), city=(city or "").strip()[:80] or None,
        )
        self.users.add(user)
        return user

    def login(self, email: str, password: str) -> User:
        try:
            user = self.users.by_email(normalize_email(email))
        except Invalid:
            user = None
        if user is None or not self.passwords.verify(user.password_hash, password):
            raise Unauthorized("Wrong e-mail or password", "bad_credentials")
        if not user.is_active:
            raise Unauthorized("This account is blocked", "blocked")
        return user

    def token_for(self, user: User) -> tuple[str, int]:
        return self.tokens.issue(user.id, user.role, user.token_version)

    def logout(self, principal: Principal) -> None:
        """Revokes every token of the account (v1: revoke the active Passport token)."""
        user = self._get(principal.user_id)
        user.revoke_sessions()
        self.users.save(user)

    def check_principal(self, principal: Principal, token_version: int) -> Principal | None:
        user = self.users.get(principal.user_id)
        if user is None or not user.is_active or user.token_version != token_version:
            return None
        return Principal(user.id, user.role)

    def forgot_password(self, email: str) -> None:
        """Always succeeds (no account enumeration). The worker 'mails' the link."""
        try:
            user = self.users.by_email(normalize_email(email))
        except Invalid:
            return
        if user is None or not user.is_active:
            return
        token, token_hash = self.tokens.reset_token()
        self.resets.add(ResetToken(uuid4(), user.id, token_hash, datetime.now(UTC) + timedelta(hours=1)))
        self.events.add(
            DomainEvent(
                PASSWORD_RESET_REQUESTED,
                {"user_id": str(user.id), "email": user.email, "token": token, "_sensitive": True},
            )
        )

    def reset_password(self, token: str, password: str) -> None:
        check_password(password)
        found = self.resets.by_hash(self.tokens.hash(token))
        now = datetime.now(UTC)
        if found is None or not found.usable(now):
            raise Invalid("This reset link is invalid or expired", "reset_token")
        user = self._get(found.user_id)
        user.password_hash = self.passwords.hash(password)
        user.revoke_sessions()
        self.users.save(user)
        self.resets.mark_used(found.id, now)

    # ── profile ──
    def me(self, principal: Principal) -> User:
        return self._get(principal.user_id)

    def public(self, user_id: UUID) -> User:
        user = self._get(user_id)
        if not user.is_active:
            raise NotFound("User not found")
        return user

    def update_profile(self, principal: Principal, ch: ProfileChanges) -> User:
        user = self._get(principal.user_id)
        f = ch.fields_set
        if "name" in f and ch.name is not None:
            user.name = clean_name(ch.name)
        if "phone" in f:
            user.phone = clean_phone(ch.phone)
        if "city" in f:
            user.city = (ch.city or "").strip()[:80] or None
        if "gender" in f:
            user.gender = clean_gender(ch.gender)
        if "birth_date" in f:
            user.birth_date = clean_birth_date(ch.birth_date, date.today())
        if "bio" in f:
            user.bio = (ch.bio or "").strip()[:500] or None
        old: list[str] = []
        if ch.avatar_upload_id:
            stored = self.media.claim(user.id, [ch.avatar_upload_id], "avatar")[0]
            if user.avatar_key:
                old.append(user.avatar_key)
            user.avatar_key = stored.key
        if ch.cover_upload_id:
            stored = self.media.claim(user.id, [ch.cover_upload_id], "cover")[0]
            if user.cover_key:
                old.append(user.cover_key)
            user.cover_key = stored.key
        self.users.save(user)
        if old:
            self.events.add(DomainEvent(UPLOAD_ORPHANED, {"keys": old}))
        return user

    def avatar_url(self, user: User) -> str | None:
        return self.media.url(user.avatar_key) if user.avatar_key else None

    def cover_url(self, user: User) -> str | None:
        return self.media.url(user.cover_key) if user.cover_key else None

    # ── facade ──
    def summaries(self, ids: list[UUID]) -> dict[str, UserSummary]:
        unique = list({i for i in ids})
        if not unique:
            return {}
        return {
            str(u.id): UserSummary(str(u.id), u.name, u.city, self.avatar_url(u)) for u in self.users.many(unique)
        }

    def list_users(self, q: str | None, page: PageRequest) -> Page[User]:
        items, total = self.users.search(q, page.offset, page.per_page)
        return Page(items, page.page, page.per_page, total)

    def set_active(self, admin: Principal, user_id: UUID, active: bool) -> User:
        if admin.user_id == user_id:
            raise Invalid("You cannot block yourself")
        user = self._get(user_id)
        if active:
            user.is_active = True
        else:
            user.block()
        self.users.save(user)
        return user

    def set_role(self, admin: Principal, user_id: UUID, role: str) -> User:
        if admin.user_id == user_id:
            raise Invalid("You cannot change your own role")
        user = self._get(user_id)
        user.set_role(role)
        self.users.save(user)
        return user

    def _get(self, user_id: UUID) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise NotFound("User not found")
        return user
