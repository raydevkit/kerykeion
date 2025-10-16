"""
Calculation Service

Helper functions for astrological calculations and data processing.
"""

from typing import Dict, Any
from datetime import datetime
from kerykeion import AstrologicalSubject
from app.schemas.common import SubjectInput
from app.core.config import settings as app_settings
from app.services.kerykeion_service import (
    create_astrological_subject,
    subject_to_dict,
    extract_planet_data,
    extract_house_data,
    extract_aspect_data
)
import logging

logger = logging.getLogger(__name__)


def calculate_birth_data(subject_input: SubjectInput, zodiac_type: str = "Tropic",
                        house_system: str = "P", sidereal_mode: str = None) -> Dict[str, Any]:
    """
    Calculate birth chart data without generating SVG.

    Args:
        subject_input: Birth data input
        zodiac_type: Zodiac type
        house_system: House system
        sidereal_mode: Sidereal mode (if applicable)

    Returns:
        Dictionary with complete birth data
    """
    try:
        # Create AstrologicalSubject
        subject = create_astrological_subject(
            subject_input,
            zodiac_type=zodiac_type,
            house_system=house_system,
            sidereal_mode=sidereal_mode
        )

        # Convert to dictionary
        data = subject_to_dict(subject)

        return data

    except Exception as e:
        logger.error(f"Error calculating birth data: {str(e)}")
        raise


def get_current_sky_positions(timezone: str = "UTC", longitude: float = 0.0, latitude: float = 0.0) -> Dict[str, Any]:
    """
    Get current planetary positions.

    Args:
        timezone: Timezone string (default: UTC)
        longitude: Longitude for location (default: 0.0)
        latitude: Latitude for location (default: 0.0)

    Returns:
        Dictionary with current planetary positions
    """
    try:
        now = datetime.utcnow()

        # Create a subject for the current moment
        current_subject = AstrologicalSubject(
            name="Current Sky",
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            lng=longitude,
            lat=latitude,
            tz_str=timezone,
            city="Sky Position",
            geonames_username=app_settings.GEONAMES_USERNAME
        )

        # Extract planet data
        planets = extract_planet_data(current_subject)

        return {
            'date': now.isoformat() + 'Z',
            'location': {
                'longitude': longitude,
                'latitude': latitude,
                'timezone': timezone
            },
            'planets': {planet['name']: planet for planet in planets}
        }

    except Exception as e:
        logger.error(f"Error calculating current sky: {str(e)}")
        raise


def calculate_element_distribution(subject: AstrologicalSubject) -> Dict[str, int]:
    """
    Calculate element distribution (Fire, Earth, Air, Water).

    Args:
        subject: AstrologicalSubject instance

    Returns:
        Dictionary with element counts
    """
    elements = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}

    planets = extract_planet_data(subject)

    for planet in planets:
        element = planet.get('element', '')
        if element in elements:
            elements[element] += 1

    return elements


def calculate_quality_distribution(subject: AstrologicalSubject) -> Dict[str, int]:
    """
    Calculate quality/modality distribution (Cardinal, Fixed, Mutable).

    Args:
        subject: AstrologicalSubject instance

    Returns:
        Dictionary with quality counts
    """
    qualities = {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}

    planets = extract_planet_data(subject)

    for planet in planets:
        quality = planet.get('quality', '')
        if quality in qualities:
            qualities[quality] += 1

    return qualities


def calculate_aspect_statistics(subject: AstrologicalSubject) -> Dict[str, Any]:
    """
    Calculate aspect statistics.

    Args:
        subject: AstrologicalSubject instance

    Returns:
        Dictionary with aspect statistics
    """
    aspects = extract_aspect_data(subject)

    aspect_types = {}
    for aspect in aspects:
        aspect_type = aspect.get('aspect', 'Unknown')
        if aspect_type not in aspect_types:
            aspect_types[aspect_type] = 0
        aspect_types[aspect_type] += 1

    return {
        'total_aspects': len(aspects),
        'aspect_breakdown': aspect_types,
        'aspects': aspects
    }


def calculate_house_planets(subject: AstrologicalSubject) -> Dict[int, list]:
    """
    Group planets by house.

    Args:
        subject: AstrologicalSubject instance

    Returns:
        Dictionary mapping house numbers to planets in that house
    """
    planets = extract_planet_data(subject)
    house_planets = {i: [] for i in range(1, 13)}

    for planet in planets:
        house = planet.get('house')
        if house and 1 <= house <= 12:
            house_planets[house].append(planet['name'])

    return house_planets


def get_dominant_element(subject: AstrologicalSubject) -> str:
    """
    Get the dominant element.

    Args:
        subject: AstrologicalSubject instance

    Returns:
        Name of dominant element
    """
    elements = calculate_element_distribution(subject)
    return max(elements, key=elements.get)


def get_dominant_quality(subject: AstrologicalSubject) -> str:
    """
    Get the dominant quality/modality.

    Args:
        subject: AstrologicalSubject instance

    Returns:
        Name of dominant quality
    """
    qualities = calculate_quality_distribution(subject)
    return max(qualities, key=qualities.get)
