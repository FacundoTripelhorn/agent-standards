"""The limits in code and in docs/agent/rules/thresholds.md must agree."""

from __future__ import annotations

import re
from pathlib import Path

from standards.constants import LIMITS, Language

DOC = Path(__file__).parent.parent / "docs/agent/rules/thresholds.md"

ROWS = {
    Language.PYTHON: ("Lines per module", "Statements per function"),
    Language.TYPESCRIPT: ("Lines per file", "Lines per function"),
    Language.CSHARP: ("Lines of code per file", "Lines of code per method"),
}


def documented(label: str) -> int:
    match = re.search(
        rf"^\| {re.escape(label)} \| (\d+) \|", DOC.read_text(), re.MULTILINE
    )
    assert match, f"thresholds.md has no row '{label}'"
    return int(match.group(1))


def test_limits_match_thresholds_doc() -> None:
    for language, (file_row, function_row) in ROWS.items():
        assert LIMITS[language].file.value == documented(file_row)
        assert LIMITS[language].function.value == documented(function_row)
