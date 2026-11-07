"""Forecast Endpoints: solar return and secondary progressions"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from kerykeion.schemas.kerykeion_exception import KerykeionException

from app.core.security import verify_api_key
from app.schemas.requests import ProgressionsRequest, SolarReturnRequest
from app.schemas.responses import ProgressionsResponse, SolarReturnResponse
from app.services.forecast_service import secondary_progressions, solar_return
from app.services.kerykeion_service import create_astrological_subject

router = APIRouter()
logger = logging.getLogger(__name__)


def _failed(error: str, message: str, status_code: int) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"error": error, "message": message, "details": {}})


@router.post("/return/solar", response_model=SolarReturnResponse)
def generate_solar_return(
    request: SolarReturnRequest,
    api_key: str = Depends(verify_api_key),
):
    """Solar return for the birthday in `year`: the exact moment, the return chart data and its SVG."""
    try:
        natal = create_astrological_subject(
            request.subject,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode,
        )
        return solar_return(
            natal,
            request.year,
            request.location,
            theme=request.config.theme,
            language=request.config.language,
            style=request.config.style,
        )
    except (ValueError, KerykeionException) as e:
        logger.error(f"Validation error in solar return: {str(e)}")
        raise _failed("INVALID_INPUT", str(e), 400)
    except Exception:
        logger.exception("Error generating solar return")
        raise _failed("GENERATION_FAILED", "Failed to generate solar return", 500)


@router.post("/progressions", response_model=ProgressionsResponse)
def generate_progressions(
    request: ProgressionsRequest,
    api_key: str = Depends(verify_api_key),
):
    """Secondary progressions for `target_date`: progressed positions, aspects to natal and a bi-wheel SVG."""
    try:
        natal = create_astrological_subject(
            request.subject,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode,
        )
        return secondary_progressions(
            natal,
            request.target_date,
            theme=request.config.theme,
            language=request.config.language,
            style=request.config.style,
        )
    except (ValueError, KerykeionException) as e:
        logger.error(f"Validation error in progressions: {str(e)}")
        raise _failed("INVALID_INPUT", str(e), 400)
    except Exception:
        logger.exception("Error generating progressions")
        raise _failed("GENERATION_FAILED", "Failed to generate progressions", 500)
