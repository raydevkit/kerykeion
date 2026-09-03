"""
Kerykeion Service

Wrapper functions for the Kerykeion astrology library.
Handles creation of AstrologicalSubject instances and data extraction.
"""

from typing import Dict, Any, List, Optional
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    from kerykeion import AstrologicalSubject, SynastryAspects, CompositeSubjectFactory
from app.schemas.common import SubjectInput
from app.core.config import settings as app_settings
from app.utils.validators import normalize_house_system, normalize_zodiac_type
import logging

logger = logging.getLogger(__name__)


def create_astrological_subject(subject_input: SubjectInput, zodiac_type: str = "Tropic",
                                house_system: str = "P", sidereal_mode: Optional[str] = None) -> AstrologicalSubject:
    """
    Create an AstrologicalSubject instance from SubjectInput.

    Uses offline mode (lng/lat/tz_str) to avoid GeoNames API dependency.

    Args:
        subject_input: Pydantic model with birth data
        zodiac_type: "Tropic" (default) or "Sidereal"
        house_system: House system identifier (default "P" for Placidus)
                     P=Placidus, K=Koch, W=Whole Sign, E=Equal, C=Campanus,
                     R=Regiomontanus, O=Porphyrius, M=Morinus
        sidereal_mode: Sidereal mode if using Sidereal zodiac

    Returns:
        AstrologicalSubject instance
    """
    # Normalize inputs
    normalized_zodiac = normalize_zodiac_type(zodiac_type)
    normalized_house_system = normalize_house_system(house_system)

    # Use offline mode with coordinates
    if subject_input.longitude is not None and subject_input.latitude is not None and subject_input.timezone:
        return AstrologicalSubject(
            name=subject_input.name,
            year=subject_input.year,
            month=subject_input.month,
            day=subject_input.day,
            hour=subject_input.hour,
            minute=subject_input.minute,
            lng=subject_input.longitude,
            lat=subject_input.latitude,
            tz_str=subject_input.timezone,
            city=subject_input.city or "Unknown",
            # Label-only in offline mode (lng/lat/tz provided) — without it the
            # library defaults to "GB" and charts render e.g. "Rome, GB".
            nation=subject_input.nation or "GB",
            zodiac_type=normalized_zodiac,
            houses_system_identifier=normalized_house_system,
            sidereal_mode=sidereal_mode,
            geonames_username=app_settings.GEONAMES_USERNAME,
        )
    # Fallback to city/nation lookup (requires GeoNames API)
    elif subject_input.city and subject_input.nation:
        return AstrologicalSubject(
            name=subject_input.name,
            year=subject_input.year,
            month=subject_input.month,
            day=subject_input.day,
            hour=subject_input.hour,
            minute=subject_input.minute,
            city=subject_input.city,
            nation=subject_input.nation,
            zodiac_type=normalized_zodiac,
            houses_system_identifier=normalized_house_system,
            sidereal_mode=sidereal_mode,
            geonames_username=app_settings.GEONAMES_USERNAME,
        )
    else:
        raise ValueError("Must provide either (longitude, latitude, timezone) or (city, nation)")


def extract_planet_data(subject: AstrologicalSubject) -> List[Dict[str, Any]]:
    """
    Extract planet data from AstrologicalSubject.

    Args:
        subject: AstrologicalSubject instance

    Returns:
        List of planet dictionaries
    """
    planets = []

    # Get all planets
    planet_names = [
        'sun', 'moon', 'mercury', 'venus', 'mars',
        'jupiter', 'saturn', 'uranus', 'neptune', 'pluto',
        'mean_node', 'true_node', 'chiron'
    ]

    for planet_name in planet_names:
        planet_obj = getattr(subject, planet_name, None)
        if planet_obj:
            planets.append({
                'name': planet_obj.get('name', planet_name.capitalize()),
                'sign': planet_obj.get('sign', ''),
                'position': planet_obj.get('position', 0.0),
                'abs_pos': planet_obj.get('abs_pos', 0.0),
                'house': planet_obj.get('house', None),
                'retrograde': planet_obj.get('retrograde', False),
                'element': planet_obj.get('element', ''),
                'quality': planet_obj.get('quality', ''),
            })

    return planets


def extract_house_data(subject: AstrologicalSubject) -> List[Dict[str, Any]]:
    """
    Extract house data from AstrologicalSubject.

    Args:
        subject: AstrologicalSubject instance

    Returns:
        List of house dictionaries
    """
    houses = []

    # Get all 12 houses
    house_names = [
        'first_house', 'second_house', 'third_house', 'fourth_house',
        'fifth_house', 'sixth_house', 'seventh_house', 'eighth_house',
        'ninth_house', 'tenth_house', 'eleventh_house', 'twelfth_house'
    ]

    for i, house_name in enumerate(house_names, start=1):
        house_obj = getattr(subject, house_name, None)
        if house_obj:
            houses.append({
                'number': i,
                'name': house_obj.get('name', f'House {i}'),
                'sign': house_obj.get('sign', ''),
                'position': house_obj.get('position', 0.0),
                'abs_pos': house_obj.get('abs_pos', 0.0),
            })

    return houses


