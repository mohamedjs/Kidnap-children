from app.modules.geo.domain.geo import ReverseGeocoder, check_point


class GeoService:
    """v1: GET /address/{lat}/{lng}/{lang} (Google, key hard-coded). v2: key from env, off when unset."""

    def __init__(self, geocoder: ReverseGeocoder | None) -> None:
        self.geocoder = geocoder

    def reverse(self, lat: float, lng: float, lang: str) -> str | None:
        lang = check_point(lat, lng, lang)
        return self.geocoder.address(lat, lng, lang) if self.geocoder else None
