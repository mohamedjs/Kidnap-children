from typing import Protocol
from uuid import UUID


class Passwords(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password_hash: str, password: str) -> bool: ...


class Tokens(Protocol):
    def issue(self, user_id: UUID, role: str, token_version: int) -> tuple[str, int]: ...

    def reset_token(self) -> tuple[str, str]:
        """(token sent to the user, hash stored)."""
        ...

    def hash(self, token: str) -> str: ...
