"""The copies of the shared files match the action's own version (ci.md).

A copy that differs was edited by hand, or comes from another version than
the one the workflow pins. Either way `standards-sync` restores it."""

from __future__ import annotations

import re
from importlib import metadata
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
    read,
    shared_root,
)

DISTRIBUTION = "agent-standards-checks"
WORKFLOWS_GLOB = ".github/workflows/*.y*ml"
# `uses: FacundoTripelhorn/agent-standards@<40 hex characters>`
PINNED_ACTION = re.compile(rf"{re.escape(ACTION_REPOSITORY)}@([0-9a-f]{{40}})")
UNKNOWN_PIN = "<the commit your workflow pins>"


def pinned_commit(repo: Path) -> str:
    """The agent-standards commit the repository's workflows pin."""
    for workflow in sorted(repo.glob(WORKFLOWS_GLOB)):
        match = PINNED_ACTION.search(workflow.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return UNKNOWN_PIN


def _finding(message: str, path: str, repo: Path) -> Finding:
    command = (
        f"uvx --from git+https://github.com/{ACTION_REPOSITORY}@{pinned_commit(repo)}"
        " standards-sync"
    )
    return Finding(
        Check.SHARED_COPY,
        message,
        f"Run `{command}`. To change a shared rule, change it in agent-standards.",
        Rule.CI,
        path,
    )


def check_shared_copies(repo: Path, project: Project | None) -> list[Finding]:
    """Report each copy that is missing or differs from this version."""
    if project is None or is_origin(repo):
        return []
    root = shared_root()
    version = metadata.version(DISTRIBUTION)
    findings = []
    for name in copied_files(root):
        copy = read(repo / name)
        if copy is None:
            findings.append(_finding(f"`{name}` is missing.", name, repo))
        elif copy != read(root / name):
            message = f"`{name}` differs from agent-standards {version}."
            findings.append(_finding(message, name, repo))
    block = current_block(read(repo / AGENTS_FILE) or "")
    if block is None:
        message = f"`{AGENTS_FILE}` has no shared block."
        findings.append(_finding(message, AGENTS_FILE, repo))
    elif block != base_block(root):
        message = f"The shared block in `{AGENTS_FILE}` differs from {version}."
        findings.append(_finding(message, AGENTS_FILE, repo))
    return findings
