"""
Calculation Service

Helper functions for astrological calculations and data processing.
"""

from typing import Dict, Any
from datetime import datetime
import math
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
        Dictionary with current planetary positions, moon phase, and houses
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

        # Extract planet data as individual planets (matching birth chart format)
        planets_data = {}
        planet_names = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                       'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        
        for planet_name in planet_names:
            planet_obj = getattr(current_subject, planet_name, None)
            if planet_obj:
                planets_data[planet_name] = {
                    'name': planet_obj.get('name', planet_name.capitalize()),
                    'sign': planet_obj.get('sign', ''),
                    'position': planet_obj.get('position', 0.0),
                    'abs_pos': planet_obj.get('abs_pos', 0.0),
                    'house': planet_obj.get('house', None),
                    'retrograde': planet_obj.get('retrograde', False),
                    'element': planet_obj.get('element', ''),
                    'quality': planet_obj.get('quality', ''),
                }

        # Extract house data
        houses = extract_house_data(current_subject)

        # Extract lunar phase
        lunar_phase = None
        if hasattr(current_subject, 'lunar_phase') and current_subject.lunar_phase:
            lp = current_subject.lunar_phase
            moon_phase_day = lp.get('moon_phase', 0)
            degrees_between = lp.get('degrees_between_s_m', 0)
            
            # Calculate illumination using the correct formula based on elongation angle
            # illumination = (1 - cos(elongation)) / 2 * 100
            # This gives: 0° = 0%, 90° = 50%, 180° = 100%
            illumination = (1 - math.cos(math.radians(degrees_between))) / 2 * 100
            
            lunar_phase = {
                'name': lp.get('moon_phase_name', ''),
                'emoji': lp.get('moon_emoji', ''),
                'day': moon_phase_day,
                'illumination': round(illumination, 1),
                'degrees_between_sun_moon': degrees_between,
            }

        return {
            'date': now.isoformat() + 'Z',
            'location': {
                'longitude': longitude,
                'latitude': latitude,
                'timezone': timezone
            },
            **planets_data,  # Spread planets as individual properties
            'houses': houses,
            'lunar_phase': lunar_phase,
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


def get_detailed_moon_phase(timezone: str = "UTC", longitude: float = 0.0, latitude: float = 0.0) -> Dict[str, Any]:
    """
    Get detailed moon phase information.
    
    Args:
        timezone: Timezone string (default: UTC)
        longitude: Longitude for location (default: 0.0)
        latitude: Latitude for location (default: 0.0)
        
    Returns:
        Dictionary with comprehensive moon phase data
    """
    try:
        now = datetime.utcnow()
        
        # Create a subject for the current moment
        current_subject = AstrologicalSubject(
            name="Moon Phase",
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            lng=longitude,
            lat=latitude,
            tz_str=timezone,
            city="Moon Phase",
            geonames_username=app_settings.GEONAMES_USERNAME
        )
        
        # Get lunar phase data
        lp = current_subject.lunar_phase
        moon = current_subject.moon
        sun = current_subject.sun
        
        # Calculate values
        degrees_between = lp.get('degrees_between_s_m', 0)
        moon_phase_day = lp.get('moon_phase', 0)
        
        # Calculate illumination using cosine formula
        illumination = (1 - math.cos(math.radians(degrees_between))) / 2 * 100
        
        # Calculate moon age with decimal precision
        synodic_month = 29.53059  # Average synodic month in days
        moon_age = degrees_between / 360 * synodic_month
        
        # Determine if waxing or waning
        is_waxing = degrees_between < 180
        
        # Calculate days until next phase
        # Each major phase is ~7.38 days apart
        phase_length = synodic_month / 4
        days_into_current_phase = moon_age % phase_length
        days_until_next_phase = phase_length - days_into_current_phase
        
        # Determine next phase
        phase_names = ['New Moon', 'First Quarter', 'Full Moon', 'Last Quarter']
        current_phase_index = int(moon_age / phase_length) % 4
        next_phase_index = (current_phase_index + 1) % 4
        next_phase = phase_names[next_phase_index]
        
        # Moon sign data
        moon_sign = moon.get('sign', '')
        moon_position = moon.get('position', 0)
        moon_abs_pos = moon.get('abs_pos', 0)
        moon_element = moon.get('element', '')
        moon_quality = moon.get('quality', '')
        
        # Sun position for reference
        sun_sign = sun.get('sign', '')
        sun_position = sun.get('position', 0)
        
        return {
            'timestamp': now.isoformat() + 'Z',
            'location': {
                'longitude': longitude,
                'latitude': latitude,
                'timezone': timezone
            },
            'phase': {
                'name': lp.get('moon_phase_name', ''),
                'emoji': lp.get('moon_emoji', ''),
                'illumination': round(illumination, 1),
                'is_waxing': is_waxing,
            },
            'age': {
                'days': round(moon_age, 2),
                'phase_day': moon_phase_day,
                'synodic_month': synodic_month,
                'percent_complete': round((moon_age / synodic_month) * 100, 1),
            },
            'next_phase': {
                'name': next_phase,
                'days_until': round(days_until_next_phase, 1),
            },
            'moon_position': {
                'sign': moon_sign,
                'sign_emoji': moon.get('emoji', ''),
                'degree': round(moon_position, 2),
                'abs_degree': round(moon_abs_pos, 2),
                'element': moon_element,
                'quality': moon_quality,
            },
            'sun_position': {
                'sign': sun_sign,
                'degree': round(sun_position, 2),
            },
            'geometry': {
                'elongation': round(degrees_between, 2),
                'sun_phase': lp.get('sun_phase', 0),
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating moon phase: {str(e)}")
        raise


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
