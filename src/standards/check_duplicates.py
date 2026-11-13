"""Two constants with the same string value (code.md, One value, one name).
Counted across the whole repository at HEAD and at the base, so only new
duplicates are reported."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from standards.constants import SAME_VALUE_MARKER, Check, Language, Rule
from standards.context import Context
from standards.findings import Finding
from standards.gitio import show, tracked_files
from standards.literals import ConstantDef, constant_definitions
from standards.syntax import is_test_path, language_for

# TypeScript, TSX and JavaScript share values; each other language is apart.
_FAMILY = {
    Language.PYTHON: Language.PYTHON,
    Language.TYPESCRIPT: Language.TYPESCRIPT,
    Language.TSX: Language.TYPESCRIPT,
    Language.JAVASCRIPT: Language.TYPESCRIPT,
    Language.CSHARP: Language.CSHARP,
}

type ValueKey = tuple[Language, str]

# A value is duplicated once two constants hold it.
_DUPLICATE = 2


@dataclass(frozen=True)
class Located:
    """A constant definition and the file it is in."""

    path: str
    definition: ConstantDef


def _definitions(sources: dict[str, str]) -> dict[ValueKey, list[Located]]:
    found: dict[ValueKey, list[Located]] = defaultdict(list)
    for path, source in sources.items():
        language = language_for(path)
        if language is None:
            continue
        for definition in constant_definitions(language, source):
            if not definition.marked:
                key = (_FAMILY[language], definition.value)
                found[key].append(Located(path, definition))
    return found


def _source_paths(paths: list[str]) -> list[str]:
    return [p for p in paths if language_for(p) is not None and not is_test_path(p)]


def _head_sources(context: Context) -> dict[str, str]:
    paths = _source_paths(tracked_files(context.repo))
    return {
        p: (context.repo / p).read_text(encoding="utf-8", errors="replace")
        for p in paths
        if (context.repo / p).is_file()
    }


def _base_sources(context: Context, base: str) -> dict[str, str]:
    sources = {}
    for path in _source_paths(tracked_files(context.repo, base)):
        source = show(context.repo, base, path)
        if source is not None:
            sources[path] = source
    return sources


def _finding(new: Located, others: list[Located]) -> Finding:
    first = others[0]
    where = f"`{first.definition.name}` ({first.path}:{first.definition.line})"
    return Finding(
        Check.DUPLICATE_VALUE,
        f'`{new.definition.name}` has the value "{new.definition.value}", '
        f"like {where}.",
        "Use the existing constant. If they are different concepts that share "
        f"a value, add a `{SAME_VALUE_MARKER} <why>` comment on the line.",
        Rule.CODE,
        new.path,
        new.definition.line,
    )


def check_duplicate_values(context: Context) -> list[Finding]:
    """Report constants added in this change whose value another constant
    already has."""
    if context.base is None:
        return []
    added = {c.path: c.added_lines for c in context.changes}
    if not any(language_for(p) for p in added):
        return []
    now = _definitions(_head_sources(context))
    before = Counter(
        {
            k: len(v)
            for k, v in _definitions(_base_sources(context, context.base)).items()
        }
    )
    findings = []
    for key, defs in now.items():
        if len(defs) < _DUPLICATE or len(defs) <= before[key]:
            continue
        for located in defs:
            if located.definition.line in added.get(located.path, frozenset()):
                others = [d for d in defs if d is not located]
                findings.append(_finding(located, others))
    return findings
