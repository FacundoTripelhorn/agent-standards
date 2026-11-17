"""`standards-sync` and the drift check, on a repository with project.yml."""

from __future__ import annotations

import shutil

import pytest

from conftest import Repo
from standards.check_shared import check_shared_copies, pinned_commit
from standards.constants import Check
from standards.project_config import load_project
from standards.shared import (
    AGENTS_FILE,
    BLOCK_END,
    base_block,
    copied_files,
    shared_root,
    shared_text,
)
from standards.sync import EXIT_INVALID_BLOCK, EXIT_UNSAFE_PATH
from standards.sync import main as sync

PROJECT_PART = "# My project\n\nProject rules.\n"
PIN = "a" * 40


def drift(repo: Repo) -> list[str]:
    project, _ = load_project(repo.root)
    findings = check_shared_copies(repo.root, project)
    assert all(f.check is Check.SHARED_COPY for f in findings)
    return sorted(f.path or "" for f in findings)


def test_sync_writes_every_copy_and_keeps_the_project_part(repo: Repo) -> None:
    repo.write(AGENTS_FILE, PROJECT_PART)
    assert sync(["--repo", str(repo.root)]) == 0
    root = shared_root()
    for name in copied_files(root):
        assert (repo.root / name).read_text() == shared_text(root, name)
    agents = (repo.root / AGENTS_FILE).read_text()
    assert agents == PROJECT_PART + "\n" + base_block(root)
    assert drift(repo) == []


