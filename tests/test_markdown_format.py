"""`just check` keeps every shared Markdown file in Prettier's default format,
with one pinned Prettier, so a repository's own Prettier accepts the copies."""

from __future__ import annotations

import re
import shlex
from pathlib import Path

from standards.shared import BASE_FILE, MARKDOWN_GLOB, copied_files

ROOT = Path(__file__).parents[1]
JUSTFILE = ROOT / "justfile"
ISSUE_TEMPLATE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
TEMPLATES_DIR = ROOT / "templates"
# A justfile variable, `name := "value"`, and a recipe's header line, `name:`.
VARIABLE = re.compile(r'^(\w+) := "(.*)"$', re.MULTILINE)
RECIPE_HEADER = "{name}:"
RECIPE_INDENT = "    "
PRETTIER_VARIABLE = "prettier"
FILES_VARIABLE = "shared_markdown"
PINNED_PRETTIER = re.compile(r"\bprettier@\d+\.\d+\.\d+ ")
CHECK_RECIPE = "check"
FIX_RECIPE = "fix"
CHECK_COMMAND = "{{prettier}} --check {{shared_markdown}}"
FIX_COMMAND = "{{prettier}} --write {{shared_markdown}}"


def justfile_text() -> str:
    return JUSTFILE.read_text(encoding="utf-8")


def variables() -> dict[str, str]:
    return dict(VARIABLE.findall(justfile_text()))


def recipe_lines(name: str) -> list[str]:
    """The commands of one recipe, without their indentation."""
    lines = justfile_text().splitlines()
    start = lines.index(RECIPE_HEADER.format(name=name)) + 1
    body = []
    for line in lines[start:]:
        if not line.startswith(RECIPE_INDENT):
            break
        body.append(line.strip())
    return body


def test_prettier_is_pinned_to_an_exact_version() -> None:
    assert PINNED_PRETTIER.search(variables()[PRETTIER_VARIABLE])


def test_check_and_fix_run_the_same_prettier_on_the_shared_markdown() -> None:
    assert CHECK_COMMAND in recipe_lines(CHECK_RECIPE)
    assert FIX_COMMAND in recipe_lines(FIX_RECIPE)


def test_every_shared_file_and_template_is_formatted() -> None:
    patterns = shlex.split(variables()[FILES_VARIABLE])
    covered = {path for pattern in patterns for path in ROOT.glob(pattern)}
    shared = [ROOT / BASE_FILE] + [ROOT / name for name in copied_files(ROOT, None)]
    issue_templates = ISSUE_TEMPLATE_DIR.glob(MARKDOWN_GLOB)
    templates = TEMPLATES_DIR.rglob(MARKDOWN_GLOB)
    expected = {*shared, *issue_templates, *templates}
    assert expected
    assert expected - covered == set()
