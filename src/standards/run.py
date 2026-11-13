"""Run every check and report the findings."""

from __future__ import annotations

import argparse
from pathlib import Path

from standards.check_duplicates import check_duplicate_values
from standards.checks_code import check_literals, check_size, check_suppressions
from standards.checks_repo import (
    check_pinned_actions,
    check_pr_title,
    check_release_tag,
)
from standards.constants import Mode
from standards.context import build_context
from standards.findings import Finding, report
from standards.project_config import load_project


def collect(repo: Path, base: str | None) -> tuple[list[Finding], list[str]]:
    """All findings for the repository, and notes on what was skipped."""
    context, notes = build_context(repo, base)
    project, findings = load_project(repo)
    findings += check_pr_title(context, project)
    findings += check_release_tag(context, project)
    findings += check_pinned_actions(context)
    findings += check_size(context)
    findings += check_literals(context)
    findings += check_duplicate_values(context)
    findings += check_suppressions(context)
    return findings, notes


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; returns the exit code."""
    parser = argparse.ArgumentParser(
        prog="standards", description="agent-standards checks"
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--mode", type=Mode, choices=list(Mode), default=Mode.WARN)
    parser.add_argument(
        "--base", help="Commit to compare against. Default: from the GitHub event."
    )
    args = parser.parse_args(argv)
    findings, notes = collect(args.repo.resolve(), args.base)
    return report(findings, args.mode, notes)
