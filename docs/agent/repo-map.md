# Repository map

Where things live, by the kind of task. Read this before searching the code.

## Layout

| Path | What lives there |
|---|---|
| `AGENTS.base.md`, `docs/agent/rules/` | The shared rules (originals) |
| `templates/` | Starting points copied into other repositories |
| `project.example.yml` | Reference for `project.yml` |
| `action.yml` | The composite action every repository's `standards` job uses |
| `src/standards/` | The checks the action runs |
| `tests/` | pytest suite; `conftest.py` builds throwaway git repositories |
| `.github/` | This repository's CI and the PR and issue templates (shared) |

## Start here by task type

### Shared rules

| What | Where |
|---|---|
| Always-loaded rules | `AGENTS.base.md` |
| Detail read on demand | `docs/agent/rules/*.md` |
| Size limits | `docs/agent/rules/thresholds.md` and `src/standards/constants.py` (`LIMITS`) |
| PR and issue templates | `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/` |

### Templates for other repositories

| What | Where |
|---|---|
| Project part of `AGENTS.md` | `templates/AGENTS.md` |
| Agent docs | `templates/docs/agent/` |
| Design doc | `templates/docs/design.md` |
| `justfile` per stack | `templates/just/` |
| CI, Dependabot | `templates/.github/` |
| Lockfile attributes | `templates/.gitattributes` |

### The check

| What | Where |
|---|---|
| Entry point and order of checks | `src/standards/run.py` |
| GitHub event, base commit, changed files | `src/standards/context.py`, `src/standards/gitio.py` |
| `project.yml` validation | `src/standards/project_config.py` |
| PR title, pinned actions, release tag | `src/standards/checks_repo.py` |
| File and function size, suppressions | `src/standards/checks_code.py` |
| Measuring sizes | `src/standards/metrics.py` |
| Counting suppressions, `allow-suppression:` | `src/standards/suppressions.py` |
| Parsing, tree-sitter node names | `src/standards/syntax.py`, `src/standards/node_types.py` |
| Annotations and job summary | `src/standards/findings.py` |
| Which files are shared copies, the `AGENTS.md` block markers | `src/standards/shared.py` |
| `standards-sync` (writes the copies) | `src/standards/sync.py` |
| Drift check of the copies | `src/standards/check_shared.py` |
| Bundling the shared files into the package | `pyproject.toml` (`force-include`) |
| Secrets (gitleaks) | `action.yml` |
| Tests | `tests/test_<module>.py`; end to end in `tests/test_checks.py` |
