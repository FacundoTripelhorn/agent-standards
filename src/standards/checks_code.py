"""Ratchet checks on changed source files: size, literal comparisons and
suppressions. Each compares the file at HEAD with the same file at the
base commit, so existing debt is reported only when it grows."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from standards.constants import (
    COMMENT_PREFIX,
    LIMITS,
    SIZE_EXCEPTIONS_FILE,
    Check,
    Language,
    Rule,
)
from standards.context import Context
from standards.findings import Finding
from standards.gitio import Change, show
from standards.literals import literal_comparisons
from standards.metrics import file_size, function_sizes
from standards.suppressions import count_suppressions
from standards.syntax import is_test_path, language_for

_SPLIT_FIX = (
    "Move code out into a new module or function first, or list the file in "
    f"{SIZE_EXCEPTIONS_FILE} with a reason."
)


def _sources(context: Context, change: Change) -> tuple[str, str | None]:
    head = (context.repo / change.path).read_text(encoding="utf-8", errors="replace")
    base = None
    if context.base and change.base_path:
        base = show(context.repo, context.base, change.base_path)
    return head, base


def load_size_exceptions(repo: Path) -> tuple[set[str], list[Finding]]:
    """Paths listed in size-exceptions.txt, and entries without a reason."""
    path = repo / SIZE_EXCEPTIONS_FILE
    if not path.is_file():
        return set(), []
    paths: set[str] = set()
    findings = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        entry, _, reason = line.partition(COMMENT_PREFIX)
        if not entry.strip():
            continue
        paths.add(entry.strip())
        if not reason.strip():
            findings.append(
                Finding(
                    Check.SIZE_EXCEPTIONS,
                    f"`{entry.strip()}` has no reason.",
                    "Add `# <why this file may stay large>` after the path.",
                    Rule.THRESHOLDS,
                    SIZE_EXCEPTIONS_FILE,
                    number,
                )
            )
    return paths, findings


def _file_finding(
    change: Change, language: Language, sizes: tuple[int, int | None], excepted: bool
) -> Finding | None:
    head, base = sizes
    limit = LIMITS[language].file
    if head <= limit.value or (base is not None and head <= base):
        return None
    grew = "a new file" if base is None else f"it grew from {base}"
    return Finding(
        Check.FILE_SIZE,
        f"`{change.path}` has {head} {limit.unit.value} ({grew}); "
        f"the limit is {limit.value}.",
        _SPLIT_FIX,
        Rule.THRESHOLDS,
        change.path,
        blocking=not excepted,
    )


def _function_findings(
    change: Change, language: Language, head: str, base: str | None, excepted: bool
) -> list[Finding]:
    limit = LIMITS[language].function
    before = {f.key: f.size for f in function_sizes(language, base)} if base else {}
    findings = []
    for fn in function_sizes(language, head):
        old = before.get(fn.key)
        if fn.size <= limit.value or (old is not None and fn.size <= old):
            continue
        grew = "new" if old is None else f"grew from {old}"
        findings.append(
            Finding(
                Check.FUNCTION_SIZE,
                f"`{fn.key}` has {fn.size} {limit.unit.value} ({grew}); "
                f"the limit is {limit.value}.",
                "Extract named helpers so each function does one thing.",
                Rule.THRESHOLDS,
                change.path,
                fn.line,
                blocking=not excepted,
            )
        )
    return findings


def check_size(context: Context) -> list[Finding]:
    """Files and functions stay under their limits, or do not grow."""
    exceptions, findings = load_size_exceptions(context.repo)
    for change in context.changes:
        language = language_for(change.path)
        if language is None:
            continue
        head, base = _sources(context, change)
        excepted = change.path in exceptions
        sizes = (file_size(language, head), file_size(language, base) if base else None)
        file_finding = _file_finding(change, language, sizes, excepted)
        if file_finding:
            findings.append(file_finding)
        # A test suite is one long callback (`describe`); only its file size counts.
        if not is_test_path(change.path):
            findings += _function_findings(change, language, head, base, excepted)
    return findings


def check_literals(context: Context) -> list[Finding]:
    """No new comparisons or case labels on string literals."""
    findings = []
    for change in context.changes:
        language = language_for(change.path)
        if language is None or is_test_path(change.path):
            continue
        head, base = _sources(context, change)
        now = literal_comparisons(language, head)
        before = Counter(u.value for u in literal_comparisons(language, base or ""))
        grown = {v for v, n in Counter(u.value for u in now).items() if n > before[v]}
        for use in now:
            if use.value in grown and use.line in change.added_lines:
                findings.append(
                    Finding(
                        Check.LITERAL,
                        f'Compares against the literal "{use.value}".',
                        "Use a named constant or enum member for this value.",
                        Rule.CODE,
                        change.path,
                        use.line,
                    )
                )
    return findings


def check_suppressions(context: Context) -> list[Finding]:
    """The number of each kind of suppression in a file does not go up."""
    findings = []
    for change in context.changes:
        language = language_for(change.path)
        if language is None:
            continue
        head, base = _sources(context, change)
        now = count_suppressions(language, head)
        before = count_suppressions(language, base or "")
        for kind, count in now.items():
            if count > before[kind]:
                findings.append(
                    Finding(
                        Check.SUPPRESSION,
                        f"Adds {count - before[kind]} `{kind.value}` "
                        f"(now {count}, was {before[kind]}).",
                        "Type the value or fix the warning instead of silencing it.",
                        Rule.CODE,
                        change.path,
                    )
                )
    return findings
