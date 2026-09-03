"""Reject full-suite failures or errors that differ from the reviewed base."""

from __future__ import annotations

import argparse
from contextlib import nullcontext, redirect_stdout
import json
import os
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASELINE = ROOT / ".github" / "pytest-regression-baseline.json"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--tests-root", type=Path, default=ROOT / "tests")
    parser.add_argument("--print-observed", action="store_true")
    args = parser.parse_args()

    project_root = args.tests_root.resolve().parent
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))

    collector = FailureCollector()
    output = redirect_stdout(sys.stderr) if args.print_observed else nullcontext()
    with output:
        exit_code = pytest.main(
            [
                "-o",
                "addopts=",
                "-o",
                "log_cli=false",
                "-q",
                "--tb=no",
                "--continue-on-collection-errors",
                str(args.tests_root.resolve()),
            ],
            plugins=[collector],
        )
    observed = collector.result()

    if args.print_observed:
        print(json.dumps(observed, indent=2))
        return 0 if exit_code in {pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED} else int(exit_code)

    expected_document = json.loads(args.baseline.read_text(encoding="utf-8"))
    expected = {name: sorted(expected_document[name]) for name in ("failed", "errors")}
    if exit_code not in {pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED} or observed != expected:
        print("Full-suite regression baseline mismatch.", file=sys.stderr)
        print(json.dumps({"expected": expected, "observed": observed}, indent=2), file=sys.stderr)
        return 1

    print(f"Regression baseline matched: {len(observed['failed'])} failures, {len(observed['errors'])} errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
