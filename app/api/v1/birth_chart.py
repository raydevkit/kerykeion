"""
Birth Chart Endpoints

Handles birth chart generation requests.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.core.security import verify_api_key
from app.schemas.requests import BirthChartRequest
from app.schemas.responses import BirthChartResponse, BirthDataResponse
from app.services.kerykeion_service import create_astrological_subject, subject_to_dict
from app.services.chart_service import generate_birth_chart_svg
from app.services.calculation_service import calculate_birth_data

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chart", response_model=BirthChartResponse)
async def generate_birth_chart(
    request: BirthChartRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Generate a complete birth chart with SVG visualization.

    Returns birth chart data along with an SVG visualization of the chart.
    This endpoint is more resource-intensive due to SVG generation.
    """
    try:
        # Create AstrologicalSubject
        subject = create_astrological_subject(
            request.subject,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        # Generate SVG chart
        svg_content = generate_birth_chart_svg(
            subject,
            theme=request.config.theme,
            language=request.config.language,
            style=request.config.style,
        )

        # Get chart data
        chart_data = subject_to_dict(subject)

        return BirthChartResponse(
            svg=svg_content,
            data=chart_data
        )

    except ValueError as e:
        logger.error(f"Validation error in birth chart generation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error(f"Error generating birth chart: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "GENERATION_FAILED",
                "message": "Failed to generate birth chart",
                "details": {"error": str(e)}
            }
        )


@router.post("/data", response_model=BirthDataResponse)
async def get_birth_data(
    request: BirthChartRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Get birth chart data only (no SVG) - faster response.

    Returns only the calculated astrological data without generating
    an SVG chart. Use this endpoint when you only need the data
    or want faster response times.
    """
    try:
        # Calculate birth data
        data = calculate_birth_data(
            request.subject,
            zodiac_type=request.config.zodiac_type,
            house_system=request.config.house_system,
            sidereal_mode=request.config.sidereal_mode
        )

        return BirthDataResponse(
            name=data['name'],
            sun=data['sun'],
            moon=data['moon'],
            planets=data['planets'],
            houses=data['houses'],
            aspects=data['aspects']
        )

    except ValueError as e:
        logger.error(f"Validation error in birth data calculation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error(f"Error calculating birth data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": "Failed to calculate birth data",
                "details": {"error": str(e)}
            }
        )
