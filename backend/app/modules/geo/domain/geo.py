from typing import Protocol

from app.shared.domain.errors import Invalid

LANGS = {"ar", "en"}


def check_point(lat: float, lng: float, lang: str) -> str:
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise Invalid("Coordinates are out of range", "location")
    return lang if lang in LANGS else "ar"


class ReverseGeocoder(Protocol):
    def address(self, lat: float, lng: float, lang: str) -> str | None: ...
