from typing import Any

from fastapi import APIRouter

from app.modules.geo.infrastructure.google import geo_service
from app.shared.presentation.auth import CurrentPrincipal
from app.shared.presentation.http import ok

router = APIRouter(tags=["geo"])


@router.get("/api/geo/reverse")
def reverse(lat: float, lng: float, _: CurrentPrincipal, lang: str = "ar") -> dict[str, Any]:
    """Address for a map pin; `address` is null when no geocoder is configured."""
    svc = geo_service()
    return ok({"address": svc.reverse(lat, lng, lang), "enabled": svc.geocoder is not None})
