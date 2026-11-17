"""The copies of the shared files match the action's own version (ci.md).

A copy that differs was edited by hand, or comes from another version than
the one the workflow pins. Either way `standards-sync` restores it."""

from __future__ import annotations

import re
from pathlib import Path

from standards.constants import Check, Rule
from standards.findings import Finding
from standards.project_config import Project
from standards.shared import (
    ACTION_REPOSITORY,
    AGENTS_FILE,
    base_block,
    copied_files,
    current_block,
    is_origin,
    package_version,
    read,
    shared_root,
    shared_text,
)

WORKFLOWS_GLOB = ".github/workflows/*.y*ml"
# A workflow step's uses declaration, not a comment or arbitrary text.
PINNED_ACTION = re.compile(
    rf"""(?:-\s*)?uses:\s*['"]?{re.escape(ACTION_REPOSITORY)}"""
    r"""@([0-9a-f]{40})['"]?(?:\s+#.*)?"""
)


def pinned_commit(repo: Path) -> str | None:
    """The unique action SHA, or None when missing or conflicting."""
    pins = set()
    for workflow in sorted(repo.glob(WORKFLOWS_GLOB)):
        for line in workflow.read_text(encoding="utf-8").splitlines():
            match = PINNED_ACTION.fullmatch(line.strip())
            if match:
                pins.add(match.group(1))
    return next(iter(pins)) if len(pins) == 1 else None


def _finding(message: str, path: str, repo: Path) -> Finding:
    pin = pinned_commit(repo)
    if pin is None:
        fix = (
            "Ensure the workflows have exactly one full-SHA agent-standards "
            "pin, then run standards-sync with that commit."
        )
    else:
        command = (
            f"uvx --from git+https://github.com/{ACTION_REPOSITORY}@{pin}"
            " standards-sync"
        )
        fix = f"Run `{command}`. To change a rule, edit agent-standards."
    return Finding(
        Check.SHARED_COPY,
        message,
        fix,
        Rule.CI,
        path,
    )


def check_shared_copies(repo: Path, project: Project | None) -> list[Finding]:
    """Report each copy that is missing or differs from this version."""
    if project is None or is_origin(repo):
        return []
    root = shared_root()
    version = package_version()
    findings = []
    for name in copied_files(root):
        copy = read(repo / name)
        if copy is None:
            findings.append(_finding(f"`{name}` is missing.", name, repo))
        elif copy != shared_text(root, name):
            message = f"`{name}` differs from agent-standards {version}."
            findings.append(_finding(message, name, repo))
    try:
        block = current_block(read(repo / AGENTS_FILE) or "")
    except ValueError as error:
        message = f"Invalid `{AGENTS_FILE}` block: {error}."
        findings.append(_finding(message, AGENTS_FILE, repo))
    else:
        if block is None:
            message = f"`{AGENTS_FILE}` has no shared block."
            findings.append(_finding(message, AGENTS_FILE, repo))
        elif block != base_block(root):
            message = f"The shared block in `{AGENTS_FILE}` differs from {version}."
            findings.append(_finding(message, AGENTS_FILE, repo))
    return findings
