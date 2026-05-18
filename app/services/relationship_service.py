"""
Relationship Service

Handles relationship compatibility scoring based on synastry aspects.
"""

from typing import Dict, Any, List
from kerykeion import AstrologicalSubject
from app.services.kerykeion_service import get_synastry_aspects
import logging

logger = logging.getLogger(__name__)


# Aspect scoring weights (positive = harmonious, negative = challenging)
ASPECT_SCORES = {
    'conjunction': 10,      # Very strong connection
    'sextile': 8,           # Harmonious, easy flow
    'trine': 10,            # Very harmonious, natural compatibility
    'square': -5,           # Challenging, growth-oriented
    'opposition': -3,       # Tension, needs balance
    'quincunx': -2,         # Adjustment needed
}

# Planet importance weights for relationship scoring
PLANET_WEIGHTS = {
    'Sun': 3.0,             # Identity, ego, vitality
    'Moon': 3.0,            # Emotions, comfort, security
    'Venus': 2.5,           # Love, affection, values
    'Mars': 2.0,            # Passion, action, drive
    'Mercury': 1.5,         # Communication, thinking
    'Jupiter': 1.5,         # Growth, optimism, expansion
    'Saturn': 1.5,          # Commitment, responsibility
    'Uranus': 1.0,          # Change, excitement, independence
    'Neptune': 1.0,         # Dreams, spirituality, illusion
    'Pluto': 1.0,           # Transformation, intensity
    'Chiron': 0.5,          # Healing, wounds
    'Mean_Node': 0.5,       # Karma, destiny
    'True_Node': 0.5,       # Karma, destiny
}


def calculate_relationship_score(subject_one: AstrologicalSubject, subject_two: AstrologicalSubject) -> Dict[str, Any]:
    """
    Calculate comprehensive relationship compatibility score.

    Args:
        subject_one: First person's AstrologicalSubject
        subject_two: Second person's AstrologicalSubject

    Returns:
        Dictionary with score, percentage, rating, and breakdown
    """
    try:
        # Get synastry aspects
        aspects = get_synastry_aspects(subject_one, subject_two)

        # Calculate weighted scores
        total_score = 0
        max_possible_score = 0
        category_scores = {
            'emotional': 0,      # Sun, Moon
            'communication': 0,  # Mercury
            'love': 0,           # Venus
            'passion': 0,        # Mars
            'growth': 0,         # Jupiter, Saturn
            'spiritual': 0,      # Neptune, Pluto, Chiron
        }
        category_max_scores = {
            'emotional': 0,
            'communication': 0,
            'love': 0,
            'passion': 0,
            'growth': 0,
            'spiritual': 0,
        }

        for aspect in aspects:
            aspect_type = aspect.get('aspect', '').lower()
            planet1 = aspect.get('planet1', '')
            planet2 = aspect.get('planet2', '')

            # Get aspect score
            aspect_score = ASPECT_SCORES.get(aspect_type, 0)

            # Get planet weights
            weight1 = PLANET_WEIGHTS.get(planet1, 0.5)
            weight2 = PLANET_WEIGHTS.get(planet2, 0.5)
            avg_weight = (weight1 + weight2) / 2

            # Calculate weighted score
            weighted_score = aspect_score * avg_weight

            total_score += weighted_score
            max_possible_score += abs(10 * avg_weight)  # Max possible for this aspect

            # Categorize score
            category = _categorize_aspect(planet1, planet2)
            if category:
                category_scores[category] += weighted_score
                category_max_scores[category] += abs(10 * avg_weight)

        # Normalize to 0-100 scale
        if max_possible_score > 0:
            percentage = max(0, min(100, ((total_score / max_possible_score) * 50) + 50))
        else:
            percentage = 50.0  # Neutral if no aspects

        # Get rating description
        rating = _get_compatibility_rating(percentage)

        # Normalize category scores using per-category denominator
        normalized_categories = {}
        for category, score in category_scores.items():
            cat_max = category_max_scores[category]
            if cat_max > 0:
                normalized_score = max(0, min(100, ((score / cat_max) * 50) + 50))
            else:
                normalized_score = 50.0
            normalized_categories[category] = round(normalized_score, 1)

        return {
            'score': round(total_score, 2),
            'max_score': round(max_possible_score, 2),
            'percentage': round(percentage, 1),
            'rating': rating,
            'breakdown': normalized_categories,
            'aspect_count': len(aspects),
            'harmonious_aspects': len([a for a in aspects if ASPECT_SCORES.get(a.get('aspect', '').lower(), 0) > 0]),
            'challenging_aspects': len([a for a in aspects if ASPECT_SCORES.get(a.get('aspect', '').lower(), 0) < 0]),
        }

    except Exception as e:
        logger.error(f"Error calculating relationship score: {str(e)}")
        raise


