"""Find comparisons and switch cases on string literals, and constants
defined with a string value (code.md, Names over literals)."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from tree_sitter import Node

from standards.constants import SAME_VALUE_MARKER, Language
from standards.node_types import EQUALITY_OPERATORS, Cs, CsToken, Py, Ts, TsToken
from standards.syntax import (
    COMMENT_TYPES,
    STRING_TYPES,
    field_text,
    line_of,
    parse,
    string_value,
    text,
    walk,
)

_OPERATOR = "operator"
_LEFT = "left"
_RIGHT = "right"
_VALUE = "value"
_NAME = "name"
_KEY = "key"
_MAIN_GUARD = frozenset({"__name__", "__main__"})
# Type checkers narrow on these only when compared with a literal.
_PLATFORM_OPERANDS = frozenset({"sys.platform", "os.name", "process.platform"})
_PY_CONTAINERS = frozenset({Py.TUPLE, Py.LIST, Py.SET})


@dataclass(frozen=True)
class LiteralUse:
    """A string literal used as a comparison operand or a case label."""

    value: str
    line: int


@dataclass(frozen=True)
class ConstantDef:
    """A named constant or enum member defined with a string value."""

    name: str
    value: str
    line: int
    marked: bool


def _strings(nodes: Iterator[Node] | list[Node]) -> Iterator[Node]:
    for node in nodes:
        if node.type in STRING_TYPES and string_value(node):
            yield node


def _python_uses(node: Node) -> Iterator[Node]:
    if node.type == Py.CASE_PATTERN:
        yield from _strings(walk(node))
        return
    if node.type != Py.COMPARISON:
        return
    operands = node.named_children
    if {text(n).strip("'\"") for n in operands} == _MAIN_GUARD:
        return
    if any(text(n) in _PLATFORM_OPERANDS for n in operands):
        return
    for operand in operands:
        if operand.type in _PY_CONTAINERS:
            yield from _strings(operand.named_children)
        else:
            yield from _strings([operand])


def _is_typeof(node: Node | None) -> bool:
    return (
        node is not None
        and node.type == Ts.UNARY
        and field_text(node, _OPERATOR) == TsToken.TYPEOF
    )


def _ts_uses(node: Node) -> Iterator[Node]:
    if node.type == Ts.SWITCH_CASE:
        value = node.child_by_field_name(_VALUE)
        yield from _strings([value] if value is not None else [])
        return
    if node.type != Ts.BINARY or field_text(node, _OPERATOR) not in EQUALITY_OPERATORS:
        return
    left, right = node.child_by_field_name(_LEFT), node.child_by_field_name(_RIGHT)
    if _is_typeof(left) or _is_typeof(right):
        return
    if any(n is not None and text(n) in _PLATFORM_OPERANDS for n in (left, right)):
        return
    yield from _strings([n for n in (left, right) if n is not None])


def _cs_uses(node: Node) -> Iterator[Node]:
    if node.type == Cs.CONSTANT_PATTERN:
        yield from _strings(node.named_children)
        return
    if node.type == Cs.BINARY and field_text(node, _OPERATOR) in EQUALITY_OPERATORS:
        yield from _strings(node.named_children)


_USES = {
    Language.PYTHON: _python_uses,
    Language.TYPESCRIPT: _ts_uses,
    Language.TSX: _ts_uses,
    Language.JAVASCRIPT: _ts_uses,
    Language.CSHARP: _cs_uses,
}


def literal_comparisons(language: Language, source: str) -> list[LiteralUse]:
    """Every string literal compared against or used as a case label."""
    finder = _USES[language]
    uses = []
    for node in walk(parse(language, source)):
        for literal in finder(node):
            uses.append(LiteralUse(string_value(literal) or "", line_of(literal)))
    return uses


def _marker_rows(root: Node) -> set[int]:
    return {
        node.start_point[0]
        for node in walk(root)
        if node.type in COMMENT_TYPES and SAME_VALUE_MARKER in text(node)
    }


def _python_constants(root: Node) -> Iterator[tuple[str, Node]]:
    for node in walk(root):
        if node.type != Py.ASSIGNMENT or node.parent is None:
            continue
        statement = node.parent
        if not _python_constant_scope(statement):
            continue
        name, value = node.child_by_field_name(_LEFT), node.child_by_field_name(_RIGHT)
        if name is None or value is None or name.type != Py.IDENTIFIER:
            continue
        if text(name).isupper() and value.type in STRING_TYPES:
            yield _python_owner(statement) + text(name), value


def _python_constant_scope(statement: Node) -> bool:
    """Constants live at module level or in a class body, not in functions."""
    scope = statement.parent
    if scope is None:
        return False
    if scope.type == Py.MODULE:
        return True
    return (
        scope.type == Py.BLOCK
        and scope.parent is not None
        and scope.parent.type == Py.CLASS
    )


def _python_owner(statement: Node) -> str:
    block = statement.parent
    owner = block.parent if block is not None else None
    if owner is not None and owner.type == Py.CLASS:
        return f"{field_text(owner, _NAME)}."
    return ""


def _ts_top_level(declaration: Node) -> bool:
    parent = declaration.parent
    if parent is not None and parent.type == Ts.EXPORT:
        parent = parent.parent
    return parent is not None and parent.type == Ts.PROGRAM


def _ts_constants(root: Node) -> Iterator[tuple[str, Node]]:
    for node in walk(root):
        if node.type == Ts.ENUM_ASSIGNMENT:
            value = node.child_by_field_name(_VALUE)
            if value is not None and value.type in STRING_TYPES:
                yield field_text(node, _NAME) or "", value
        if node.type != Ts.VARIABLE_DECLARATOR or node.parent is None:
            continue
        declaration = node.parent
        is_const = (
            declaration.child(0) is not None
            and text(declaration.child(0)) == TsToken.CONST
        )
        value = node.child_by_field_name(_VALUE)
        if not (is_const and _ts_top_level(declaration)) or value is None:
            continue
        name = field_text(node, _NAME) or ""
        if value.type in STRING_TYPES:
            yield name, value
        elif value.type == Ts.AS_EXPRESSION and value.named_children:
            yield from _ts_object_members(name, value.named_children[0])


def _ts_object_members(owner: str, obj: Node) -> Iterator[tuple[str, Node]]:
    if obj.type != Ts.OBJECT:
        return
    for pair in obj.named_children:
        value = pair.child_by_field_name(_VALUE)
        if pair.type == Ts.PAIR and value is not None and value.type in STRING_TYPES:
            yield f"{owner}.{field_text(pair, _KEY)}", value


def _cs_is_constant(field: Node) -> bool:
    modifiers = {text(m) for m in field.named_children if m.type == Cs.MODIFIER}
    return CsToken.CONST in modifiers or {CsToken.STATIC, CsToken.READONLY} <= modifiers


def _cs_constants(root: Node) -> Iterator[tuple[str, Node]]:
    for node in walk(root):
        if node.type != Cs.FIELD or not _cs_is_constant(node):
            continue
        for declarator in walk(node):
            if declarator.type != Cs.VARIABLE_DECLARATOR:
                continue
            values = [c for c in declarator.named_children if c.type in STRING_TYPES]
            if values:
                yield field_text(declarator, _NAME) or "", values[0]


_CONSTANTS = {
    Language.PYTHON: _python_constants,
    Language.TYPESCRIPT: _ts_constants,
    Language.TSX: _ts_constants,
    Language.JAVASCRIPT: _ts_constants,
    Language.CSHARP: _cs_constants,
}


def constant_definitions(language: Language, source: str) -> list[ConstantDef]:
    """Every constant or enum member whose value is a fixed string."""
    root = parse(language, source)
    markers = _marker_rows(root)
    defs = []
    for name, value_node in _CONSTANTS[language](root):
        value = string_value(value_node)
        if not value:
            continue
        row = value_node.start_point[0]
        marked = row in markers or row - 1 in markers
        defs.append(ConstantDef(name, value, line_of(value_node), marked))
    return defs
