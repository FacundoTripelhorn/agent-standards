"""The shared files every repository keeps a copy of, and where this version's
originals are: bundled in the installed package, or in the source tree."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

from standards.constants import RULES_DIR
from standards.project_config import Tracker

# Inside the installed package, the originals keep their repository paths
# under this folder (pyproject.toml, force-include).
PACKAGED_DIR = "files"
DISTRIBUTION = "agent-standards-checks"
VERSION_TOKEN = "{agent-standards-version}"
BASE_FILE = "AGENTS.base.md"
AGENTS_FILE = "AGENTS.md"
PR_TEMPLATE = ".github/pull_request_template.md"
# Only this template: a repository's other issue templates are its own.
ISSUE_TEMPLATE = ".github/ISSUE_TEMPLATE/work-item.md"
MARKDOWN_GLOB = "*.md"
# The shared block in AGENTS.md starts with a line beginning with
# BLOCK_START and ends with the BLOCK_END line.
BLOCK_START = "<!-- agent-standards:base"
BLOCK_END = "<!-- /agent-standards:base -->"
ACTION_REPOSITORY = "FacundoTripelhorn/agent-standards"
CRLF = "\r\n"
LF = "\n"


def shared_root() -> Path:
    """Where this version's originals are."""
    packaged = Path(__file__).parent / PACKAGED_DIR
    if (packaged / BASE_FILE).is_file():
        return packaged
    source = Path(__file__).resolve().parents[2]
    if (source / BASE_FILE).is_file():
        return source
    raise FileNotFoundError(f"{BASE_FILE} is neither packaged nor in the source tree")


def package_version() -> str:
    """The installed package release."""
    return metadata.version(DISTRIBUTION)


def header_version() -> str:
    """The release line in the copies' headers: MAJOR.MINOR only, so a patch
    release (fixes to the check, no rule changes) leaves every copy as it is."""
    major, minor, *_ = package_version().split(".")
    return f"{major}.{minor}"


def is_origin(repo: Path) -> bool:
    """agent-standards itself holds the originals, not copies."""
    return (repo / BASE_FILE).is_file()


def unsafe_destinations(repo: Path, names: list[str]) -> list[str]:
    """Managed paths that go through a symlink, or resolve outside `repo`
    (which must be resolved). `standards-sync` never writes through them."""
    unsafe = []
    for name in names:
        path = repo
        for component in Path(name).parts:
            path = path / component
            if path.is_symlink():
                unsafe.append(name)
                break
        else:
            if not path.resolve().is_relative_to(repo):
                unsafe.append(name)
    return unsafe


def copied_files(root: Path, tracker: Tracker | None) -> list[str]:
    """Repository paths of the files copied whole. The issue template is for
    GitHub issues, so a repository with `tracker: linear` does not get it;
    one whose tracker is unknown (no valid project.yml yet) does."""
    rules = sorted((root / RULES_DIR).glob(MARKDOWN_GLOB))
    templates = [PR_TEMPLATE]
    if tracker is not Tracker.LINEAR:
        templates.append(ISSUE_TEMPLATE)
    return [f"{RULES_DIR}/{path.name}" for path in rules] + templates


def normalized(text: str) -> str:
    """Line endings do not count as a difference (Windows checkouts)."""
    return text.replace(CRLF, LF)


def read(path: Path) -> str | None:
    """A file's normalized text, or None if it does not exist."""
    if not path.is_file():
        return None
    return normalized(path.read_text(encoding="utf-8"))


def shared_text(root: Path, name: str) -> str:
    """Render a shared original with the installed release line."""
    content = read(root / name)
    if content is None:
        raise FileNotFoundError(root / name)
    return content.replace(VERSION_TOKEN, header_version())


def base_block(root: Path) -> str:
    """The shared block, markers included, ending with a newline."""
    text = shared_text(root, BASE_FILE)
    return text if text.endswith(LF) else text + LF


def _block_span(text: str) -> tuple[int, int] | None:
    starts = text.count(BLOCK_START)
    ends = text.count(BLOCK_END)
    if starts != ends or starts > 1:
        raise ValueError("shared block markers are unmatched or duplicated")
    if not starts:
        return None
    start = text.find(BLOCK_START)
    end = text.find(BLOCK_END, start)
    if end < 0:
        raise ValueError("the closing marker precedes the opening marker")
    end += len(BLOCK_END)
    if text.startswith(LF, end):
        end += len(LF)
    return start, end


def current_block(agents_text: str) -> str | None:
    """The shared block as it is in an AGENTS.md, or None if it has none."""
    span = _block_span(agents_text)
    return agents_text[span[0] : span[1]] if span else None


def with_block(agents_text: str, block: str) -> str:
    """AGENTS.md with its shared block replaced, or appended if missing."""
    span = _block_span(agents_text)
    if span:
        return agents_text[: span[0]] + block + agents_text[span[1] :]
    if not agents_text:
        return block
    separator = LF if agents_text.endswith(LF) else LF + LF
    return agents_text + separator + block
