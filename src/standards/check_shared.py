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
    unsafe_destinations,
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


def _unsafe_finding(name: str) -> Finding:
    return Finding(
        Check.SHARED_COPY,
        f"`{name}` is a symlink or resolves outside the repository.",
        "Make it a regular file in the repository, then run standards-sync; "
        "the sync never writes through a symlink.",
        Rule.CI,
        name,
    )


def _copy_findings(repo: Path, root: Path, names: list[str]) -> list[Finding]:
    version = package_version()
    findings = []
    for name in names:
        copy = read(repo / name)
        if copy is None:
            findings.append(_finding(f"`{name}` is missing.", name, repo))
        elif copy != shared_text(root, name):
            message = f"`{name}` differs from agent-standards {version}."
            findings.append(_finding(message, name, repo))
    return findings


def _block_findings(repo: Path, root: Path) -> list[Finding]:
    try:
        block = current_block(read(repo / AGENTS_FILE) or "")
    except ValueError as error:
        message = f"Invalid `{AGENTS_FILE}` block: {error}."
        return [_finding(message, AGENTS_FILE, repo)]
    if block is None:
        message = f"`{AGENTS_FILE}` has no shared block."
        return [_finding(message, AGENTS_FILE, repo)]
    if block != base_block(root):
        version = package_version()
        message = f"The shared block in `{AGENTS_FILE}` differs from {version}."
        return [_finding(message, AGENTS_FILE, repo)]
    return []


def check_shared_copies(repo: Path, project: Project | None) -> list[Finding]:
    """Report each copy that is missing, differs from this version, or sits
    behind a symlink the sync would refuse to write through."""
    if project is None or is_origin(repo):
        return []
    repo = repo.resolve()
    root = shared_root()
    copies = copied_files(root, project.tracker)
    unsafe = unsafe_destinations(repo, [*copies, AGENTS_FILE])
    findings = [_unsafe_finding(name) for name in unsafe]
    findings += _copy_findings(repo, root, [n for n in copies if n not in unsafe])
    if AGENTS_FILE not in unsafe:
        findings += _block_findings(repo, root)
    return findings
