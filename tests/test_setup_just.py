"""setup-just installs only an archive that matches the pinned sha256."""

from __future__ import annotations

import hashlib
import io
import os
import re
import subprocess
import tarfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]
ACTION = ROOT / "setup-just" / "action.yml"
INSTALL = ROOT / "setup-just" / "install.sh"
FAKE_JUST = b"#!/bin/sh\necho just 0.0.0-test\n"
SHA256 = re.compile(r"[0-9a-f]{64}")
VERSION = re.compile(r"\d+\.\d+\.\d+")
EXIT_FAILED = 1
LINUX_X64 = {"RUNNER_OS": "Linux", "RUNNER_ARCH": "X64"}


def archive(tmp_path: Path) -> tuple[str, str]:
    """A just-like release archive as a file:// URL, and its sha256."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        entry = tarfile.TarInfo("just")
        entry.size = len(FAKE_JUST)
        entry.mode = 0o755
        tar.addfile(entry, io.BytesIO(FAKE_JUST))
    path = tmp_path / "just.tar.gz"
    path.write_bytes(buffer.getvalue())
    return path.as_uri(), hashlib.sha256(buffer.getvalue()).hexdigest()


def install(
    tmp_path: Path, url: str, sha256: str, runner: dict[str, str]
) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
    dest = tmp_path / "bin"
    github_path = tmp_path / "github_path"
    github_path.write_text("")
    env = {"PATH": os.environ["PATH"], "GITHUB_PATH": str(github_path), **runner}
    result = subprocess.run(
        [str(INSTALL), url, sha256, str(dest)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return result, dest, github_path


def test_a_matching_archive_is_installed_and_put_on_the_path(tmp_path: Path) -> None:
    url, sha256 = archive(tmp_path)
    result, dest, github_path = install(tmp_path, url, sha256, LINUX_X64)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "just 0.0.0-test" in result.stdout
    assert (dest / "just").stat().st_mode & 0o111
    assert github_path.read_text().splitlines() == [str(dest)]


def test_a_wrong_checksum_installs_nothing(tmp_path: Path) -> None:
    url, _ = archive(tmp_path)
    result, dest, github_path = install(tmp_path, url, "0" * 64, LINUX_X64)
    assert result.returncode == EXIT_FAILED
    assert "does not match the pinned sha256" in result.stdout
    assert not dest.exists()
    assert github_path.read_text() == ""


@pytest.mark.parametrize(
    "runner",
    [
        {"RUNNER_OS": "Windows", "RUNNER_ARCH": "X64"},
        {"RUNNER_OS": "macOS", "RUNNER_ARCH": "ARM64"},
        {"RUNNER_OS": "Linux", "RUNNER_ARCH": "ARM64"},
    ],
)
def test_other_runners_stop_with_a_clear_message(
    tmp_path: Path, runner: dict[str, str]
) -> None:
    url, sha256 = archive(tmp_path)
    result, dest, github_path = install(tmp_path, url, sha256, runner)
    assert result.returncode == EXIT_FAILED
    assert "Only Linux x64 runners are supported" in result.stdout
    assert not dest.exists()
    assert github_path.read_text() == ""


def test_the_action_pins_an_exact_version_and_a_checksum() -> None:
    [step] = yaml.safe_load(ACTION.read_text())["runs"]["steps"]
    assert VERSION.fullmatch(step["env"]["JUST_VERSION"])
    assert SHA256.fullmatch(step["env"]["JUST_SHA256"])
    assert "${JUST_VERSION}" in step["run"]
