"""The shared files every repository keeps a copy of, and where this version's
originals are: bundled in the installed package, or in the source tree."""

from __future__ import annotations

from pathlib import Path

from standards.constants import RULES_DIR

# Inside the installed package, the originals keep their repository paths
# under this folder (pyproject.toml, force-include).
PACKAGED_DIR = "files"
BASE_FILE = "AGENTS.base.md"
AGENTS_FILE = "AGENTS.md"
PR_TEMPLATE = ".github/pull_request_template.md"
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


def is_origin(repo: Path) -> bool:
    """agent-standards itself holds the originals, not copies."""
    return (repo / BASE_FILE).is_file()


def copied_files(root: Path) -> list[str]:
    """Repository paths of the files copied whole."""
    rules = sorted((root / RULES_DIR).glob(MARKDOWN_GLOB))
    return [f"{RULES_DIR}/{path.name}" for path in rules] + [PR_TEMPLATE]


def normalized(text: str) -> str:
    """Line endings do not count as a difference (Windows checkouts)."""
    return text.replace(CRLF, LF)


def read(path: Path) -> str | None:
    """A file's normalized text, or None if it does not exist."""
    if not path.is_file():
        return None
    return normalized(path.read_text(encoding="utf-8"))


def base_block(root: Path) -> str:
    """The shared block, markers included, ending with a newline."""
    text = read(root / BASE_FILE) or ""
    return text if text.endswith(LF) else text + LF


def _block_span(text: str) -> tuple[int, int] | None:
    start = text.find(BLOCK_START)
    end = text.find(BLOCK_END, start if start >= 0 else 0)
    if start < 0 or end < 0:
        return None
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
