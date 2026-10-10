"""
Calculation Service

Helper functions for astrological calculations and data processing.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone as datetime_timezone
import math
import swisseph as swe
from kerykeion.moon_phase_details.utils import configure_ephemeris_path
from kerykeion.utilities import datetime_to_julian, julian_to_datetime
from kerykeion import AstrologicalSubject
from kerykeion.astrological_subject_factory import AstrologicalSubjectFactory
from kerykeion.moon_phase_details.factory import (
    MoonPhaseDetailsFactory,
    SYNODIC_MONTH_DAYS,
)
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
    Get detailed moon phase information using Kerykeion v5 MoonPhaseDetailsFactory.

    Uses precise Swiss Ephemeris calculations via MoonPhaseDetailsFactory for
    phase timings, eclipses, and sun position while preserving the existing
    API response shape for backwards compatibility.

    Args:
        timezone: Timezone string (default: UTC)
        longitude: Longitude for location (default: 0.0)
        latitude: Latitude for location (default: 0.0)

    Returns:
        Dictionary with comprehensive moon phase data (existing shape + optional richer fields)
    """
    try:
        now = datetime.utcnow()

        subject = AstrologicalSubjectFactory.from_birth_data(
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
            online=False,
            suppress_geonames_warning=True,
        )

        overview = MoonPhaseDetailsFactory.from_subject(
            subject,
            using_default_location=(longitude == 0.0 and latitude == 0.0),
        )

        moon_summary = overview.moon
        sun_info = overview.sun

        lunar_phase = subject.lunar_phase
        moon_point = subject.moon
        sun_point = subject.sun

        degrees_between = float(lunar_phase.degrees_between_s_m)
        moon_phase_day = int(lunar_phase.moon_phase)

        illumination = (1 - math.cos(math.radians(degrees_between))) / 2 * 100
        is_waxing = degrees_between < 180

        phase_fraction = degrees_between / 360.0
        age_days_precise = phase_fraction * SYNODIC_MONTH_DAYS
        percent_complete = round(phase_fraction * 100, 1)

        phase_windows = _compute_phase_windows_from_elongation(now, degrees_between)
        next_phase_name, days_until_next = _compute_next_phase_from_windows(phase_windows)

        result: Dict[str, Any] = {
            'timestamp': now.isoformat() + 'Z',
            'location': {
                'longitude': longitude,
                'latitude': latitude,
                'timezone': timezone,
            },
            'phase': {
                'name': moon_summary.phase_name or lunar_phase.moon_phase_name,
                'emoji': lunar_phase.moon_emoji,
                'illumination': round(illumination, 1),
                'is_waxing': is_waxing,
            },
            'age': {
                'days': round(age_days_precise, 2),
                'phase_day': moon_phase_day,
                'synodic_month': SYNODIC_MONTH_DAYS,
                'percent_complete': percent_complete,
            },
            'next_phase': {
                'name': next_phase_name,
                'days_until': round(days_until_next, 1),
            },
            'moon_position': {
                'sign': moon_point.sign,
                'sign_emoji': moon_point.emoji,
                'degree': round(moon_point.position, 2),
                'abs_degree': round(moon_point.abs_pos, 2),
                'element': moon_point.element,
                'quality': moon_point.quality,
            },
            'sun_position': {
                'sign': sun_point.sign,
                'degree': round(sun_point.position, 2),
            },
            'geometry': {
                'elongation': round(degrees_between, 2),
                'sun_phase': 0,
            },
        }

        _enrich_with_optional_fields(result, overview, sun_info, phase_windows)

        return result

    except Exception as e:
        logger.error(f"Error calculating moon phase: {str(e)}")
        raise


def _compute_next_phase_from_windows(phase_windows: Dict[str, Any]) -> tuple:
    phase_names = {
        'new_moon': 'New Moon',
        'first_quarter': 'First Quarter',
        'full_moon': 'Full Moon',
        'last_quarter': 'Last Quarter',
    }
    best_key = None
    best_days = float('inf')

    for key, window in phase_windows.items():
        next_event = window.get('next') if window else None
        days_ahead = next_event.get('days_ahead') if next_event else None
        if days_ahead is not None and 0 < days_ahead < best_days:
            best_days = float(days_ahead)
            best_key = key

    if best_key is None:
        return 'New Moon', SYNODIC_MONTH_DAYS

    return phase_names[best_key], best_days