def test_sync_renders_version_from_package_metadata(
    repo: Repo, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("standards.shared.package_version", lambda: "9.9.9")
    assert sync(["--repo", str(repo.root)]) == 0
    assert "v9.9.9" in (repo.root / AGENTS_FILE).read_text()
    assert "v9.9.9" in (repo.root / "docs/agent/rules/code.md").read_text()
    assert drift(repo) == []


def test_sync_twice_changes_nothing_and_check_mode_reports(
    repo: Repo, capsys: pytest.CaptureFixture[str]
) -> None:
    sync(["--repo", str(repo.root)])
    assert sync(["--repo", str(repo.root), "--check"]) == 0
    assert "up to date" in capsys.readouterr().out
    (repo.root / "docs/agent/rules/code.md").write_text("edited\n")
    assert sync(["--repo", str(repo.root), "--check"]) == 1
    assert "would update docs/agent/rules/code.md" in capsys.readouterr().out
    assert (repo.root / "docs/agent/rules/code.md").read_text() == "edited\n"


def test_sync_replaces_an_old_block_in_place(repo: Repo) -> None:
    old = f"<!-- agent-standards:base v0.1 -->\nold rules\n{BLOCK_END}\n"
    repo.write(AGENTS_FILE, PROJECT_PART + "\n" + old + "\n## After\n")
    sync(["--repo", str(repo.root)])
    agents = (repo.root / AGENTS_FILE).read_text()
    assert agents == PROJECT_PART + "\n" + base_block(shared_root()) + "\n## After\n"


def test_drift_reports_edited_missing_and_stale_copies(repo: Repo) -> None:
    sync(["--repo", str(repo.root)])
    (repo.root / "docs/agent/rules/code.md").write_text("edited\n")
    (repo.root / ".github/pull_request_template.md").unlink()
    agents = (repo.root / AGENTS_FILE).read_text()
    repo.write(AGENTS_FILE, agents.replace("## Shared rules", "## Old rules"))
    assert drift(repo) == [
        ".github/pull_request_template.md",
        AGENTS_FILE,
        "docs/agent/rules/code.md",
    ]


def test_windows_line_endings_are_not_drift(repo: Repo) -> None:
    sync(["--repo", str(repo.root)])
    path = repo.root / "docs/agent/rules/code.md"
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert drift(repo) == []


def test_no_block_and_no_project_and_the_origin(repo: Repo) -> None:
    sync(["--repo", str(repo.root)])
    repo.write(AGENTS_FILE, PROJECT_PART)
    assert drift(repo) == [AGENTS_FILE]
    assert check_shared_copies(repo.root, None) == []
    repo.write("AGENTS.base.md", "originals live here\n")
    project, _ = load_project(repo.root)
    assert check_shared_copies(repo.root, project) == []


def test_fix_names_the_pinned_commit(repo: Repo) -> None:
    uses = f"      - uses: FacundoTripelhorn/agent-standards@{PIN}\n"
    repo.write(".github/workflows/ci.yml", "jobs:\n  s:\n    steps:\n" + uses)
    assert pinned_commit(repo.root) == PIN
    (repo.root / "docs/agent/rules/code.md").write_text("edited\n")
    project, _ = load_project(repo.root)
    [first] = check_shared_copies(repo.root, project)
    assert f"agent-standards@{PIN} standards-sync" in first.fix


@pytest.mark.parametrize(
    "broken",
    [
        "<!-- agent-standards:base v0.1 -->\n",
        "<!-- /agent-standards:base -->\n",
        ("<!-- agent-standards:base v0.1 -->\n<!-- /agent-standards:base -->\n") * 2,
    ],
)
def test_invalid_blocks_refuse_to_sync_without_writing(repo: Repo, broken: str) -> None:
    repo.write(AGENTS_FILE, PROJECT_PART + broken)
    path = repo.root / "docs/agent/rules/code.md"
    path.write_text("edited\n")
    assert sync(["--repo", str(repo.root)]) == EXIT_INVALID_BLOCK
    assert path.read_text() == "edited\n"
    project, _ = load_project(repo.root)
    findings = check_shared_copies(repo.root, project)
    assert any("Invalid" in finding.message for finding in findings)


@pytest.mark.parametrize("link", [".github/pull_request_template.md", "docs/agent"])
def test_sync_refuses_a_destination_that_resolves_outside_the_repository(
    repo: Repo, tmp_path_factory: pytest.TempPathFactory, link: str
) -> None:
    outside = tmp_path_factory.mktemp("outside")
    victim = outside / "victim.md"
    victim.write_text("keep me\n")
    target = victim if link.endswith(".md") else outside
    path = repo.root / link
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    path.symlink_to(target)
    (repo.root / AGENTS_FILE).unlink()
    assert sync(["--repo", str(repo.root)]) == EXIT_UNSAFE_PATH
    assert victim.read_text() == "keep me\n"
    assert sorted(p.name for p in outside.iterdir()) == ["victim.md"]
    assert not (repo.root / AGENTS_FILE).exists()


@pytest.mark.parametrize(
    "link", [AGENTS_FILE, ".github/pull_request_template.md", "docs/agent"]
)
def test_internal_symlinks_are_rejected_without_writes(repo: Repo, link: str) -> None:
    other = repo.root / "unrelated"
    other.mkdir()
    (other / "note.md").write_text("keep me\n")
    path = repo.root / link
    if path.is_dir():
        shutil.rmtree(path)
        target = other
    else:
        path.unlink()
        target = other / "note.md"
    path.symlink_to(target)
    assert sync(["--repo", str(repo.root)]) == EXIT_UNSAFE_PATH
    assert (other / "note.md").read_text() == "keep me\n"


def test_pinned_commit_ignores_comments_and_conflicts(repo: Repo) -> None:
    repo.write(
        ".github/workflows/a.yml",
        f"# - uses: FacundoTripelhorn/agent-standards@{PIN}\n",
    )
    assert pinned_commit(repo.root) is None
    repo.write(
        ".github/workflows/b.yml",
        f"  - uses: FacundoTripelhorn/agent-standards@{PIN}\n",
    )
    assert pinned_commit(repo.root) == PIN
    repo.write(
        ".github/workflows/c.yml",
        f"  - uses: FacundoTripelhorn/agent-standards@{'b' * 40}\n",
    )
    assert pinned_commit(repo.root) is None
    (repo.root / "docs/agent/rules/code.md").write_text("edited\n")
    project, _ = load_project(repo.root)
    [first] = check_shared_copies(repo.root, project)
    assert "exactly one full-SHA" in first.fix
