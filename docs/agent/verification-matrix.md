# Verification matrix

Which checks to run for which kind of change. CI runs the full set on every
PR; this page tells you what to run while working and what CI cannot prove.

## Default order

| Step | Command | When |
|---|---|---|
| Lint, format and types | `just fix`, then `just check` | Every change |
| Tests | `just test` | Every change |
| Build | `just build` | Nothing to build: the action runs from source |

## Narrow checks by task type

| Task type | Paths | Run |
|---|---|---|
| A check | `src/standards/` | `just test`, then `just run <another repo> <base>` on a real repository and read the findings |
| Size limits | `constants.py`, `thresholds.md` | `uv run pytest tests/test_thresholds_doc.py` |
| The action | `action.yml` | The `standards` job of this PR runs it with `uses: ./` |
| Installing `just` | `setup-just/` | `uv run pytest tests/test_setup_just.py`; this PR's `check`, `test` and `build` jobs run it with `uses: ./setup-just` |
| CI template | `templates/.github/workflows/ci.yml` | `uv run pytest tests/test_ci_template.py` (the Unity jobs: pinned actions, missing secrets fail, `check` fails unless `test` succeeded) |
| Rules or templates only | `AGENTS.base.md`, `docs/agent/rules/`, `templates/` | `just fix`, then `just check` (Prettier on the shared Markdown); check that no rule contradicts another and links resolve |

## What only the owner can verify

| Check | When it is needed | How |
|---|---|---|
| The action in another repository | Before a repository updates its pin | Open a PR there that updates the pin and read its `standards` job |
| A release tag | After a release PR merges | Push `v<version>`; the `standards` job checks it against `pyproject.toml` |
| Windows PowerShell recipes in `templates/just/` | Changes to those recipes | Run them on Windows |