def _refine_phase_dt(estimate: datetime, target: float) -> datetime:
    """
    Exact moment the Sun-Moon elongation reaches `target`, from a mean-motion
    estimate. The Moon's speed varies by about 20%, so the mean estimate can be
    off by most of a day; Newton steps on Swiss Ephemeris positions converge to
    the second in a few iterations. Falls back to the estimate on failure.
    """
    try:
        iflag = configure_ephemeris_path() | swe.FLG_SPEED
        jd = datetime_to_julian(estimate.astimezone(datetime_timezone.utc))
        for _ in range(8):
            sun = swe.calc_ut(jd, swe.SUN, iflag)[0]
            moon = swe.calc_ut(jd, swe.MOON, iflag)[0]
            diff = ((moon[0] - sun[0] - target + 180.0) % 360.0) - 180.0
            step = diff / (moon[3] - sun[3])
            jd -= step
            if abs(step) < 1.0 / 86400.0:
                break
        return julian_to_datetime(jd).replace(tzinfo=datetime_timezone.utc)
    except Exception:  # pragma: no cover - ephemeris failure keeps the estimate
        logger.warning("Phase refinement failed; using the mean estimate", exc_info=True)
        return estimate


def _compute_phase_windows_from_elongation(now: datetime, degrees_between: float) -> Dict[str, Any]:
    if now.tzinfo is None:
        base_dt = now.replace(tzinfo=datetime_timezone.utc)
    else:
        base_dt = now.astimezone(datetime_timezone.utc)

    phase_targets = {
        'new_moon': 0.0,
        'first_quarter': 90.0,
        'full_moon': 180.0,
        'last_quarter': 270.0,
    }

    windows = {}
    for key, target in phase_targets.items():
        days_since = ((degrees_between - target) % 360.0) / 360.0 * SYNODIC_MONTH_DAYS
        days_until = ((target - degrees_between) % 360.0) / 360.0 * SYNODIC_MONTH_DAYS

        if days_since == 0:
            days_since = SYNODIC_MONTH_DAYS
        if days_until == 0:
            days_until = SYNODIC_MONTH_DAYS

        last_dt = _refine_phase_dt(base_dt - timedelta(days=days_since), target)
        if last_dt >= base_dt:
            last_dt = _refine_phase_dt(last_dt - timedelta(days=SYNODIC_MONTH_DAYS), target)
        next_dt = _refine_phase_dt(base_dt + timedelta(days=days_until), target)
        if next_dt <= base_dt:
            next_dt = _refine_phase_dt(next_dt + timedelta(days=SYNODIC_MONTH_DAYS), target)
        windows[key] = {
            'last': _serialize_phase_event(last_dt, base_dt, is_past=True),
            'next': _serialize_phase_event(next_dt, base_dt, is_past=False),
        }

    return windows


def _serialize_phase_event(event_dt: datetime, reference_dt: datetime, is_past: bool) -> Dict[str, Any]:
    event_dt = event_dt.astimezone(datetime_timezone.utc)
    reference_dt = reference_dt.astimezone(datetime_timezone.utc)
    days_diff = abs((reference_dt - event_dt).total_seconds()) / 86400.0
    event = {
        'timestamp': int(event_dt.timestamp()),
        'datestamp': event_dt.strftime("%a, %d %b %Y %H:%M:%S %z"),
    }
    if is_past:
        event['days_ago'] = int(round(days_diff))
    else:
        event['days_ahead'] = int(round(days_diff))
    return event


