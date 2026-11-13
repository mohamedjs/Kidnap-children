from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class PageRequest:
    page: int = 1
    per_page: int = 15

    @staticmethod
    def of(page: int | None, per_page: int | None, max_per_page: int = 50) -> "PageRequest":
        p = max(1, page or 1)
        n = min(max(1, per_page or 15), max_per_page)
        return PageRequest(p, n)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


@dataclass(frozen=True)
class Page(Generic[T]):
    items: list[T]
    page: int
    per_page: int
    total: int
