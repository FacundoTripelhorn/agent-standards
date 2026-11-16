"""Fixtures: a throwaway git repository with a base commit and a head."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

PROJECT_YML = """\
key: GHOST
language: en
tracker: github
status: active
package_manager: pnpm
version_file: package.json
release: tag
"""


class Repo:
    """A git repository the test writes files into and commits."""

    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir(parents=True)
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.email", "test@example.invalid")
        self._git("config", "user.name", "Test")
        self._git("config", "commit.gpgsign", "false")

    def _git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    def write(self, path: str, content: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def commit(self, message: str = "change") -> str:
        self._git("add", "-A")
        self._git("commit", "-q", "--allow-empty", "-m", message)
        return self._git("rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    created = Repo(tmp_path / "repo")
    created.write("project.yml", PROJECT_YML)
    created.write("package.json", json.dumps({"version": "1.2.3"}))
    return created


@pytest.fixture(autouse=True)
def no_github_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests run inside CI too: never read the real run's event or summary."""
    for name in ("GITHUB_EVENT_PATH", "GITHUB_REF", "GITHUB_STEP_SUMMARY"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def event(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Callable[..., None]:
    """Write a GitHub event payload and point the environment at it."""

    def _set(payload: dict[str, object], ref: str = "refs/heads/feature") -> None:
        path = tmp_path / "event.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
        monkeypatch.setenv("GITHUB_REF", ref)

    return _set