def _compute_next_phase(overview) -> tuple:
    """
    Compute the next upcoming major phase and days until it using precise
    Swiss Ephemeris data from the MoonPhaseDetailsFactory overview model.

    Returns:
        (phase_name, days_until) tuple
    """
    detailed = overview.moon.detailed if overview.moon else None
    if detailed is None or detailed.upcoming_phases is None:
        return _compute_next_phase_approx(overview)

    upcoming = detailed.upcoming_phases
    phases = [
        ("New Moon", upcoming.new_moon),
        ("First Quarter", upcoming.first_quarter),
        ("Full Moon", upcoming.full_moon),
        ("Last Quarter", upcoming.last_quarter),
    ]

    best_name = None
    best_days = float('inf')
    for name, window in phases:
        if window is None or window.next is None:
            continue
        days_ahead = window.next.days_ahead
        if days_ahead is not None and 0 < days_ahead < best_days:
            best_days = days_ahead
            best_name = name

    if best_name is not None:
        return best_name, float(best_days)

    return _compute_next_phase_approx(overview)


def _compute_next_phase_approx(overview) -> tuple:
    """
    Fallback: approximate next phase from current phase fraction.
    """
    phase_frac = overview.moon.phase if overview.moon and overview.moon.phase is not None else 0.0
    phase_length = SYNODIC_MONTH_DAYS / 4
    current_index = int(phase_frac * 4) % 4
    next_index = (current_index + 1) % 4
    names = ["New Moon", "First Quarter", "Full Moon", "Last Quarter"]
    days_into = (phase_frac * SYNODIC_MONTH_DAYS) % phase_length
    days_until = phase_length - days_into
    return names[next_index], max(0.1, days_until)


def _enrich_with_optional_fields(
    result: Dict[str, Any],
    overview,
    sun_info,
    phase_windows: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Add optional richer fields from the factory overview to the result dict.
    All fields are additive and optional — existing consumers are unaffected.
    """
    detailed = overview.moon.detailed if overview.moon else None

    if phase_windows is not None:
        result['upcoming_phases'] = phase_windows
    elif detailed is not None and detailed.upcoming_phases is not None:
        up = detailed.upcoming_phases
        result['upcoming_phases'] = {
            'new_moon': _serialize_phase_window(up.new_moon),
            'first_quarter': _serialize_phase_window(up.first_quarter),
            'full_moon': _serialize_phase_window(up.full_moon),
            'last_quarter': _serialize_phase_window(up.last_quarter),
        }

    if sun_info is not None:
        sun_data: Dict[str, Any] = {}
        if sun_info.sunrise is not None:
            sun_data['sunrise'] = sun_info.sunrise
        if sun_info.sunrise_timestamp is not None:
            sun_data['sunrise_time'] = sun_info.sunrise_timestamp
        if sun_info.sunset is not None:
            sun_data['sunset'] = sun_info.sunset
        if sun_info.sunset_timestamp is not None:
            sun_data['sunset_time'] = sun_info.sunset_timestamp
        if sun_info.solar_noon is not None:
            sun_data['solar_noon'] = sun_info.solar_noon
        if sun_info.day_length is not None:
            sun_data['day_length'] = sun_info.day_length
        if sun_info.position is not None:
            sun_data['sky_position'] = {
                'altitude': sun_info.position.altitude,
                'azimuth': sun_info.position.azimuth,
                'distance': sun_info.position.distance,
            }
        if sun_info.next_solar_eclipse is not None:
            eclipse = sun_info.next_solar_eclipse
            result['next_solar_eclipse'] = {
                'timestamp': eclipse.timestamp,
                'datestamp': eclipse.datestamp,
                'type': eclipse.type,
            }
        if sun_data:
            result['sun_info'] = sun_data

    if overview.moon and overview.moon.next_lunar_eclipse is not None:
        eclipse = overview.moon.next_lunar_eclipse
        result['next_lunar_eclipse'] = {
            'timestamp': eclipse.timestamp,
            'datestamp': eclipse.datestamp,
            'type': eclipse.type,
        }


def _serialize_phase_window(window) -> Optional[Dict[str, Any]]:
    """Serialize a MoonPhaseMajorPhaseWindowModel to a plain dict."""
    if window is None:
        return None
    result: Dict[str, Any] = {}
    if window.last is not None:
        result['last'] = {
            'timestamp': window.last.timestamp,
            'datestamp': window.last.datestamp,
            'days_ago': window.last.days_ago,
        }
    if window.next is not None:
        result['next'] = {
            'timestamp': window.next.timestamp,
            'datestamp': window.next.datestamp,
            'days_ahead': window.next.days_ahead,
        }
    return result if result else None


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
