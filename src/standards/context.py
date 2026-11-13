"""What a run knows: the repository, the GitHub event, the base commit to
compare against, the changed files and the project settings."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import cast

from standards.constants import NULL_SHA
from standards.gitio import Change, changed_files, has_commit


class Env(StrEnum):
    """Variables GitHub Actions sets for every step."""

    EVENT_PATH = "GITHUB_EVENT_PATH"
    REF = "GITHUB_REF"


class EventKey(StrEnum):
    """Keys of the GitHub event payload."""

    PULL_REQUEST = "pull_request"
    TITLE = "title"
    BASE = "base"
    SHA = "sha"
    BEFORE = "before"


@dataclass(frozen=True)
class Event:
    """The parts of the GitHub event the checks use."""

    pr_title: str | None = None
    base_sha: str | None = None
    ref: str = ""


@dataclass
class Context:
    """Everything a check reads. `base` is None when there is nothing to
    compare against; the ratchet checks are then skipped."""

    repo: Path
    event: Event
    base: str | None
    changes: list[Change] = field(default_factory=list)


def _as_dict(value: object) -> dict[str, object]:
    return cast(dict[str, object], value) if isinstance(value, dict) else {}


def read_event() -> Event:
    """The event from GITHUB_EVENT_PATH, or an empty one outside Actions."""
    ref = os.environ.get(Env.REF, "")
    path = os.environ.get(Env.EVENT_PATH)
    if not path or not Path(path).is_file():
        return Event(ref=ref)
    payload = _as_dict(json.loads(Path(path).read_text(encoding="utf-8")))
    pull = _as_dict(payload.get(EventKey.PULL_REQUEST))
    if pull:
        base = _as_dict(pull.get(EventKey.BASE))
        title = pull.get(EventKey.TITLE)
        sha = base.get(EventKey.SHA)
        return Event(
            pr_title=title if isinstance(title, str) else None,
            base_sha=sha if isinstance(sha, str) else None,
            ref=ref,
        )
    before = payload.get(EventKey.BEFORE)
    if isinstance(before, str) and before != NULL_SHA:
        return Event(base_sha=before, ref=ref)
    return Event(ref=ref)


def build_context(repo: Path, base_override: str | None) -> tuple[Context, list[str]]:
    """The run's context, plus notes about anything that was skipped."""
    event = read_event()
    base = base_override or event.base_sha
    notes: list[str] = []
    if base and not has_commit(repo, base):
        notes.append(
            f"Base commit {base} is not in the checkout (use fetch-depth: 0); "
            "the size, literal and suppression checks were skipped."
        )
        base = None
    elif not base:
        notes.append(
            "No base commit to compare against; "
            "the size, literal and suppression checks were skipped."
        )
    changes = changed_files(repo, base) if base else []
    return Context(repo, event, base, changes), notes
