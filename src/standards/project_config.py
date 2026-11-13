"""Read and validate project.yml (project.example.yml in agent-standards)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import yaml

from standards.constants import PROJECT_FILE, Check, Rule
from standards.findings import Finding

_KEY = re.compile(r"^[A-Z][A-Z0-9]{1,9}$")
_LANGUAGE = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")


class Field(StrEnum):
    """Keys of project.yml."""

    KEY = "key"
    LANGUAGE = "language"
    DOCS_LANGUAGE = "docs_language"
    TRACKER = "tracker"
    STATUS = "status"
    PACKAGE_MANAGER = "package_manager"
    VERSION_FILE = "version_file"
    RELEASE = "release"
    DEFAULT_BRANCH = "default_branch"


class Tracker(StrEnum):
    GITHUB = "github"
    LINEAR = "linear"


class Status(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"


class PackageManager(StrEnum):
    UV = "uv"
    PNPM = "pnpm"
    NPM = "npm"
    UNITY = "unity"


class Release(StrEnum):
    NONE = "none"
    TAG = "tag"
    PACKAGE = "package"


_CHOICES: dict[Field, type[StrEnum]] = {
    Field.TRACKER: Tracker,
    Field.STATUS: Status,
    Field.PACKAGE_MANAGER: PackageManager,
    Field.RELEASE: Release,
}
_REQUIRED = (
    Field.KEY,
    Field.LANGUAGE,
    Field.TRACKER,
    Field.STATUS,
    Field.PACKAGE_MANAGER,
    Field.VERSION_FILE,
    Field.RELEASE,
)
_FIX = "Compare it with project.example.yml in agent-standards."


@dataclass(frozen=True)
class Project:
    """The validated settings the other checks use."""

    key: str
    version_file: str
    release: Release


def _finding(message: str, line: int | None = None) -> Finding:
    return Finding(Check.PROJECT, message, _FIX, Rule.PROJECT, PROJECT_FILE, line)


def _field_problems(data: dict[str, object], repo: Path) -> list[str]:
    problems = [f"`{f.value}` is missing." for f in _REQUIRED if f.value not in data]
    known = {f.value for f in Field}
    problems += [f"`{k}` is not a known field." for k in data if k not in known]
    for field, choices in _CHOICES.items():
        value = data.get(field.value)
        if value is not None and value not in {c.value for c in choices}:
            allowed = ", ".join(c.value for c in choices)
            problems.append(f"`{field.value}: {value}` must be one of {allowed}.")
    key = data.get(Field.KEY.value)
    if key is not None and not _KEY.match(str(key)):
        problems.append(f"`key: {key}` must be 2 to 10 uppercase letters or digits.")
    for lang in (Field.LANGUAGE, Field.DOCS_LANGUAGE):
        value = data.get(lang.value)
        if value is not None and not _LANGUAGE.match(str(value)):
            problems.append(f"`{lang.value}: {value}` must look like `en` or `es-AR`.")
    version_file = data.get(Field.VERSION_FILE.value)
    if version_file is not None and not (repo / str(version_file)).is_file():
        problems.append(f"`version_file: {version_file}` does not exist.")
    return problems


def load_project(repo: Path) -> tuple[Project | None, list[Finding]]:
    """The project settings, or None and the findings that explain why."""
    path = repo / PROJECT_FILE
    if not path.is_file():
        return None, [_finding(f"`{PROJECT_FILE}` is missing at the repository root.")]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return None, [_finding(f"`{PROJECT_FILE}` is not valid YAML: {error}")]
    if not isinstance(data, dict):
        return None, [_finding(f"`{PROJECT_FILE}` must be a mapping of fields.")]
    problems = _field_problems(data, path.parent)
    if problems:
        return None, [_finding(problem) for problem in problems]
    project = Project(
        key=str(data[Field.KEY.value]),
        version_file=str(data[Field.VERSION_FILE.value]),
        release=Release(data[Field.RELEASE.value]),
    )
    return project, []
