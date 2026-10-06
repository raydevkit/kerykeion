import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.check_regression_baseline import BaselineError, verify_regression


BASE_SHA = "a" * 40
OTHER_SHA = "b" * 40
BASELINE = {
    "base_sha": BASE_SHA,
    "failed": ["tests/test_example.py::test_failure"],
    "errors": ["tests/test_example.py::test_error"],
}
OBSERVED = {
    "failed": ["tests/test_example.py::test_failure"],
    "errors": ["tests/test_example.py::test_error"],
}


@pytest.mark.parametrize("base_sha", [None, "short", "g" * 40])
def test_rejects_a_missing_or_malformed_baseline_sha(base_sha):
    baseline = {**BASELINE}
    if base_sha is None:
        baseline.pop("base_sha")
    else:
        baseline["base_sha"] = base_sha

    with pytest.raises(BaselineError, match="base_sha"):
        verify_regression(baseline, OBSERVED)


def test_rejects_a_different_pull_request_base_sha():
    with pytest.raises(BaselineError, match="does not match"):
        verify_regression(BASELINE, OBSERVED, expected_base_sha=OTHER_SHA, base_observed=OBSERVED)


def test_rejects_a_base_observation_that_differs_from_the_baseline():
    changed_base = {"failed": [], "errors": OBSERVED["errors"]}

    with pytest.raises(BaselineError, match="base observation"):
        verify_regression(BASELINE, OBSERVED, expected_base_sha=BASE_SHA, base_observed=changed_base)


def test_rejects_a_new_head_failure():
    changed_head = {"failed": [*OBSERVED["failed"], "tests/test_new.py::test_failure"], "errors": OBSERVED["errors"]}

    with pytest.raises(BaselineError, match="new failures"):
        verify_regression(BASELINE, changed_head)


def test_rejects_a_failure_that_changes_into_an_error():
    changed_head = {"failed": [], "errors": [*OBSERVED["errors"], OBSERVED["failed"][0]]}

    with pytest.raises(BaselineError, match="new errors"):
        verify_regression(BASELINE, changed_head)


def test_rejects_an_error_that_changes_into_a_failure():
    changed_head = {"failed": [*OBSERVED["failed"], OBSERVED["errors"][0]], "errors": []}

    with pytest.raises(BaselineError, match="new failures"):
        verify_regression(BASELINE, changed_head)


def test_accepts_an_independently_verified_base_and_known_head_results():
    verify_regression(BASELINE, OBSERVED, expected_base_sha=BASE_SHA, base_observed=OBSERVED)


def test_base_collection_replays_http_without_hiding_failures(tmp_path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_base.py").write_text(
        'from kerykeion.fetch_geonames import FetchGeonames\n'
        # A lookup during collection verifies the plugin runs before test imports.
        'rome = FetchGeonames("Roma", "IT").get_serialized_data()\n'
        'def test_known_location():\n'
        '    assert rome["timezonestr"] == "Europe/Rome"\n'
        'def test_unknown_location():\n'
        '    FetchGeonames("Unrecorded City", "IT").get_serialized_data()\n'
        'def test_real_failure():\n'
        '    assert False, "real regression"\n',
        encoding="utf-8",
    )
    output = tmp_path / "observed.json"
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check_regression_baseline.py"), "collect",
         "--tests-root", str(tests), "--offline-geonames", "--output", str(output)],
        env={**os.environ, "PYTHONPATH": str(root)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(output.read_text()) == {
        "failed": ["tests/test_base.py::test_real_failure", "tests/test_base.py::test_unknown_location"],
        "errors": [],
    }
