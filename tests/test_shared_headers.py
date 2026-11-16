"""Every shared file names its version in a header, so each repository's
copies show which agent-standards release they came from (workflow.md)."""

from __future__ import annotations

from standards.shared import BASE_FILE, PR_TEMPLATE, copied_files, shared_root

RULE_HEADER = "<!-- agent-standards v"
BASE_HEADER = "<!-- agent-standards:base v"


def test_every_rule_file_has_the_version_header() -> None:
    root = shared_root()
    rules = [name for name in copied_files(root) if name != PR_TEMPLATE]
    missing = [name for name in rules if RULE_HEADER not in (root / name).read_text()]
    assert rules and missing == []


def test_the_base_block_starts_with_its_version_header() -> None:
    assert (shared_root() / BASE_FILE).read_text().startswith(BASE_HEADER)
