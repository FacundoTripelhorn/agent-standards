"""Findings and how they are reported: GitHub annotations, the job summary
and the exit code."""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from standards.constants import Check, Mode, Rule

SUMMARY_ENV = "GITHUB_STEP_SUMMARY"


class Level(StrEnum):
    """GitHub workflow command for an annotation."""

    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class Finding:
    """One problem: what is wrong, where, how to fix it, and which rule."""

    check: Check
    message: str
    fix: str
    rule: Rule
    path: str | None = None
    line: int | None = None
    blocking: bool = True


def _escape(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(text: str) -> str:
    return _escape(text).replace(":", "%3A").replace(",", "%2C")


def level_for(finding: Finding, mode: Mode) -> Level:
    """Non-blocking findings are notices; the rest follow the mode."""
    if not finding.blocking:
        return Level.NOTICE
    return Level.ERROR if mode is Mode.FAIL else Level.WARNING


def annotation(finding: Finding, mode: Mode) -> str:
    """The `::warning file=…,line=…::` command for one finding."""
    props = [f"title={_escape_property(finding.check.value)}"]
    if finding.path:
        props.insert(0, f"file={_escape_property(finding.path)}")
    if finding.line:
        props.insert(1, f"line={finding.line}")
    body = f"{finding.message} Fix: {finding.fix} Rule: {finding.rule.value}."
    return f"::{level_for(finding, mode).value} {','.join(props)}::{_escape(body)}"


def summary(findings: list[Finding], mode: Mode, notes: list[str]) -> str:
    """Markdown for the job summary: counts per check, then each finding."""
    lines = [f"## agent-standards checks ({mode.value} mode)", ""]
    lines += [f"- {note}" for note in notes]
    if not findings:
        lines += ["", "No findings."]
        return "\n".join(lines) + "\n"
    counts = Counter(f.check for f in findings)
    lines += ["", "| Check | Findings |", "|---|---|"]
    lines += [f"| {check.value} | {count} |" for check, count in counts.items()]
    lines += ["", "| Where | Problem | Fix |", "|---|---|---|"]
    for f in findings:
        where = f"`{f.path}:{f.line}`" if f.path and f.line else f"`{f.path or '-'}`"
        lines.append(f"| {where} | {f.message} | {f.fix} ({f.rule.value}) |")
    return "\n".join(lines) + "\n"


def report(findings: list[Finding], mode: Mode, notes: list[str]) -> int:
    """Print annotations, write the summary, return the exit code."""
    for finding in findings:
        print(annotation(finding, mode))
    for note in notes:
        print(note)
    summary_path = os.environ.get(SUMMARY_ENV)
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as handle:
            handle.write(summary(findings, mode, notes))
    blocking = any(f.blocking for f in findings)
    return 1 if mode is Mode.FAIL and blocking else 0
