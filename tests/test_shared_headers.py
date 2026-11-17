"""Shared sources have placeholders rendered with the installed version."""

from __future__ import annotations

from standards.shared import (
    BASE_FILE,
    PR_TEMPLATE,
    VERSION_TOKEN,
    base_block,
    copied_files,
    package_version,
    shared_root,
    shared_text,
)

RULE_HEADER = f"<!-- agent-standards v{VERSION_TOKEN}"
BASE_HEADER = f"<!-- agent-standards:base v{VERSION_TOKEN}"


def test_every_rule_file_has_one_version_placeholder() -> None:
    root = shared_root()
    rules = [name for name in copied_files(root) if name != PR_TEMPLATE]
    assert rules
    for name in rules:
        source = (root / name).read_text()
        assert RULE_HEADER in source
        assert source.count(VERSION_TOKEN) == 1
        rendered = shared_text(root, name)
        assert f"<!-- agent-standards v{package_version()}" in rendered
        assert VERSION_TOKEN not in rendered


def test_base_block_renders_installed_version() -> None:
    source = (shared_root() / BASE_FILE).read_text()
    assert source.startswith(BASE_HEADER)
    assert source.count(VERSION_TOKEN) == 1
    assert base_block(shared_root()).startswith(
        f"<!-- agent-standards:base v{package_version()}"
    )
