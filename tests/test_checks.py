"""Each check against a real git repository with a base and a head commit."""

from __future__ import annotations

from collections.abc import Callable

from conftest import Repo
from standards.constants import Check
from standards.findings import Finding
from standards.run import collect


def checks(repo: Repo, base: str) -> list[Finding]:
    findings, _ = collect(repo.root, base)
    return findings


def of(findings: list[Finding], check: Check) -> list[Finding]:
    return [f for f in findings if f.check is check]


def long_function(lines: int) -> str:
    body = "\n".join(f"  const v{i} = {i};" for i in range(lines - 2))
    return f"export function big() {{\n{body}\n}}\n"


def test_clean_change_has_no_findings(repo: Repo) -> None:
    base = repo.commit()
    repo.write("src/a.ts", "export const ok = 1;\n")
    repo.commit()
    assert checks(repo, base) == []


def test_new_long_function_is_reported_but_existing_debt_is_not(repo: Repo) -> None:
    repo.write("src/old.ts", long_function(60))
    base = repo.commit()
    repo.write("src/old.ts", long_function(60) + "export const x = 1;\n")
    repo.write("src/new.ts", long_function(55))
    repo.commit()
    found = of(checks(repo, base), Check.FUNCTION_SIZE)
    assert [(f.path, f.line) for f in found] == [("src/new.ts", 1)]


def test_growing_an_oversized_function_is_reported(repo: Repo) -> None:
    repo.write("src/old.ts", long_function(60))
    base = repo.commit()
    repo.write("src/old.ts", long_function(61))
    repo.commit()
    [finding] = of(checks(repo, base), Check.FUNCTION_SIZE)
    assert "grew from 60" in finding.message


def test_size_exception_is_reported_but_not_blocking(repo: Repo) -> None:
    base = repo.commit()
    repo.write("src/big.ts", "\n".join(f"export const v{i} = {i};" for i in range(310)))
    repo.write("size-exceptions.txt", "src/big.ts  # generated table\nsrc/other.ts\n")
    repo.commit()
    findings = checks(repo, base)
    [size] = of(findings, Check.FILE_SIZE)
    assert size.blocking is False
    [missing_reason] = of(findings, Check.SIZE_EXCEPTIONS)
    assert missing_reason.line == 2


def test_literal_check_only_reports_added_comparisons(repo: Repo) -> None:
    repo.write("src/a.py", 'def f(s):\n    return s == "old"\n')
    base = repo.commit()
    repo.write("src/a.py", 'def f(s):\n    return s == "old" or s == "new"\n')
    repo.write("tests/test_a.py", 'def test():\n    assert "x" == "x"\n')
    repo.commit()
    found = of(checks(repo, base), Check.LITERAL)
    assert [(f.path, f.line, f.message) for f in found] == [
        ("src/a.py", 2, 'Compares against the literal "new".')
    ]


def test_new_duplicate_constant_is_reported_unless_marked(repo: Repo) -> None:
    repo.write("src/a.py", 'STATUS = "paid"\n')
    repo.write("src/old.py", 'OLD_A = "same"\nOLD_B = "same"\n')
    base = repo.commit()
    repo.write(
        "src/b.py",
        'PAID = "paid"\n# same-value: a tab name, not a status\nTAB = "paid"\n',
    )
    repo.commit()
    found = of(checks(repo, base), Check.DUPLICATE_VALUE)
    assert [(f.path, f.line) for f in found] == [("src/b.py", 1)]


def test_added_suppression_is_reported(repo: Repo) -> None:
    repo.write("src/a.ts", "// @ts-ignore\nexport const a = 1;\n")
    base = repo.commit()
    repo.write("src/a.ts", "// @ts-ignore\nexport const a: any = 1;\n")
    repo.commit()
    [finding] = of(checks(repo, base), Check.SUPPRESSION)
    assert "`any`" in finding.message


def test_unpinned_action_in_a_changed_workflow(repo: Repo) -> None:
    base = repo.commit()
    repo.write(
        ".github/workflows/ci.yml",
        "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1\n"
        "      - uses: ./local-action\n",
    )
    repo.commit()
    [finding] = of(checks(repo, base), Check.PINNED_ACTION)
    assert (finding.line, "actions/checkout@v4" in finding.message) == (6, True)


def test_pr_title(repo: Repo, event: Callable[..., None]) -> None:
    base = repo.commit()
    event({"pull_request": {"title": "Fix things", "base": {"sha": base}}})
    [finding] = of(collect(repo.root, None)[0], Check.PR_TITLE)
    assert "GHOST-<number>" in finding.message
    event({"pull_request": {"title": "GHOST-47 Compare armour", "base": {"sha": base}}})
    assert of(collect(repo.root, None)[0], Check.PR_TITLE) == []


def test_release_tag_must_match_version_file(
    repo: Repo, event: Callable[..., None]
) -> None:
    repo.commit()
    event({}, ref="refs/tags/v1.2.4")
    [finding] = of(collect(repo.root, None)[0], Check.RELEASE_TAG)
    assert "1.2.4" in finding.message and "1.2.3" in finding.message
    event({}, ref="refs/tags/v1.2.3")
    assert of(collect(repo.root, None)[0], Check.RELEASE_TAG) == []


def test_without_a_base_the_ratchets_are_skipped(repo: Repo) -> None:
    repo.write("src/new.ts", long_function(80))
    repo.commit()
    findings, notes = collect(repo.root, None)
    assert findings == [] and "skipped" in notes[0]
