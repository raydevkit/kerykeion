"""Current Sky (Planetary Positions) Endpoint"""

from fastapi import APIRouter, Depends, HTTPException, Query
import logging

from app.core.security import verify_api_key
from app.schemas.responses import CurrentSkyResponse, MoonPhaseResponse
from app.services.calculation_service import get_current_sky_positions, get_detailed_moon_phase

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/now", response_model=CurrentSkyResponse)
async def get_current_sky(
    timezone: str = Query(default="UTC", description="Timezone string (e.g., 'America/New_York')"),
    longitude: float = Query(default=0.0, ge=-180, le=180, description="Longitude"),
    latitude: float = Query(default=0.0, ge=-90, le=90, description="Latitude"),
    api_key: str = Depends(verify_api_key),
):
    """
    Get current planetary positions.

    Returns the current positions of all planets in the sky,
    moon phase, and house cusps for a given location and timezone.
    """
    try:
        sky_data = get_current_sky_positions(
            timezone=timezone,
            longitude=longitude,
            latitude=latitude
        )

        return CurrentSkyResponse(**sky_data)

    except Exception:
        logger.exception("Error calculating current sky positions")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": "Failed to calculate current sky positions",
                "details": {}
            }
        )


@router.get("/moon-phase", response_model=MoonPhaseResponse)
async def get_moon_phase(
    timezone: str = Query(default="UTC", description="Timezone string (e.g., 'America/New_York')"),
    longitude: float = Query(default=0.0, ge=-180, le=180, description="Longitude"),
    latitude: float = Query(default=0.0, ge=-90, le=90, description="Latitude"),
    api_key: str = Depends(verify_api_key),
):
    """
    Get detailed moon phase information.

    Returns comprehensive moon phase data including:
    - Current phase name and illumination
    - Moon age in days
    - Next phase and days until
    - Moon position (sign, degree, element)
    - Sun-Moon geometry
    """
    try:
        moon_data = get_detailed_moon_phase(
            timezone=timezone,
            longitude=longitude,
            latitude=latitude
        )

        return MoonPhaseResponse(**moon_data)

    except Exception:
        logger.exception("Error calculating moon phase")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": "Failed to calculate moon phase",
                "details": {}
            }
        )
