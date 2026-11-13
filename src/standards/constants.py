"""Fixed values shared by every check: modes, check names, languages,
limits and the rule documents each finding points to."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

RULES_DIR = "docs/agent/rules"
PROJECT_FILE = "project.yml"
SIZE_EXCEPTIONS_FILE = "size-exceptions.txt"
SAME_VALUE_MARKER = "same-value:"
COMMENT_PREFIX = "#"
NULL_SHA = "0" * 40
TAG_REF_PREFIX = "refs/tags/v"


class Mode(StrEnum):
    """How findings are reported: as warnings, or as errors that fail."""

    WARN = "warn"
    FAIL = "fail"


class Check(StrEnum):
    """One name per check, used in annotations and the summary."""

    PROJECT = PROJECT_FILE
    PR_TITLE = "PR title"
    FILE_SIZE = "File size"
    FUNCTION_SIZE = "Function size"
    LITERAL = "Literal comparison"
    DUPLICATE_VALUE = "Duplicate constant value"
    SUPPRESSION = "Suppressions"
    PINNED_ACTION = "Pinned actions"
    RELEASE_TAG = "Release tag"
    SIZE_EXCEPTIONS = SIZE_EXCEPTIONS_FILE


class Rule(StrEnum):
    """Where each rule is explained, relative to the repository root."""

    PROJECT = "project.example.yml in agent-standards"
    WORKFLOW = f"{RULES_DIR}/workflow.md"
    THRESHOLDS = f"{RULES_DIR}/thresholds.md"
    CODE = f"{RULES_DIR}/code.md"
    DEPENDENCIES = f"{RULES_DIR}/dependencies.md"


class Language(StrEnum):
    """Languages the code checks understand."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    TSX = "tsx"
    JAVASCRIPT = "javascript"
    CSHARP = "csharp"


class Unit(StrEnum):
    """What a size limit counts."""

    LINES = "lines"
    CODE_LINES = "lines of code"
    STATEMENTS = "statements"


EXTENSIONS: dict[str, Language] = {
    ".py": Language.PYTHON,
    ".ts": Language.TYPESCRIPT,
    ".mts": Language.TYPESCRIPT,
    ".cts": Language.TYPESCRIPT,
    ".tsx": Language.TSX,
    ".js": Language.JAVASCRIPT,
    ".jsx": Language.JAVASCRIPT,
    ".mjs": Language.JAVASCRIPT,
    ".cjs": Language.JAVASCRIPT,
    ".cs": Language.CSHARP,
}

# Type declarations are generated or describe external code.
SKIPPED_SUFFIXES = (".d.ts",)


@dataclass(frozen=True)
class Limit:
    """A size limit: how many units are allowed."""

    value: int
    unit: Unit


@dataclass(frozen=True)
class Limits:
    """File and function limits of one language (thresholds.md)."""

    file: Limit
    function: Limit


_TS_LIMITS = Limits(Limit(300, Unit.LINES), Limit(50, Unit.LINES))

LIMITS: dict[Language, Limits] = {
    Language.PYTHON: Limits(Limit(1000, Unit.LINES), Limit(50, Unit.STATEMENTS)),
    Language.TYPESCRIPT: _TS_LIMITS,
    Language.TSX: _TS_LIMITS,
    Language.JAVASCRIPT: _TS_LIMITS,
    Language.CSHARP: Limits(Limit(1000, Unit.CODE_LINES), Limit(80, Unit.CODE_LINES)),
}

# Paths whose literals are test data, not program values (code.md).
TEST_PATH_PARTS = ("tests", "test", "__tests__", "Tests")
TEST_NAME_PATTERNS = ("test_*.py", "*_test.py", "*.test.*", "*.spec.*", "*Tests.cs")
