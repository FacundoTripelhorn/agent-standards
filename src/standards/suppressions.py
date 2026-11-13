"""Count type and lint suppressions per file (code.md, Types). CI only
lets the count go down."""

from __future__ import annotations

import re
from collections import Counter
from enum import StrEnum

from tree_sitter import Node

from standards.constants import Language
from standards.node_types import Cs, CsToken, Py, Ts, TsToken
from standards.syntax import COMMENT_TYPES, field_text, parse, text, walk

_NAME = "name"
_ANY = "Any"


class Suppression(StrEnum):
    """Kinds of suppression the checks count."""

    PY_ANY = "Any"
    PY_TYPE_IGNORE = "# type: ignore"
    PY_NOQA = "# noqa"
    PY_PYLINT = "# pylint: disable"
    TS_ANY = "any"
    TS_IGNORE = "@ts-ignore"
    TS_NOCHECK = "@ts-nocheck"
    TS_EXPECT_ERROR = "@ts-expect-error"
    ESLINT_DISABLE = "eslint-disable"
    CS_PRAGMA = "#pragma warning disable"
    CS_SUPPRESS_MESSAGE = "[SuppressMessage]"


_COMMENT_PATTERNS: dict[Language, dict[Suppression, re.Pattern[str]]] = {
    Language.PYTHON: {
        Suppression.PY_TYPE_IGNORE: re.compile(r"type:\s*ignore"),
        Suppression.PY_NOQA: re.compile(r"\bnoqa\b"),
        Suppression.PY_PYLINT: re.compile(r"pylint:\s*disable"),
    },
    Language.TYPESCRIPT: {
        Suppression.TS_IGNORE: re.compile(r"@ts-ignore\b"),
        Suppression.TS_NOCHECK: re.compile(r"@ts-nocheck\b"),
        Suppression.TS_EXPECT_ERROR: re.compile(r"@ts-expect-error\b"),
        Suppression.ESLINT_DISABLE: re.compile(r"eslint-disable"),
    },
    Language.CSHARP: {},
}
_COMMENT_PATTERNS[Language.TSX] = _COMMENT_PATTERNS[Language.TYPESCRIPT]
_COMMENT_PATTERNS[Language.JAVASCRIPT] = _COMMENT_PATTERNS[Language.TYPESCRIPT]


def _inside_import(node: Node) -> bool:
    parent = node.parent
    while parent is not None:
        if parent.type == Py.IMPORT_FROM:
            return True
        parent = parent.parent
    return False


def _python_suppression(node: Node) -> Suppression | None:
    is_any = node.type == Py.IDENTIFIER and text(node) == _ANY
    return Suppression.PY_ANY if is_any and not _inside_import(node) else None


def _csharp_suppression(node: Node) -> Suppression | None:
    if node.type == Cs.PRAGMA:
        tokens = {text(c) for c in node.children}
        disables = {CsToken.WARNING, CsToken.DISABLE} <= tokens
        return Suppression.CS_PRAGMA if disables else None
    name = field_text(node, _NAME) if node.type == Cs.ATTRIBUTE else None
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


def count_suppressions(language: Language, source: str) -> Counter[Suppression]:
    """How many suppressions of each kind the file has."""
    counts: Counter[Suppression] = Counter()
    patterns = _COMMENT_PATTERNS[language]
    for node in walk(parse(language, source)):
        if node.type in COMMENT_TYPES:
            body = text(node)
            counts.update(
                kind for kind, pattern in patterns.items() if pattern.search(body)
            )
            continue
        found = _NODE_SUPPRESSIONS[language](node)
        if found is not None:
            counts[found] += 1
    return counts
