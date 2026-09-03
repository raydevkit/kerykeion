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
