"""Current Sky (Planetary Positions) Endpoint"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
import logging

from app.core.security import verify_api_key
from app.schemas.responses import CurrentSkyResponse
from app.services.calculation_service import get_current_sky_positions

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

    Returns the current positions of all planets in the sky
    for a given location and timezone.
    """
    try:
        sky_data = get_current_sky_positions(
            timezone=timezone,
            longitude=longitude,
            latitude=latitude
        )

        return CurrentSkyResponse(
            date=sky_data['date'],
            planets=sky_data['planets']
        )

    except Exception as e:
        logger.error(f"Error calculating current sky positions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": "Failed to calculate current sky positions",
                "details": {"error": str(e)}
            }
        )
