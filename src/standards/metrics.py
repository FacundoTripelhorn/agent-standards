"""Measure files and functions in the units thresholds.md uses: lines for
Python files and TypeScript, lines of code for C#, statements for Python
functions."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from tree_sitter import Node

from standards.constants import LIMITS, Language, Unit
from standards.node_types import (
    ANONYMOUS,
    STATEMENT_SUFFIX,
    Common,
    Cs,
    Py,
    SyntaxField,
    Ts,
)
from standards.syntax import code_rows, field_text, line_of, parse, walk

_FUNCTIONS: dict[Language, frozenset[str]] = {
    Language.PYTHON: frozenset({Py.FUNCTION}),
    Language.TYPESCRIPT: frozenset(
        {
            Ts.FUNCTION,
            Ts.GENERATOR,
            Ts.FUNCTION_EXPRESSION,
            Ts.FUNCTION_LEGACY,
            Ts.GENERATOR_EXPRESSION,
            Ts.ARROW,
            Ts.METHOD,
        }
    ),
    Language.CSHARP: frozenset(
        {
            Cs.METHOD,
            Cs.CONSTRUCTOR,
            Cs.DESTRUCTOR,
            Cs.OPERATOR,
            Cs.CONVERSION,
            Cs.LOCAL_FUNCTION,
            Cs.ACCESSOR,
        }
    ),
}
_FUNCTIONS[Language.TSX] = _FUNCTIONS[Language.TYPESCRIPT]
_FUNCTIONS[Language.JAVASCRIPT] = _FUNCTIONS[Language.TYPESCRIPT]

_SCOPES = frozenset(
    {
        Py.CLASS,
        Common.CLASS_DECLARATION,
        Ts.CLASS_EXPRESSION,
        Ts.ABSTRACT_CLASS,
        Cs.STRUCT,
        Cs.RECORD,
        Cs.INTERFACE,
        Cs.PROPERTY,
    }
)
_PY_CLAUSES = frozenset({Py.ELIF, Py.ELSE, Py.EXCEPT, Py.FINALLY, Py.CASE})
_PY_STATEMENTS = frozenset({Py.FUNCTION, Py.CLASS})
_PY_COUNTED = _PY_CLAUSES | _PY_STATEMENTS
# A function value takes the name of what it is assigned to.
_NAMING_PARENTS: dict[str, str] = {
    Common.VARIABLE_DECLARATOR: SyntaxField.NAME,
    Ts.PAIR: SyntaxField.KEY,
    Ts.FIELD: SyntaxField.NAME,
    Ts.ASSIGNMENT: SyntaxField.LEFT,
}


@dataclass(frozen=True)
class FunctionSize:
    """A function's identity in its file, where it starts, and its size."""

    key: str
    line: int
    size: int


def file_size(language: Language, source: str) -> int:
    """File length in the unit of its language's file limit."""
    if LIMITS[language].file.unit is Unit.CODE_LINES:
        return len(code_rows(parse(language, source)))
    return len(source.splitlines())


def _own_name(node: Node) -> str:
    name = field_text(node, SyntaxField.NAME)
    if name:
        return name
    parent = node.parent
    if parent is not None and parent.type in _NAMING_PARENTS:
        named = field_text(parent, _NAMING_PARENTS[parent.type])
        if named:
            return named
    return ANONYMOUS if node.type in _FUNCTIONS[Language.TYPESCRIPT] else node.type


def _qualified_name(node: Node, functions: frozenset[str]) -> str:
    parts = [_own_name(node)]
    parent = node.parent
    while parent is not None:
        if parent.type in _SCOPES or parent.type in functions:
            parts.append(_own_name(parent))
        parent = parent.parent
    return ".".join(reversed(parts))


def _python_statements(function: Node) -> int:
    count = 0
    for node in walk(function):
        if node is function:
            continue
        if node.type.endswith(STATEMENT_SUFFIX) or node.type in _PY_COUNTED:
            count += 1
    return count


def _function_size(language: Language, node: Node, rows: set[int]) -> int:
    unit = LIMITS[language].function.unit
    if unit is Unit.STATEMENTS:
        return _python_statements(node)
    if unit is Unit.CODE_LINES:
        span = range(node.start_point[0], node.end_point[0] + 1)
        return sum(1 for row in span if row in rows)
    return node.end_point[0] - node.start_point[0] + 1


def function_sizes(language: Language, source: str) -> list[FunctionSize]:
    """Every function with a stable key: its qualified name, plus an
    ordinal when the same name repeats (overloads, anonymous functions)."""
    root = parse(language, source)
    functions = _FUNCTIONS[language]
    rows = (
        code_rows(root) if LIMITS[language].function.unit is Unit.CODE_LINES else set()
    )
    seen: Counter[str] = Counter()
    sizes = []
    for node in walk(root):
        if not node.is_named or node.type not in functions:
            continue
        name = _qualified_name(node, functions)
        seen[name] += 1
        key = name if seen[name] == 1 else f"{name}#{seen[name]}"
        sizes.append(
            FunctionSize(key, line_of(node), _function_size(language, node, rows))
        )
    return sizes
