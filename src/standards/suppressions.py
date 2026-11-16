"""Count type and lint suppressions per file (code.md, Types). CI only
lets the count go down. A suppression with an `allow-suppression: <why>`
comment on its line, or the line above, is deliberate and not counted."""

from __future__ import annotations

import re
from collections import Counter
from enum import StrEnum

from tree_sitter import Node

from standards.constants import ALLOW_SUPPRESSION_MARKER, Language
from standards.node_types import Cs, CsToken, Py, SyntaxField, Ts, TsToken
from standards.syntax import COMMENT_TYPES, field_text, parse, text, walk


class Suppression(StrEnum):
    """Kinds of suppression the checks count."""

    PY_ANY = "Any"
    PY_TYPE_IGNORE = "# type: ignore"
    PY_NOQA = "# noqa"
    PY_PYLINT = "# pylint: disable"
    TS_ANY = TsToken.ANY
    TS_IGNORE = "@ts-ignore"
    TS_NOCHECK = "@ts-nocheck"
    TS_EXPECT_ERROR = "@ts-expect-error"
    ESLINT_DISABLE = "eslint-disable"
    CS_PRAGMA = "#pragma warning disable"
    CS_SUPPRESS_MESSAGE = "[SuppressMessage]"


# `allow-suppression:` followed by a reason; the marker alone exempts nothing.
ALLOWED_WITH_REASON = re.compile(rf"{re.escape(ALLOW_SUPPRESSION_MARKER)}\s*\S")

# Suppressions written as comments, matched inside the comment text.
# eslint-disable also matches its -line and -next-line forms.
TYPE_IGNORE_COMMENT = re.compile(r"type:\s*ignore")
NOQA_COMMENT = re.compile(r"\bnoqa\b")
PYLINT_DISABLE_COMMENT = re.compile(r"pylint:\s*disable")
TS_IGNORE_COMMENT = re.compile(r"@ts-ignore\b")
TS_NOCHECK_COMMENT = re.compile(r"@ts-nocheck\b")
TS_EXPECT_ERROR_COMMENT = re.compile(r"@ts-expect-error\b")
ESLINT_DISABLE_COMMENT = re.compile(r"eslint-disable")

_TS_COMMENT_PATTERNS = {
    Suppression.TS_IGNORE: TS_IGNORE_COMMENT,
    Suppression.TS_NOCHECK: TS_NOCHECK_COMMENT,
    Suppression.TS_EXPECT_ERROR: TS_EXPECT_ERROR_COMMENT,
    Suppression.ESLINT_DISABLE: ESLINT_DISABLE_COMMENT,
}
_COMMENT_PATTERNS: dict[Language, dict[Suppression, re.Pattern[str]]] = {
    Language.PYTHON: {
        Suppression.PY_TYPE_IGNORE: TYPE_IGNORE_COMMENT,
        Suppression.PY_NOQA: NOQA_COMMENT,
        Suppression.PY_PYLINT: PYLINT_DISABLE_COMMENT,
    },
    Language.TYPESCRIPT: _TS_COMMENT_PATTERNS,
    Language.TSX: _TS_COMMENT_PATTERNS,
    Language.JAVASCRIPT: _TS_COMMENT_PATTERNS,
    Language.CSHARP: {},
}


def _inside_import(node: Node) -> bool:
    parent = node.parent
    while parent is not None:
        if parent.type == Py.IMPORT_FROM:
            return True
        parent = parent.parent
    return False


def _python_suppression(node: Node) -> Suppression | None:
    is_any = node.type == Py.IDENTIFIER and text(node) == Suppression.PY_ANY
    return Suppression.PY_ANY if is_any and not _inside_import(node) else None


def _csharp_suppression(node: Node) -> Suppression | None:
    if node.type == Cs.PRAGMA:
        tokens = {text(c) for c in node.children}
        disables = {CsToken.WARNING, CsToken.DISABLE} <= tokens
        return Suppression.CS_PRAGMA if disables else None
    name = field_text(node, SyntaxField.NAME) if node.type == Cs.ATTRIBUTE else None
    if name in (CsToken.SUPPRESS_MESSAGE, CsToken.SUPPRESS_MESSAGE_ATTRIBUTE):
        return Suppression.CS_SUPPRESS_MESSAGE
    return None


def _typescript_suppression(node: Node) -> Suppression | None:
    is_any = node.type == Ts.PREDEFINED_TYPE and text(node) == TsToken.ANY
    return Suppression.TS_ANY if is_any else None


_NODE_SUPPRESSIONS = {
    Language.PYTHON: _python_suppression,
    Language.CSHARP: _csharp_suppression,
    Language.TYPESCRIPT: _typescript_suppression,
    Language.TSX: _typescript_suppression,
    Language.JAVASCRIPT: _typescript_suppression,
}


def _allowed_rows(root: Node) -> set[int]:
    """Rows a reasoned `allow-suppression:` comment covers: its own rows and
    the row after it."""
    rows: set[int] = set()
    for node in walk(root):
        if node.type in COMMENT_TYPES and ALLOWED_WITH_REASON.search(text(node)):
            rows.update(range(node.start_point[0], node.end_point[0] + 2))
    return rows


def _found(language: Language, node: Node) -> list[Suppression]:
    if node.type in COMMENT_TYPES:
        body = text(node)
        patterns = _COMMENT_PATTERNS[language]
        return [kind for kind, pattern in patterns.items() if pattern.search(body)]
    found = _NODE_SUPPRESSIONS[language](node)
    return [found] if found is not None else []


def count_suppressions(language: Language, source: str) -> Counter[Suppression]:
    """How many suppressions of each kind the file has, leaving out the
    ones marked as deliberate."""
    root = parse(language, source)
    allowed = _allowed_rows(root)
    counts: Counter[Suppression] = Counter()
    for node in walk(root):
        if node.start_point[0] not in allowed:
            counts.update(_found(language, node))
    return counts
