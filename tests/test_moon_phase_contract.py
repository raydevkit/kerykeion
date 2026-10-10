"""
Tests for the Moon Phase adapter contract.

Verifies that get_detailed_moon_phase() preserves the existing API response
shape and fields while using MoonPhaseDetailsFactory internally.
"""

import pytest
import logging
from datetime import datetime

logging.basicConfig(level=logging.CRITICAL)

from app.services import calculation_service
from app.services.calculation_service import get_detailed_moon_phase


def _fetch_moon_phase(**kwargs):
    defaults = {"timezone": "UTC", "longitude": 0.0, "latitude": 51.5}
    defaults.update(kwargs)
    return get_detailed_moon_phase(**defaults)


class TestMoonPhaseResponseShape:
    def test_top_level_keys(self):
        result = _fetch_moon_phase()
        assert "timestamp" in result
        assert "location" in result
        assert "phase" in result
        assert "age" in result
        assert "next_phase" in result
        assert "moon_position" in result
        assert "sun_position" in result
        assert "geometry" in result

    def test_optional_richer_fields_present(self):
        result = _fetch_moon_phase()
        assert "upcoming_phases" in result
        assert "sun_info" in result
        assert "next_lunar_eclipse" in result


class TestMoonPhaseFields:
    def test_timestamp_is_iso_string(self):
        result = _fetch_moon_phase()
        assert isinstance(result["timestamp"], str)
        assert "T" in result["timestamp"] or result["timestamp"].endswith("Z")

    def test_location_has_coordinates(self):
        result = _fetch_moon_phase(timezone="Europe/London", longitude=-0.12, latitude=51.5)
        loc = result["location"]
        assert loc["longitude"] == -0.12
        assert loc["latitude"] == 51.5
        assert loc["timezone"] == "Europe/London"

    def test_phase_fields(self):
        result = _fetch_moon_phase()
        phase = result["phase"]
        assert isinstance(phase["name"], str)
        assert len(phase["name"]) > 0
        assert isinstance(phase["emoji"], str)
        assert isinstance(phase["illumination"], (int, float))
        assert 0 <= phase["illumination"] <= 100
        assert isinstance(phase["is_waxing"], bool)

    def test_age_fields(self):
        result = _fetch_moon_phase()
        age = result["age"]
        assert isinstance(age["days"], (int, float))
        assert age["days"] >= 0
        assert isinstance(age["phase_day"], int)
        assert isinstance(age["synodic_month"], float)
        assert abs(age["synodic_month"] - 29.530588853) < 0.001
        assert isinstance(age["percent_complete"], (int, float))
        assert 0 <= age["percent_complete"] <= 100

    def test_next_phase_fields(self):
        result = _fetch_moon_phase()
        np = result["next_phase"]
        assert isinstance(np["name"], str)
        assert np["name"] in ("New Moon", "First Quarter", "Full Moon", "Last Quarter")
        assert isinstance(np["days_until"], (int, float))
        assert np["days_until"] > 0

    def test_moon_position_fields(self):
        result = _fetch_moon_phase()
        mp = result["moon_position"]
        assert isinstance(mp["sign"], str)
        assert len(mp["sign"]) > 0
        assert isinstance(mp["sign_emoji"], str)
        assert isinstance(mp["degree"], (int, float))
        assert 0 <= mp["degree"] < 30
        assert isinstance(mp["abs_degree"], (int, float))
        assert 0 <= mp["abs_degree"] < 360
        assert isinstance(mp["element"], str)
        assert mp["element"] in ("Fire", "Earth", "Air", "Water")
        assert isinstance(mp["quality"], str)
        assert mp["quality"] in ("Cardinal", "Fixed", "Mutable")

    def test_sun_position_fields(self):
        result = _fetch_moon_phase()
        sp = result["sun_position"]
        assert isinstance(sp["sign"], str)
        assert len(sp["sign"]) > 0
        assert isinstance(sp["degree"], (int, float))

    def test_geometry_fields(self):
        result = _fetch_moon_phase()
        geo = result["geometry"]
        assert isinstance(geo["elongation"], (int, float))
        assert 0 <= geo["elongation"] <= 360
        assert isinstance(geo["sun_phase"], int)

    def test_illumination_consistent_with_elongation(self):
        result = _fetch_moon_phase()
        elongation = result["geometry"]["elongation"]
        illumination = result["phase"]["illumination"]
        expected_approx = (1 - __import__("math").cos(__import__("math").radians(elongation))) / 2 * 100
        assert abs(illumination - expected_approx) < 2

    def test_is_waxing_consistent_with_elongation(self):
        result = _fetch_moon_phase()
        elongation = result["geometry"]["elongation"]
        is_waxing = result["phase"]["is_waxing"]
        if elongation < 180:
            assert is_waxing is True
        else:
            assert is_waxing is False


