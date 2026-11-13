"""Parse source files with tree-sitter and answer small questions about
the tree: which language a path is, which lines hold code, what a string
literal's value is."""

from __future__ import annotations

from collections.abc import Iterator
from fnmatch import fnmatch
from functools import cache
from pathlib import PurePosixPath

import tree_sitter_c_sharp
import tree_sitter_javascript
import tree_sitter_python
import tree_sitter_typescript
from tree_sitter import Language as TsLanguage
from tree_sitter import Node, Parser

from standards.constants import (
    EXTENSIONS,
    SKIPPED_SUFFIXES,
    TEST_NAME_PATTERNS,
    TEST_PATH_PARTS,
    Language,
)
from standards.node_types import Cs, Py, Ts

_GRAMMARS = {
    Language.PYTHON: tree_sitter_python.language,
    Language.TYPESCRIPT: tree_sitter_typescript.language_typescript,
    Language.TSX: tree_sitter_typescript.language_tsx,
    Language.JAVASCRIPT: tree_sitter_javascript.language,
    Language.CSHARP: tree_sitter_c_sharp.language,
}

COMMENT_TYPES = frozenset({Py.COMMENT, Ts.COMMENT, Cs.COMMENT})
_INTERPOLATIONS = frozenset({Py.INTERPOLATION, Ts.TEMPLATE_SUBSTITUTION})
_STRING_PARTS = frozenset(
    {
        Py.STRING_CONTENT,
        Py.ESCAPE,
        Ts.STRING_FRAGMENT,
        Cs.STRING_CONTENT,
        Cs.RAW_CONTENT,
    }
)
STRING_TYPES = frozenset({Py.STRING, Ts.TEMPLATE, Cs.STRING, Cs.VERBATIM, Cs.RAW})
_VERBATIM_PREFIX = '@"'
_QUOTE = '"'


def language_for(path: str) -> Language | None:
    """The language of a file from its extension, or None to skip it."""
    if path.endswith(SKIPPED_SUFFIXES):
        return None
    return EXTENSIONS.get(PurePosixPath(path).suffix)


def is_test_path(path: str) -> bool:
    """Test files hold test data, which the literal rules do not cover."""
    pure = PurePosixPath(path)
    if any(part in TEST_PATH_PARTS for part in pure.parts[:-1]):
        return True
    return any(fnmatch(pure.name, pattern) for pattern in TEST_NAME_PATTERNS)


@cache
def _parser(language: Language) -> Parser:
    return Parser(TsLanguage(_GRAMMARS[language]()))


def parse(language: Language, source: str) -> Node:
    """The root node of a source file."""
    return _parser(language).parse(source.encode("utf-8")).root_node


def walk(node: Node) -> Iterator[Node]:
    """Every node under (and including) this one, depth first."""
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed(current.children))


def text(node: Node) -> str:
    """The source text of a node."""
    return (node.text or b"").decode("utf-8", errors="replace")


def line_of(node: Node) -> int:
    """1-based line where the node starts."""
    return node.start_point[0] + 1


def code_rows(root: Node) -> set[int]:
    """0-based rows that hold at least one token that is not a comment."""
    rows: set[int] = set()
    for node in walk(root):
        if node.type in COMMENT_TYPES:
            continue
        if node.child_count == 0 and node.end_byte > node.start_byte:
            rows.update(range(node.start_point[0], node.end_point[0] + 1))
    return rows


def string_value(node: Node) -> str | None:
    """A string literal's value, or None when it is built at run time."""
    if any(child.type in _INTERPOLATIONS for child in node.children):
        return None
    if node.type == Cs.VERBATIM:
        return text(node).removeprefix(_VERBATIM_PREFIX).removesuffix(_QUOTE)
    return "".join(text(c) for c in node.children if c.type in _STRING_PARTS)


def field_text(node: Node, name: str) -> str | None:
    """Text of a named field of the node, if present."""
    child = node.child_by_field_name(name)
    return text(child) if child is not None else None