def extract_aspect_data(subject: AstrologicalSubject) -> List[Dict[str, Any]]:
    """
    Extract aspect data from AstrologicalSubject.

    Args:
        subject: AstrologicalSubject instance

    Returns:
        List of aspect dictionaries
    """
    aspects = []

    if hasattr(subject, 'aspects_list'):
        for aspect in subject.aspects_list:
            aspects.append({
                'planet1': aspect.get('p1_name', ''),
                'planet2': aspect.get('p2_name', ''),
                'aspect': aspect.get('aspect', ''),
                'angle': aspect.get('aspect_degrees', 0.0),
                'orb': aspect.get('orbit', 0.0),
                'is_active': aspect.get('aid', 0) > 0,
            })

    return aspects


def get_synastry_aspects(subject_one: AstrologicalSubject, subject_two: AstrologicalSubject) -> List[Dict[str, Any]]:
    """
    Calculate synastry aspects between two subjects.

    Args:
        subject_one: First AstrologicalSubject
        subject_two: Second AstrologicalSubject

    Returns:
        List of synastry aspect dictionaries
    """
    synastry = SynastryAspects(subject_one, subject_two)
    aspects_list = synastry.all_aspects  # Use all_aspects property instead of get_relevant_aspects()

    formatted_aspects = []
    for aspect in aspects_list:
        # Handle both dict and AspectModel objects
        if hasattr(aspect, 'model_dump'):
            aspect_dict = aspect.model_dump()
        elif hasattr(aspect, 'dict'):
            aspect_dict = aspect.dict()
        else:
            aspect_dict = aspect

        formatted_aspects.append({
            'planet1': aspect_dict.get('p1_name', ''),
            'planet1_owner': subject_one.name,
            'planet2': aspect_dict.get('p2_name', ''),
            'planet2_owner': subject_two.name,
            'aspect': aspect_dict.get('aspect', ''),
            'angle': aspect_dict.get('aspect_degrees', 0.0),
            'orb': aspect_dict.get('orbit', 0.0),
            'color': aspect_dict.get('color', ''),
        })

    return formatted_aspects


def create_composite_subject(subject_one: AstrologicalSubject, subject_two: AstrologicalSubject) -> AstrologicalSubject:
    """
    Create a composite chart subject from two subjects.

    Args:
        subject_one: First AstrologicalSubject
        subject_two: Second AstrologicalSubject

    Returns:
        Composite AstrologicalSubject
    """
    factory = CompositeSubjectFactory(subject_one, subject_two)
    composite = factory.get_midpoint_composite_subject_model()
    return composite


def subject_to_dict(subject: AstrologicalSubject) -> Dict[str, Any]:
    """
    Convert AstrologicalSubject to dictionary format.
    Handles both regular AstrologicalSubject and CompositeSubjectModel.

    Args:
        subject: AstrologicalSubject or CompositeSubjectModel instance

    Returns:
        Dictionary representation of the subject
    """
    # Helper function to convert Pydantic models to dicts
    def to_dict(obj):
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        elif hasattr(obj, 'dict'):
            return obj.dict()
        elif isinstance(obj, dict):
            return obj
        else:
            return obj

    # Check if this is a CompositeSubjectModel (doesn't have year/month/day directly)
    is_composite = hasattr(subject, 'composite_chart_type')

    result = {
        'name': subject.name,
        'sun': to_dict(subject.sun),
        'moon': to_dict(subject.moon),
        'mercury': to_dict(subject.mercury),
        'venus': to_dict(subject.venus),
        'mars': to_dict(subject.mars),
        'jupiter': to_dict(subject.jupiter),
        'saturn': to_dict(subject.saturn),
        'uranus': to_dict(subject.uranus),
        'neptune': to_dict(subject.neptune),
        'pluto': to_dict(subject.pluto),
        'planets': extract_planet_data(subject),
        'houses': extract_house_data(subject),
        'aspects': extract_aspect_data(subject),
    }

    # Add optional planets if they exist
    if hasattr(subject, 'mean_node') and subject.mean_node:
        result['mean_node'] = to_dict(subject.mean_node)
    if hasattr(subject, 'true_node') and subject.true_node:
        result['true_node'] = to_dict(subject.true_node)
    if hasattr(subject, 'chiron') and subject.chiron:
        result['chiron'] = to_dict(subject.chiron)

    # Add date/location info only for regular subjects (not composite)
    if not is_composite:
        result['date'] = {
            'year': subject.year,
            'month': subject.month,
            'day': subject.day,
            'hour': subject.hour,
            'minute': subject.minute,
        }
        result['location'] = {
            'city': subject.city,
            'nation': subject.nation if hasattr(subject, 'nation') else None,
            'longitude': subject.lng if hasattr(subject, 'lng') else None,
            'latitude': subject.lat if hasattr(subject, 'lat') else None,
            'timezone': subject.tz_str if hasattr(subject, 'tz_str') else None,
        }
    else:
        # For composite charts, include info about both subjects
        result['composite_chart_type'] = subject.composite_chart_type
        result['first_subject_name'] = subject.first_subject.name if hasattr(subject, 'first_subject') else None
        result['second_subject_name'] = subject.second_subject.name if hasattr(subject, 'second_subject') else None

    return result
