from concurrent.futures import ThreadPoolExecutor

from app.schemas.common import SubjectInput
from kerykeion.fetch_geonames import FetchGeonames

from app.services.kerykeion_service import SWE_LOCK, create_astrological_subject

CASES = [("LAHIRI", 1990), ("FAGAN_BRADLEY", 1975)]


def make_subject(mode, year):
    subject = create_astrological_subject(
        SubjectInput(
            name=mode, year=year, month=5, day=15, hour=14, minute=30,
            longitude=12.4964, latitude=41.9028, timezone="Europe/Rome", city="Rome",
        ),
        zodiac_type="Sidereal",
        sidereal_mode=mode,
    )
    return [subject.sun.abs_pos, subject.moon.abs_pos, subject.first_house.abs_pos]


def test_concurrent_sidereal_subjects_match_sequential():
    expected = [make_subject(*case) for case in CASES]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda i: make_subject(*CASES[i % 2]), range(40)))
    for i, result in enumerate(results):
        assert result == expected[i % 2]


def test_city_lookup_runs_outside_the_ephemeris_lock(monkeypatch):
    lock_held = []

    def fake_geonames(self):
        lock_held.append(SWE_LOCK.locked())
        return {"countryCode": "IT", "timezonestr": "Europe/Rome", "lat": "41.9028", "lng": "12.4964"}

    monkeypatch.setattr(FetchGeonames, "get_serialized_data", fake_geonames)
    subject = create_astrological_subject(
        SubjectInput(name="City", year=1990, month=5, day=15, hour=14, minute=30, city="Rome", nation="it")
    )
    assert lock_held == [False]
    assert (subject.lng, subject.lat, subject.tz_str, subject.nation) == (12.4964, 41.9028, "Europe/Rome", "IT")
