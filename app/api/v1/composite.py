"""Composite Chart Endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.core.security import verify_api_key
from app.schemas.requests import CompositeRequest
from app.schemas.responses import CompositeChartResponse
from app.services.kerykeion_service import create_astrological_subject, create_composite_subject, subject_to_dict
from app.services.chart_service import generate_composite_chart_svg

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chart", response_model=CompositeChartResponse)
async def generate_composite_chart(
    request: CompositeRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Generate composite chart with SVG visualization.

    Creates a midpoint composite chart representing the relationship
    between two people as a single entity.
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

        # Create composite subject
        composite_subject = create_composite_subject(subject_one, subject_two)

        # Generate SVG chart
        svg_content = generate_composite_chart_svg(
            composite_subject,
            theme=request.config.theme,
            language=request.config.language
        )

        # Get composite data
        composite_data = subject_to_dict(composite_subject)

        return CompositeChartResponse(
            svg=svg_content,
            composite_data=composite_data
        )

    except ValueError as e:
        logger.error(f"Validation error in composite chart generation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error(f"Error generating composite chart: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "GENERATION_FAILED",
                "message": "Failed to generate composite chart",
                "details": {"error": str(e)}
            }
        )


@router.post("/data")
async def get_composite_data(
    request: CompositeRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Get composite chart data only (no SVG) - faster response.

    Returns composite chart data without generating a visualization.
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

        # Create composite subject
        composite_subject = create_composite_subject(subject_one, subject_two)

        # Get composite data
        composite_data = subject_to_dict(composite_subject)

        return {
            "subject_one": request.subject_one.name,
            "subject_two": request.subject_two.name,
            "composite_data": composite_data
        }

    except ValueError as e:
        logger.error(f"Validation error in composite data calculation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error(f"Error calculating composite data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": "Failed to calculate composite data",
                "details": {"error": str(e)}
            }
        )
