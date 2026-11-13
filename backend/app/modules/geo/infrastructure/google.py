import logging

import httpx

from app.modules.geo.application.service import GeoService
from app.modules.geo.domain.geo import ReverseGeocoder
from app.shared.infrastructure.config import get_settings

log = logging.getLogger("geo")


class GoogleGeocoder(ReverseGeocoder):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def address(self, lat: float, lng: float, lang: str) -> str | None:
        try:
            res = httpx.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"latlng": f"{lat},{lng}", "language": lang, "key": self.api_key},
                timeout=5,
            )
            data = res.json()
        except (httpx.HTTPError, ValueError) as e:
            log.warning("geocoding failed: %s", e)
            return None
        if data.get("status") != "OK" or not data.get("results"):
            return None
        return str(data["results"][0].get("formatted_address") or "") or None


def geo_service() -> GeoService:
    key = get_settings().google_maps_api_key
    return GeoService(GoogleGeocoder(key) if key else None)