def _categorize_aspect(planet1: str, planet2: str) -> str:
    """
    Categorize an aspect by planetary combination.

    Args:
        planet1: First planet name
        planet2: Second planet name

    Returns:
        Category name
    """
    planets = {planet1.lower(), planet2.lower()}

    # Emotional (Sun, Moon)
    if planets & {'sun', 'moon'}:
        return 'emotional'

    # Communication (Mercury)
    if 'mercury' in planets:
        return 'communication'

    # Love (Venus)
    if 'venus' in planets:
        return 'love'

    # Passion (Mars)
    if 'mars' in planets:
        return 'passion'

    # Growth (Jupiter, Saturn)
    if planets & {'jupiter', 'saturn'}:
        return 'growth'

    # Spiritual (Neptune, Pluto, Chiron)
    if planets & {'neptune', 'pluto', 'chiron'}:
        return 'spiritual'

    return 'growth'  # Default category


def _get_compatibility_rating(percentage: float) -> str:
    """
    Get compatibility rating description based on percentage.

    Args:
        percentage: Compatibility percentage (0-100)

    Returns:
        Rating description
    """
    if percentage >= 85:
        return "Excellent - Highly Compatible"
    elif percentage >= 70:
        return "Very Good - Strong Compatibility"
    elif percentage >= 55:
        return "Good - Compatible with Growth Potential"
    elif percentage >= 40:
        return "Moderate - Requires Effort and Understanding"
    elif percentage >= 25:
        return "Challenging - Significant Work Needed"
    else:
        return "Difficult - Major Challenges"


def get_key_synastry_aspects(subject_one: AstrologicalSubject, subject_two: AstrologicalSubject,
                             limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the most significant synastry aspects.

    Args:
        subject_one: First person's AstrologicalSubject
        subject_two: Second person's AstrologicalSubject
        limit: Maximum number of aspects to return

    Returns:
        List of most significant aspect dictionaries
    """
    aspects = get_synastry_aspects(subject_one, subject_two)

    # Score each aspect by importance
    scored_aspects = []
    for aspect in aspects:
        aspect_type = aspect.get('aspect', '').lower()
        planet1 = aspect.get('planet1', '')
        planet2 = aspect.get('planet2', '')

        # Calculate importance score
        aspect_score = abs(ASPECT_SCORES.get(aspect_type, 0))
        weight1 = PLANET_WEIGHTS.get(planet1, 0.5)
        weight2 = PLANET_WEIGHTS.get(planet2, 0.5)
        importance = aspect_score * ((weight1 + weight2) / 2)

        scored_aspects.append({
            **aspect,
            'importance': importance
        })

    # Sort by importance and return top N
    scored_aspects.sort(key=lambda x: x['importance'], reverse=True)
    return scored_aspects[:limit]


def analyze_relationship_strengths_weaknesses(subject_one: AstrologicalSubject,
                                               subject_two: AstrologicalSubject) -> Dict[str, List[str]]:
    """
    Analyze relationship strengths and weaknesses.

    Args:
        subject_one: First person's AstrologicalSubject
        subject_two: Second person's AstrologicalSubject

    Returns:
        Dictionary with 'strengths' and 'weaknesses' lists
    """
    aspects = get_synastry_aspects(subject_one, subject_two)

    strengths = []
    weaknesses = []

    for aspect in aspects:
        aspect_type = aspect.get('aspect', '').lower()
        planet1 = aspect.get('planet1', '')
        planet2 = aspect.get('planet2', '')
        aspect_score = ASPECT_SCORES.get(aspect_type, 0)

        description = f"{planet1}-{planet2} {aspect_type}"

        if aspect_score > 5:
            strengths.append(description)
        elif aspect_score < -2:
            weaknesses.append(description)

    return {
        'strengths': strengths[:10],  # Top 10 strengths
        'weaknesses': weaknesses[:10]  # Top 10 weaknesses
    }
