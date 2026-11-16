"""Read the repository through git: changed files, added lines, and the
files as they were at the base commit."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

# A unified-diff hunk header, e.g. "@@ -10,2 +12,3 @@": group 1 is the first
# new line, group 2 the number of new lines (1 when left out).
DIFF_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


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


# `git diff --name-status -z` separates fields with NUL, so paths are exact
# (no quoting of non-ASCII characters, tabs or quotes).
NUL = "\0"
_TWO_PATHS = frozenset({Status.RENAMED, Status.COPIED})


def _parse_status_records(out: str) -> list[tuple[str, str | None]]:
    """(path, path at the base) for each added, modified, renamed or copied
    file. Renames and copies carry two paths, the others one."""
    fields = out.split(NUL)
    records: list[tuple[str, str | None]] = []
    index = 0
    while index < len(fields) and fields[index]:
        letter = fields[index][:1]
        if letter in _TWO_PATHS:
            records.append((fields[index + 2], fields[index + 1]))
            index += 3
            continue
        path = fields[index + 1]
        if letter == Status.MODIFIED:
            records.append((path, path))
        elif letter == Status.ADDED:
            records.append((path, None))
        index += 2
    return records


def added_lines(repo: Path, base: str, path: str) -> frozenset[int]:
    """Line numbers (in the new file) that the diff adds or changes."""
    diff = git(repo, "diff", "-U0", "-M", base, "HEAD", "--", path)
    lines: set[int] = set()
    for line in diff.splitlines():
        match = DIFF_HUNK_HEADER.match(line)
        if match:
            start = int(match.group(1))
            count = int(match.group(2) or "1")
            lines.update(range(start, start + count))
    return frozenset(lines)


def changed_files(repo: Path, base: str) -> list[Change]:
    """Files added, modified or renamed between the base and HEAD."""
    out = git(
        repo, "diff", "--name-status", "-z", "-M", "--diff-filter=AMRC", base, "HEAD"
    )
    return [
        Change(path, base_path, added_lines(repo, base, path))
        for path, base_path in _parse_status_records(out)
    ]


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
    out = git(repo, "ls-tree", "-r", "-z", "--name-only", rev)
    return [path for path in out.split(NUL) if path]
