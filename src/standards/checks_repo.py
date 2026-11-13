"""Checks on the repository rather than the code: the PR title, pinned
actions in workflows, and release tags against the version file."""

from __future__ import annotations

import json
import re
import tomllib
from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path, PurePosixPath

import yaml

from standards.constants import TAG_REF_PREFIX, Check, Rule
from standards.context import Context
from standards.findings import Finding
from standards.project_config import Project, Release

_SHA_PIN = re.compile(r"@[0-9a-f]{40}$")
_UNITY_VERSION = re.compile(r"^\s*bundleVersion:\s*(\S+)\s*$", re.MULTILINE)
_WORKFLOWS_DIR = ".github/workflows"
_ACTION_FILES = frozenset({"action.yml", "action.yaml"})
_YAML_SUFFIXES = frozenset({".yml", ".yaml"})
_LOCAL_PREFIXES = ("./", "docker://")


class Key(StrEnum):
    """Keys read from workflow YAML and version files."""

    USES = "uses"
    PROJECT = "project"
    VERSION = "version"


class VersionFile(StrEnum):
    """File names whose version the release check can read."""

    PYPROJECT = "pyproject.toml"
    PACKAGE_JSON = "package.json"
    UNITY = "ProjectSettings.asset"


def check_pr_title(context: Context, project: Project | None) -> list[Finding]:
    """The PR title is `<KEY>-<number> <issue title>`."""
    title = context.event.pr_title
    if title is None or project is None:
        return []
    pattern = re.compile(rf"^{re.escape(project.key)}-\d+ \S")
    if pattern.match(title):
        return []
    return [
        Finding(
            Check.PR_TITLE,
            f"The PR title `{title}` does not start with `{project.key}-<number> `.",
            f"Rename it to `{project.key}-<issue number> <issue title>`; "
            "it becomes the commit on the default branch.",
            Rule.WORKFLOW,
        )
    ]


def _is_workflow(path: str) -> bool:
    pure = PurePosixPath(path)
    in_workflows = str(pure.parent) == _WORKFLOWS_DIR and pure.suffix in _YAML_SUFFIXES
    return in_workflows or pure.name in _ACTION_FILES


def _uses_values(node: object) -> Iterator[str]:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == Key.USES and isinstance(value, str):
                yield value
            else:
                yield from _uses_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _uses_values(item)


def _line_of(source: str, needle: str) -> int | None:
    for number, line in enumerate(source.splitlines(), start=1):
        if needle in line:
            return number
    return None


def check_pinned_actions(context: Context) -> list[Finding]:
    """Every `uses:` in a changed workflow is pinned to a commit SHA."""
    findings = []
    for change in context.changes:
        if not _is_workflow(change.path):
            continue
        source = (context.repo / change.path).read_text(encoding="utf-8")
        for uses in _uses_values(yaml.safe_load(source)):
            if uses.startswith(_LOCAL_PREFIXES) or _SHA_PIN.search(uses):
                continue
            findings.append(
                Finding(
                    Check.PINNED_ACTION,
                    f"`{uses}` is pinned to a tag or branch, which can be moved.",
                    "Pin it to the full commit SHA, with the version in a comment.",
                    Rule.DEPENDENCIES,
                    change.path,
                    _line_of(source, uses),
                )
            )
    return findings


def read_version(path: Path) -> str | None:
    """The version written in a pyproject.toml, package.json or Unity
    ProjectSettings.asset, or None if it is not there."""
    if not path.is_file():
        return None
    source = path.read_text(encoding="utf-8")
    if path.name == VersionFile.PYPROJECT:
        project = tomllib.loads(source).get(Key.PROJECT, {})
        version = project.get(Key.VERSION) if isinstance(project, dict) else None
    elif path.name == VersionFile.PACKAGE_JSON:
        version = json.loads(source).get(Key.VERSION)
    elif path.name == VersionFile.UNITY:
        match = _UNITY_VERSION.search(source)
        version = match.group(1) if match else None
    else:
        return None
    return version if isinstance(version, str) else None


def check_release_tag(context: Context, project: Project | None) -> list[Finding]:
    """A pushed `v<version>` tag matches the version file."""
    ref = context.event.ref
    if project is None or not ref.startswith(TAG_REF_PREFIX):
        return []
    tagged = ref.removeprefix(TAG_REF_PREFIX)
    written = read_version(context.repo / project.version_file)
    problem = None
    if project.release is Release.NONE:
        problem = "`project.yml` says `release: none`, but a release tag was pushed."
    elif written is None:
        problem = f"No version could be read from `{project.version_file}`."
    elif written != tagged:
        problem = f"The tag says {tagged}, but `{project.version_file}` says {written}."
    if problem is None:
        return []
    return [
        Finding(
            Check.RELEASE_TAG,
            problem,
            "Delete the tag, merge a release PR that sets the version, "
            "then tag that commit.",
            Rule.WORKFLOW,
            project.version_file,
        )
    ]
