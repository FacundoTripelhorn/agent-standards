"""`standards-sync`: write this version's shared files into a repository.

    uvx --from git+https://github.com/FacundoTripelhorn/agent-standards@<sha> \\
        standards-sync

Writes `docs/agent/rules/*.md` and the PR template, and replaces the shared
block in `AGENTS.md`. With `--check` it only reports what would change.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from standards.shared import (
    AGENTS_FILE,
    base_block,
    copied_files,
    is_origin,
    read,
    shared_root,
    shared_text,
    unsafe_destinations,
    with_block,
)

_ORIGIN_NOTE = "This is agent-standards: it holds the originals, nothing to sync."
EXIT_OK = 0
EXIT_CHANGES = 1
EXIT_UNSAFE_PATH = 2
EXIT_INVALID_BLOCK = 3


def planned_writes(repo: Path) -> dict[str, str]:
    """The files whose content differs from this version, with their new text."""
    root = shared_root()
    writes = {}
    for name in copied_files(root):
        original = shared_text(root, name)
        if read(repo / name) != original:
            writes[name] = original
    agents = read(repo / AGENTS_FILE) or ""
    updated = with_block(agents, base_block(root))
    if updated != agents:
        writes[AGENTS_FILE] = updated
    return writes


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; returns the exit code."""
    parser = argparse.ArgumentParser(
        prog="standards-sync",
        description="Write this version of the shared rules into a repository.",
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check", action="store_true", help="Report what would change; write nothing."
    )
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    if is_origin(repo):
        print(_ORIGIN_NOTE)
        return EXIT_OK
    managed = [*copied_files(shared_root()), AGENTS_FILE]
    unsafe = unsafe_destinations(repo, managed)
    for name in unsafe:
        print(f"refusing to sync {name}: unsafe path or symlink", file=sys.stderr)
    if unsafe:
        return EXIT_UNSAFE_PATH
    try:
        writes = planned_writes(repo)
    except ValueError as error:
        print(f"refusing to sync {AGENTS_FILE}: {error}", file=sys.stderr)
        return EXIT_INVALID_BLOCK
    for name, text in writes.items():
        if args.check:
            print(f"would update {name}")
            continue
        target = repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        print(f"updated {name}")
    if not writes:
        print("The shared files are up to date.")
    return EXIT_CHANGES if args.check and writes else EXIT_OK
