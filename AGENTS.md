# agent-standards

The shared rules, templates and CI check for the owner's repositories. The
check is a composite GitHub Action (`action.yml`) running a Python package
(`src/standards/`, Python 3.12+, uv, tree-sitter).

**Read `AGENTS.base.md` next.** It holds the shared rules every repository
follows. Here it is the original; other repositories carry a synced copy of
it inside their `AGENTS.md`.

## Commands

`just check`, `just fix`, `just test` and `just build` are described in the
shared rules. This project also has:

| Do this | Command |
|---|---|
| Run the check on another repository | `just run ../GhostMCP origin/main` |

## Architecture

- **Modules:** `run` → `checks_repo`, `checks_code` → `metrics`,
  `suppressions` → `syntax` → `node_types`. `context`, `gitio`,
  `project_config`, `findings` and `constants` are used by all of them.
  Imports only go in the direction of the arrows.
- **External systems:** git (through `gitio` only), the GitHub event file
  and step summary (through `context` and `findings`), gitleaks (in
  `action.yml` only).
- **Invariants:**
  - Existing debt never blocks: size and suppressions are compared with the
    base commit, and only growth is reported.
  - Secrets fail in either mode; everything else follows `mode`.
  - Every finding says what is wrong, where, how to fix it and which rule.
  - CI checks only mechanical rules. Practices that need judgement (names
    over literals) are reviewed, not checked.
  - The limits in `constants.py` match `docs/agent/rules/thresholds.md`
    (`tests/test_thresholds_doc.py` fails otherwise).

## Versioning and release

- The version lives in `pyproject.toml`.
- A release is the tag `v<version>` on `main`.
- Repositories use the action pinned to a commit SHA, with the version in a
  comment. A change here reaches a repository only when it updates the pin.

## Project rules

- `AGENTS.base.md` and `docs/agent/rules/` are edited here and nowhere else.
  A change to them changes every repository: say in the PR which rule
  changed and why.
- `templates/` are starting points copied into other repositories once.
  They are not synced, so a template change does not touch existing copies.
- The action installs with `uv run --locked --no-dev`: runtime dependencies
  go in `[project] dependencies`, everything else in the dev group.

## Other documents

| File | Its one job |
|---|---|
| `AGENTS.base.md` | The shared rules (the original of the synced block). |
| `project.example.yml` | The reference for every repository's `project.yml`. |
| `templates/**` | Starting points copied into other repositories. |
