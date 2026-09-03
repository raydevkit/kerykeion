"""Relationship Compatibility Score Endpoint"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from app.core.security import verify_api_key
from app.schemas.requests import SynastryRequest
from app.schemas.responses import RelationshipScoreResponse
from app.services.kerykeion_service import create_astrological_subject
from app.services.relationship_service import calculate_relationship_score

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/score", response_model=RelationshipScoreResponse)
async def calculate_compatibility_score(
    request: SynastryRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Calculate compatibility score between two birth charts.

    Analyzes synastry aspects and returns a comprehensive compatibility
    score with breakdown by category (emotional, communication, love, etc.).
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

        # Calculate relationship score
        score_data = calculate_relationship_score(subject_one, subject_two)

        return RelationshipScoreResponse(
            score=int(score_data['score']),
            max_score=int(score_data['max_score']),
            percentage=score_data['percentage'],
            rating=score_data['rating'],
            breakdown=score_data['breakdown']
        )

    except ValueError as e:
        logger.error(f"Validation error in relationship score calculation: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_INPUT",
                "message": str(e),
                "details": {}
            }
        )
    except Exception:
        logger.exception("Error calculating relationship score")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": "Failed to calculate relationship score",
                "details": {}
            }
        )
