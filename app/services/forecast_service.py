"""
Forecast Service

Solar returns (PlanetaryReturnFactory) and secondary progressions (a day after birth for each year of life).
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from kerykeion import AstrologicalSubject
from kerykeion.astrological_subject_factory import AstrologicalSubjectFactory
from kerykeion.chart_data_factory import ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer
from kerykeion.planetary_return_factory import PlanetaryReturnFactory

from app.schemas.requests import ReturnLocation
from app.services.kerykeion_service import SWE_LOCK, get_synastry_aspects, subject_to_dict

# Mean tropical year in days: secondary progressions advance the chart one ephemeris day per year of life.
TROPICAL_YEAR_DAYS = 365.242189


def _drawer_svg(chart_data, theme: str, language: str, style: str, title: Optional[str] = None) -> str:
    drawer = ChartDrawer(chart_data, theme=theme, chart_language=language, style=style, custom_title=title)
    return drawer.generate_svg_string()


def _require_tropical(natal_model) -> None:
    # PlanetaryReturnFactory searches with swe.solcross_ut, which is tropical only; progressions follow for consistency.
    if natal_model.zodiac_type != "Tropical":
        raise ValueError("forecast charts support the Tropical zodiac only")


def solar_return(
    natal: AstrologicalSubject,
    year: int,
    location: Optional[ReturnLocation],
    theme: str = "light",
    language: str = "EN",
    style: str = "modern",
) -> Dict[str, Any]:
    """The Sun's return to its natal longitude around the birthday in `year`, cast for `location` (default: birth place)."""
    natal_model = natal.model()
    _require_tropical(natal_model)
    loc = location or ReturnLocation(
        longitude=natal_model.lng,
        latitude=natal_model.lat,
        timezone=natal_model.tz_str,
        city=natal_model.city,
        nation=natal_model.nation,
    )
    # Search from three days before the birthday: the return falls within a day of it, and a Jan 1 start would
    # find the previous birthday's return for someone born on the first days of January in an eastern timezone.
    start = datetime(year, natal_model.month, 1, tzinfo=timezone.utc) + timedelta(days=natal_model.day - 4)
    with SWE_LOCK:
        factory = PlanetaryReturnFactory(
            natal_model,
            city=loc.city or "Unknown",
            nation=loc.nation or "GB",
            lng=loc.longitude,
            lat=loc.latitude,
            tz_str=loc.timezone,
            online=False,
        )
        return_model = factory.next_return_from_iso_formatted_time(start.isoformat(), "Solar")

    svg = _drawer_svg(
        ChartDataFactory.create_single_wheel_return_chart_data(return_model), theme, language, style
    )
    return {
        "svg": svg,
        "data": {
            "return_moment_utc": return_model.iso_formatted_utc_datetime,
            "return_moment_local": return_model.iso_formatted_local_datetime,
            "natal_chart": subject_to_dict(natal),
            "return_chart": subject_to_dict(return_model),
            "aspects_to_natal": get_synastry_aspects(natal_model, return_model),
        },
    }


def progressed_moment(natal_local: datetime, target: date) -> datetime:
    """Birth moment plus one day per tropical year lived up to `target`, both read on the birth's local calendar.

    `natal_local` is the timezone-aware local birth moment; the result is in UTC.
    """
    target_local = datetime.combine(target, natal_local.time(), tzinfo=natal_local.tzinfo)
    if target_local < natal_local:
        raise ValueError("target_date must be on or after the birth date")
    years = (target_local - natal_local).total_seconds() / 86400 / TROPICAL_YEAR_DAYS
    return (natal_local + timedelta(days=years)).astimezone(timezone.utc)


def secondary_progressions(
    natal: AstrologicalSubject,
    target: date,
    theme: str = "light",
    language: str = "EN",
    style: str = "modern",
) -> Dict[str, Any]:
    """Secondary progressions for `target`; the progressed chart is cast at the birth place (angles by real time)."""
    natal_model = natal.model()
    _require_tropical(natal_model)
    natal_local = datetime.fromisoformat(natal_model.iso_formatted_utc_datetime).astimezone(ZoneInfo(natal_model.tz_str))
    moment = progressed_moment(natal_local, target)
    with SWE_LOCK:
        progressed = AstrologicalSubjectFactory.from_iso_utc_time(
            name=f"{natal_model.name} Progressed",
            iso_utc_time=moment.isoformat(),
            city=natal_model.city,
            nation=natal_model.nation,
            tz_str=natal_model.tz_str,
            lng=natal_model.lng,
            lat=natal_model.lat,
            online=False,
            zodiac_type=natal_model.zodiac_type,
            sidereal_mode=natal_model.sidereal_mode,
            houses_system_identifier=natal_model.houses_system_identifier,
            perspective_type=natal_model.perspective_type,
            active_points=natal_model.active_points,
            suppress_geonames_warning=True,
        )

    svg = _drawer_svg(
        ChartDataFactory.create_transit_chart_data(natal_model, progressed),
        theme,
        language,
        style,
        title=f"{natal_model.name} - Progressions {target.isoformat()}",
    )
    return {
        "svg": svg,
        "data": {
            "target_date": target.isoformat(),
            "progressed_moment_utc": moment.isoformat(),
            "natal_chart": subject_to_dict(natal),
            "progressed_chart": subject_to_dict(progressed),
            "aspects_to_natal": get_synastry_aspects(natal_model, progressed),
        },
    }
