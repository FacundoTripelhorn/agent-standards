"""Read the repository through git: changed files, added lines, and the
files as they were at the base commit."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


class Status(StrEnum):
    """`git diff --name-status` letters that matter here."""

    ADDED = "A"
    MODIFIED = "M"
    RENAMED = "R"
    COPIED = "C"


@dataclass(frozen=True)
class Change:
    """A file added or changed since the base, with its path at the base."""

    path: str
    base_path: str | None
    added_lines: frozenset[int] = field(default_factory=frozenset)


def git(repo: Path, *args: str) -> str:
    """Run git in the repository and return stdout."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def has_commit(repo: Path, rev: str) -> bool:
    """Whether the commit exists locally (it needs fetch-depth: 0)."""
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{rev}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _parse_status_line(line: str) -> tuple[str, str | None] | None:
    parts = line.split("\t")
    letter = parts[0][:1]
    if letter in (Status.RENAMED, Status.COPIED):
        return parts[2], parts[1]
    if letter == Status.MODIFIED:
        return parts[1], parts[1]
    if letter == Status.ADDED:
        return parts[1], None
    return None


def added_lines(repo: Path, base: str, path: str) -> frozenset[int]:
    """Line numbers (in the new file) that the diff adds or changes."""
    diff = git(repo, "diff", "-U0", "-M", base, "HEAD", "--", path)
    lines: set[int] = set()
    for line in diff.splitlines():
        match = _HUNK.match(line)
        if match:
            start = int(match.group(1))
            count = int(match.group(2) or "1")
            lines.update(range(start, start + count))
    return frozenset(lines)


def changed_files(repo: Path, base: str) -> list[Change]:
    """Files added, modified or renamed between the base and HEAD."""
    out = git(repo, "diff", "--name-status", "-M", "--diff-filter=AMRC", base, "HEAD")
    changes = []
    for line in out.splitlines():
        parsed = _parse_status_line(line)
        if parsed:
            path, base_path = parsed
            changes.append(Change(path, base_path, added_lines(repo, base, path)))
    return changes


def show(repo: Path, rev: str, path: str) -> str | None:
    """A file's text at a commit, or None if it did not exist there."""
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", errors="replace")


def tracked_files(repo: Path, rev: str = "HEAD") -> list[str]:
    """Every file git tracks at a commit."""
    return git(repo, "ls-tree", "-r", "--name-only", rev).splitlines()
