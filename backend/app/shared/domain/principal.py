from dataclasses import dataclass
from uuid import UUID

ROLE_USER = "user"
ROLE_ADMIN = "admin"


@dataclass(frozen=True)
class Principal:
    """Who is calling. Built from a verified access token."""

    user_id: UUID
    role: str = ROLE_USER

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN
