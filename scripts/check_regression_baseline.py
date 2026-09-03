"""Collect and compare exact pytest failure and error identities."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASELINE = ROOT / ".github" / "pytest-regression-baseline.json"
SHA_PATTERN = re.compile(r"[0-9a-fA-F]{40}")


class BaselineError(ValueError):
    """Raised when the regression baseline or observed results are invalid."""


class FailureCollector:
    def __init__(self) -> None:
        self.failed: set[str] = set()
        self.errors: set[str] = set()

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.failed:
            target = self.failed if report.when == "call" else self.errors
            target.add(report.nodeid)

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        if report.failed:
            self.errors.add(report.nodeid)

    def result(self) -> dict[str, list[str]]:
        return {"failed": sorted(self.failed), "errors": sorted(self.errors)}


def _validated_sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or not SHA_PATTERN.fullmatch(value):
        raise BaselineError(f"{name} must be a full 40-character Git SHA")
    return value.lower()


def _result_sets(document: dict[str, Any], name: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for classification in ("failed", "errors"):
        values = document.get(classification)
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise BaselineError(f"{name}.{classification} must be a list of pytest node IDs")
        result[classification] = set(values)
    return result


def verify_regression(
    baseline: dict[str, Any],
    head_observed: dict[str, Any],
    *,
    expected_base_sha: str | None = None,
    base_observed: dict[str, Any] | None = None,
) -> None:
    """Validate the anchor and reject new or reclassified head failures."""
    baseline_sha = _validated_sha(baseline.get("base_sha"), "base_sha")
    expected = _result_sets(baseline, "baseline")

    if expected_base_sha is not None:
        expected_base_sha = _validated_sha(expected_base_sha, "expected_base_sha")
        if baseline_sha != expected_base_sha:
            raise BaselineError(f"baseline base_sha {baseline_sha} does not match PR base {expected_base_sha}")
        if base_observed is None:
            raise BaselineError("PR verification requires an independent base observation")

    if base_observed is not None and _result_sets(base_observed, "base observation") != expected:
        raise BaselineError("base observation does not match the committed baseline")

    head = _result_sets(head_observed, "head observation")
    new_failures = sorted(head["failed"] - expected["failed"])
    new_errors = sorted(head["errors"] - expected["errors"])
    if new_failures or new_errors:
        details = []
        if new_failures:
            details.append(f"new failures: {new_failures}")
        if new_errors:
            details.append(f"new errors: {new_errors}")
        raise BaselineError("; ".join(details))


def verify_ancestor(repository: Path, base_sha: str, tested_sha: str) -> None:
    """Require both commits to exist and the baseline commit to precede the tested commit."""
    base_sha = _validated_sha(base_sha, "base_sha")
    tested_sha = _validated_sha(tested_sha, "tested_sha")
    for revision in (base_sha, tested_sha):
        result = subprocess.run(
            ["git", "-C", str(repository), "cat-file", "-e", f"{revision}^{{commit}}"],
            check=False,
        )
        if result.returncode:
            raise BaselineError(f"Git commit does not exist: {revision}")
    result = subprocess.run(
        ["git", "-C", str(repository), "merge-base", "--is-ancestor", base_sha, tested_sha],
        check=False,
    )
    if result.returncode:
        raise BaselineError(f"baseline commit {base_sha} is not an ancestor of tested commit {tested_sha}")


def collect_results(tests_root: Path) -> tuple[dict[str, list[str]], pytest.ExitCode]:
    project_root = tests_root.resolve().parent
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))
    collector = FailureCollector()
    exit_code = pytest.main(
        [
            "-o",
            "addopts=",
            "-o",
            "log_cli=false",
            "-q",
            "--tb=no",
            "--continue-on-collection-errors",
            str(tests_root.resolve()),
        ],
        plugins=[collector],
    )
    return collector.result(), exit_code


def _read_json(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise BaselineError(f"{path} must contain a JSON object")
    return document


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    base_sha = subparsers.add_parser("base-sha")
    base_sha.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    base_sha.add_argument("--expected-base-sha")

    collect = subparsers.add_parser("collect")
    collect.add_argument("--tests-root", type=Path, default=ROOT / "tests")
    collect.add_argument("--output", type=Path, required=True)

    verify_pr = subparsers.add_parser("verify-pr")
    verify_pr.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    verify_pr.add_argument("--expected-base-sha", required=True)
    verify_pr.add_argument("--base-results", type=Path, required=True)
    verify_pr.add_argument("--head-results", type=Path, required=True)

    verify_release = subparsers.add_parser("verify-ancestor")
    verify_release.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    verify_release.add_argument("--head-results", type=Path, required=True)
    verify_release.add_argument("--repository", type=Path, default=ROOT)
    verify_release.add_argument("--tested-sha", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "collect":
            observed, exit_code = collect_results(args.tests_root)
            args.output.write_text(json.dumps(observed, indent=2) + "\n", encoding="utf-8")
            if exit_code not in {pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED}:
                raise BaselineError(f"pytest exited before completing the suite: {exit_code}")
            return 0

        baseline = _read_json(args.baseline)
        baseline_sha = _validated_sha(baseline.get("base_sha"), "base_sha")
        if args.command == "base-sha":
            if args.expected_base_sha is not None:
                expected = _validated_sha(args.expected_base_sha, "expected_base_sha")
                if baseline_sha != expected:
                    raise BaselineError(f"baseline base_sha {baseline_sha} does not match PR base {expected}")
            print(baseline_sha)
            return 0

        head_results = _read_json(args.head_results)
        if args.command == "verify-pr":
            verify_regression(
                baseline,
                head_results,
                expected_base_sha=args.expected_base_sha,
                base_observed=_read_json(args.base_results),
            )
        else:
            verify_ancestor(args.repository, baseline_sha, args.tested_sha)
            verify_regression(baseline, head_results)
        print("Regression baseline verified; head introduced no new or reclassified failures")
        return 0
    except (BaselineError, json.JSONDecodeError, OSError) as error:
        print(f"Regression check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
