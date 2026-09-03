"""Transit Chart Endpoints"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from app.core.security import verify_api_key
from app.schemas.requests import TransitRequest
from app.schemas.responses import TransitChartResponse
from app.services.kerykeion_service import create_astrological_subject, get_synastry_aspects
from app.services.chart_service import generate_transit_chart_svg

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chart", response_model=TransitChartResponse)
async def generate_transit_chart(
    request: TransitRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Generate transit chart with SVG visualization.

    Shows current planetary transits overlaid on the natal chart.
    """
    try:
        # Create natal subject
        natal_subject = create_astrological_subject(
            request.subject,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        # Create transit subject (current date/time)
        transit_subject = create_astrological_subject(
            request.transit_date,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        # Generate SVG chart
        svg_content = generate_transit_chart_svg(
            natal_subject,
            transit_subject,
            theme=request.config.theme,
            language=request.config.language,
            style=request.config.style,
        )

        # Get transit aspects
        transit_aspects = get_synastry_aspects(natal_subject, transit_subject)

        return TransitChartResponse(
            svg=svg_content,
            transit_aspects=transit_aspects
        )

    except ValueError as e:
        logger.error(f"Validation error in transit chart generation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception:
        logger.exception("Error generating transit chart")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "GENERATION_FAILED",
                "message": "Failed to generate transit chart",
                "details": {}
            }
        )


@router.post("/data")
async def get_transit_data(
    request: TransitRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Get transit data only (no SVG) - faster response.

    Returns transit aspects without generating a chart visualization.
    """
    try:
        # Create natal subject
        natal_subject = create_astrological_subject(
            request.subject,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        # Create transit subject
        transit_subject = create_astrological_subject(
            request.transit_date,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        # Get transit aspects
        transit_aspects = get_synastry_aspects(natal_subject, transit_subject)

        return {
            "natal_subject": request.subject.name,
            "transit_date": request.transit_date.name,
            "transit_aspects": transit_aspects,
            "aspect_count": len(transit_aspects)
        }

    except ValueError as e:
        logger.error(f"Validation error in transit data calculation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception:
        logger.exception("Error calculating transit data")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": "Failed to calculate transit data",
                "details": {}
            }
        )