class TestMoonPhaseRicherFields:
    def test_upcoming_phases_structure(self):
        result = _fetch_moon_phase()
        up = result.get("upcoming_phases")
        if up is None:
            pytest.skip("upcoming_phases not available")
        assert "new_moon" in up
        assert "first_quarter" in up
        assert "full_moon" in up
        assert "last_quarter" in up
        for phase_name in ("new_moon", "first_quarter", "full_moon", "last_quarter"):
            window = up[phase_name]
            if window and "next" in window and window["next"]:
                assert "days_ahead" in window["next"] or "timestamp" in window["next"]

    def test_sun_info_structure(self):
        result = _fetch_moon_phase(timezone="Europe/London", longitude=-0.12, latitude=51.5)
        si = result.get("sun_info")
        if si is None:
            pytest.skip("sun_info not available")
        if si.get("sunrise") is not None:
            assert isinstance(si["sunrise"], int)
        if si.get("solar_noon") is not None:
            assert isinstance(si["solar_noon"], str)

    def test_next_lunar_eclipse_structure(self):
        result = _fetch_moon_phase()
        eclipse = result.get("next_lunar_eclipse")
        if eclipse is None:
            pytest.skip("next_lunar_eclipse not available")
        assert "type" in eclipse
        assert isinstance(eclipse["type"], str)

    def test_next_solar_eclipse_structure(self):
        result = _fetch_moon_phase()
        eclipse = result.get("next_solar_eclipse")
        if eclipse is None:
            pytest.skip("next_solar_eclipse not available")
        assert "type" in eclipse
        assert isinstance(eclipse["type"], str)


class TestMoonPhasePrecision:
    def test_synodic_month_uses_precise_value(self):
        result = _fetch_moon_phase()
        synodic = result["age"]["synodic_month"]
        assert synodic == 29.530588853

    def test_age_days_non_negative(self):
        result = _fetch_moon_phase()
        assert result["age"]["days"] >= 0

    def test_percent_complete_bounded(self):
        result = _fetch_moon_phase()
        pct = result["age"]["percent_complete"]
        assert 0 <= pct <= 100


class TestMoonPhaseKnownDates:
    def test_may_18_2026_matches_reference_moon_age_and_phase(self, monkeypatch):
        class FixedDatetime(datetime):
            @classmethod
            def utcnow(cls):
                return cls(2026, 5, 18, 9, 29, 0)

        monkeypatch.setattr(calculation_service, "datetime", FixedDatetime)

        result = _fetch_moon_phase(timezone="UTC", longitude=0.0, latitude=51.5)

        assert result["phase"]["name"] == "Waxing Crescent"
        assert 3.0 <= result["phase"]["illumination"] <= 5.0
        assert 1.5 <= result["age"]["days"] <= 2.2
        assert 5.0 <= result["age"]["percent_complete"] <= 8.0

    def test_may_18_2026_upcoming_phase_windows_are_labeled_correctly(self, monkeypatch):
        class FixedDatetime(datetime):
            @classmethod
            def utcnow(cls):
                return cls(2026, 5, 18, 9, 29, 0)

        monkeypatch.setattr(calculation_service, "datetime", FixedDatetime)

        result = _fetch_moon_phase(timezone="UTC", longitude=0.0, latitude=51.5)
        upcoming = result["upcoming_phases"]

        assert "16 May 2026" in upcoming["new_moon"]["last"]["datestamp"]
        assert "23 May 2026" in upcoming["first_quarter"]["next"]["datestamp"]
        assert result["next_phase"]["name"] == "First Quarter"


if __name__ == "__main__":
    pytest.main(["-vv", "--log-level=CRITICAL", "--log-cli-level=CRITICAL", __file__])


class TestPhaseWindowPrecision:
    """Phase windows come from the ephemeris, not the mean synodic month."""

    def test_refines_mean_estimate_to_ephemeris_full_moon(self):
        from datetime import timezone
        from app.services.calculation_service import _refine_phase_dt

        # Mean-motion estimate served before the fix; Swiss Ephemeris puts the
        # October 2026 full moon (elongation 180.00°) at 26 Oct 04:11:47 UTC.
        estimate = datetime(2026, 10, 25, 10, 20, 39, tzinfo=timezone.utc)
        exact = datetime(2026, 10, 26, 4, 11, 47, tzinfo=timezone.utc)
        assert abs((_refine_phase_dt(estimate, 180.0) - exact).total_seconds()) < 60

    def test_windows_bracket_now(self):
        from datetime import timezone
        from app.services.calculation_service import _compute_phase_windows_from_elongation

        now = datetime(2026, 10, 8, 19, 27, tzinfo=timezone.utc)
        windows = _compute_phase_windows_from_elongation(now, 337.39)
        full = windows["full_moon"]
        assert full["last"]["timestamp"] < now.timestamp() < full["next"]["timestamp"]
        assert full["next"]["datestamp"].startswith("Mon, 26 Oct 2026 04:1")
