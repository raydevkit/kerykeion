"""Synastry (Relationship Compatibility) Endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.core.security import verify_api_key
from app.schemas.requests import SynastryRequest
from app.schemas.responses import SynastryChartResponse, SynastryDataResponse
from app.services.kerykeion_service import create_astrological_subject, get_synastry_aspects, subject_to_dict
from app.services.chart_service import generate_synastry_chart_svg

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chart", response_model=SynastryChartResponse)
async def generate_synastry_chart(
    request: SynastryRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Generate synastry chart with SVG visualization.

    Analyzes the astrological compatibility between two people
    and returns a visual chart showing their planetary aspects.
    """
    try:
        # Create both subjects
        subject_one = create_astrological_subject(
            request.subject_one,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        subject_two = create_astrological_subject(
            request.subject_two,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        # Generate SVG chart
        svg_content = generate_synastry_chart_svg(
            subject_one,
            subject_two,
            theme=request.config.theme,
            language=request.config.language,
            style=request.config.style,
        )

        # Get synastry aspects
        aspects = get_synastry_aspects(subject_one, subject_two)

        # Convert subjects to dict for response
        subject_one_data = subject_to_dict(subject_one)
        subject_two_data = subject_to_dict(subject_two)

        return SynastryChartResponse(
            svg=svg_content,
            data=SynastryDataResponse(
                subject_one_chart=subject_one_data,
                subject_two_chart=subject_two_data,
                aspects=aspects
            )
        )

    except ValueError as e:
        logger.error(f"Validation error in synastry chart generation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error(f"Error generating synastry chart: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "GENERATION_FAILED",
                "message": "Failed to generate synastry chart",
                "details": {"error": str(e)}
            }
        )


@router.post("/data")
async def get_synastry_data(
    request: SynastryRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Get synastry data only (no SVG) - faster response.

    Returns only the aspect data between two charts without
    generating an SVG visualization.
    """
    try:
        # Create both subjects
        subject_one = create_astrological_subject(
            request.subject_one,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        subject_two = create_astrological_subject(
            request.subject_two,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        # Get synastry aspects
        aspects = get_synastry_aspects(subject_one, subject_two)

        return {
            "subject_one": request.subject_one.name,
            "subject_two": request.subject_two.name,
            "aspects": aspects,
            "aspect_count": len(aspects)
        }

    except ValueError as e:
        logger.error(f"Validation error in synastry data calculation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error(f"Error calculating synastry data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": "Failed to calculate synastry data",
                "details": {"error": str(e)}
            }
        )
