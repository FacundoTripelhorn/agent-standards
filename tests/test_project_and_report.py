from __future__ import annotations

from pathlib import Path

import pytest

from conftest import Repo
from standards.constants import Check, Mode, Rule
from standards.findings import Finding, annotation, report
from standards.project_config import load_project


def test_valid_project(repo: Repo) -> None:
    project, findings = load_project(repo.root)
    assert findings == [] and project is not None and project.key == "GHOST"


def test_invalid_project_lists_every_problem(repo: Repo) -> None:
    repo.write(
        "project.yml",
        "key: ghost\nlanguage: English\ntracker: jira\nstatus: active\n"
        "package_manager: yarn\nversion_file: missing.toml\nrelease: tag\nextra: 1\n",
    )
    project, findings = load_project(repo.root)
    messages = " ".join(f.message for f in findings)
    assert project is None
    for expected in (
        "key: ghost",
        "English",
        "jira",
        "yarn",
        "missing.toml",
        "`extra`",
    ):
        assert expected in messages


def test_missing_project_file(tmp_path: Path) -> None:
    project, [finding] = load_project(tmp_path)
    assert project is None and "missing" in finding.message


FINDING = Finding(Check.LITERAL, "Bad, really: 100%.", "Fix it.", Rule.CODE, "a.py", 3)


def test_annotation_escapes_and_locates() -> None:
    line = annotation(FINDING, Mode.WARN)
    assert line.startswith("::warning file=a.py,line=3,title=Literal comparison::")
    assert "100%25" in line


def test_warn_mode_never_fails_and_fail_mode_does(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    assert report([FINDING], Mode.WARN, []) == 0
    assert report([FINDING], Mode.FAIL, []) == 1
    assert "| Literal comparison | 1 |" in summary.read_text(encoding="utf-8")


def test_non_blocking_findings_never_fail() -> None:
    notice = Finding(
        Check.FILE_SIZE, "Big.", "Split.", Rule.THRESHOLDS, "a.ts", blocking=False
    )
    assert annotation(notice, Mode.FAIL).startswith("::notice")
    assert report([notice], Mode.FAIL, []) == 0
