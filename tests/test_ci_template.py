"""The Unity jobs in the CI template never let a check that could not run
look like a pass (ci.md, "CI is the source of truth")."""

from __future__ import annotations

import os
import re
import subprocess
import textwrap
from pathlib import Path

import yaml

TEMPLATE = Path(__file__).parents[1] / "templates/.github/workflows/ci.yml"
# The Unity jobs are commented out at the end of the template.
UNITY_BLOCK_START = "#   test:"
COMMENT_PREFIX = "#"
PINNED_USES = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
GAMECI_ACTION = "game-ci/unity-test-runner@"
TEST_JOB = "test"
CHECK_JOB = "check"
ALWAYS = "always()"
SECRET_REFERENCE = re.compile(r"\$\{\{\s*secrets\.(\w+)\s*\}\}")
SECRET_IN_CONDITION = "secrets."
PRESENT = "set"
PASSED = 0
FAILED = 1
# needs.<job>.result values (GitHub Actions)
SUCCESS = "success"
FAILURE = "failure"
SKIPPED = "skipped"


def unity_jobs() -> dict[str, dict[str, object]]:
    text = TEMPLATE.read_text(encoding="utf-8")
    block = text[text.index(UNITY_BLOCK_START) :]
    lines = [line.removeprefix(COMMENT_PREFIX) for line in block.splitlines()]
    jobs = yaml.safe_load(textwrap.dedent("\n".join(lines)))
    assert isinstance(jobs, dict)
    return jobs


def steps(job: str) -> list[dict[str, object]]:
    found = unity_jobs()[job]["steps"]
    assert isinstance(found, list)
    return found


def gameci_secrets() -> list[str]:
    """The secrets the GameCI step reads, by name."""
    [runner] = [
        step
        for step in steps(TEST_JOB)
        if str(step.get("uses", "")).startswith(GAMECI_ACTION)
    ]
    env = runner["env"]
    assert isinstance(env, dict)
    names = []
    for value in env.values():
        match = SECRET_REFERENCE.fullmatch(str(value))
        assert match, value
        names.append(match.group(1))
    return names


def run_secret_step(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    script = str(steps(TEST_JOB)[0]["run"])
    clean = {key: value for key, value in os.environ.items() if key not in env}
    return subprocess.run(
        ["bash", "-c", script],
        env={**clean, **env},
        capture_output=True,
        text=True,
        check=False,
    )


def test_every_action_is_pinned_to_a_commit() -> None:
    for job in unity_jobs():
        for step in steps(job):
            if "uses" in step:
                assert PINNED_USES.match(str(step["uses"]))


def test_no_job_or_step_is_skipped_on_a_secret() -> None:
    for name, job in unity_jobs().items():
        assert SECRET_IN_CONDITION not in str(job.get("if", "")), name
        for step in steps(name):
            assert SECRET_IN_CONDITION not in str(step.get("if", "")), name


def test_the_first_test_step_checks_every_secret_gameci_needs() -> None:
    first = steps(TEST_JOB)[0]
    assert "uses" not in first
    env = first["env"]
    assert isinstance(env, dict)
    assert sorted(env) == sorted(gameci_secrets())


def test_a_missing_secret_fails_and_is_named() -> None:
    names = gameci_secrets()
    present = dict.fromkeys(names, PRESENT)
    assert run_secret_step(present).returncode == PASSED
    for missing in names:
        result = run_secret_step({**present, missing: ""})
        assert result.returncode == FAILED
        assert f"The {missing} secret is missing" in result.stdout


def test_check_runs_after_test_and_fails_unless_it_succeeded() -> None:
    check = unity_jobs()[CHECK_JOB]
    assert check["needs"] == TEST_JOB
    assert check["if"] == ALWAYS
    [step] = steps(CHECK_JOB)
    env = step["env"]
    assert isinstance(env, dict)
    for result, code in ((SUCCESS, PASSED), (FAILURE, FAILED), (SKIPPED, FAILED)):
        outcome = subprocess.run(
            ["bash", "-c", str(step["run"])],
            env={**os.environ, **dict.fromkeys(env, result)},
            capture_output=True,
            text=True,
            check=False,
        )
        assert outcome.returncode == code, result
