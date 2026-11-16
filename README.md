# agent-standards

Shared working rules for every repository: what agents and people read
(`AGENTS.base.md` and `docs/agent/rules/`), how each project describes
itself (`project.yml`), the issue and PR templates, and the size thresholds.

## Contents

| Path | What it is |
|---|---|
| `AGENTS.base.md` | The shared block synced into every repository's `AGENTS.md`, below the project part. |
| `templates/AGENTS.md` | The project part of `AGENTS.md`: summary, extra commands, architecture, versioning, project rules, other documents. |
| `docs/agent/rules/` | The detail behind each base rule, synced into every repository and read on demand: `code.md`, `security.md`, `workflow.md`, `dependencies.md`, `ci.md`, `docs.md`, `thresholds.md`. |
| `project.example.yml` | The `project.yml` every repository has at its root. |
| `.github/pull_request_template.md` | PR template every repository uses. |
| `.github/ISSUE_TEMPLATE/work-item.md` | Issue template for GitHub-tracked projects (same fields in Linear). |
| `templates/docs/agent/` | Starting points for the three agent docs every repository has. |
| `templates/docs/design.md` | Headings for the optional design document. |
| `templates/just/` | `justfile` starting points for Python (uv), TypeScript (pnpm/npm) and Unity. |
| `templates/.github/` | `ci.yml` with the `standards`, `check`, `test` and `build` jobs, and `dependabot.yml`. |
| `templates/.gitattributes` | Marks lockfiles as generated. |
| `action.yml`, `src/standards/` | The shared CI check every repository's `standards` job runs (`docs/agent/rules/ci.md`). |

## Projects

| Repository | Key | Tracker | Language | Docs language | Default branch | Status |
|---|---|---|---|---|---|---|
| facturadorE | `FAC` | Linear | es-AR | es-AR | master | active |
| CoastKids | `CK` | GitHub | es-AR | en | main | active |
| DeskPet | `DPET` | GitHub | en | en | main | active |
| GhostMCP | `GHOST` | GitHub | en | en | main | active |
| GroceryAgent | `GA` | Linear | en | en | master | paused |
| agent-standards | `AST` | GitHub | en | en | main | active |

Each project numbers its own issues: `FAC` and `GA` in Linear, the others in
GitHub Issues of their repository.

## Conventions in one line each

- Branch: the issue ID (`GHOST-47`), or `<platform>/<ID>` when an agent
  platform needs its prefix (`claude/GHOST-47`).
- PR title and the one commit that lands: `<ID> <issue title>`.
- Squash merge only; the squash commit uses the PR title, with no body.
- Every repository runs `just check`, `just fix`, `just test` and `just build`,
  locally and in CI. Install [just](https://just.systems) once
  (`winget install Casey.Just`, `brew install just`, or `pip install rust-just`).
- Versions are SemVer, written only in `version_file`; the owner tags
  releases `v<version>`. No changelog file.

## Adopting in a repository

One PR per repository, for its own issue (`<KEY>-<n> Adopt the shared rules`):

1. `project.yml` from `project.example.yml`.
2. `AGENTS.md`: the project part from `templates/AGENTS.md`, then the block
   from `AGENTS.base.md`, markers included. With Claude Code, a `CLAUDE.md`
   containing `@AGENTS.md`.
3. `docs/agent/rules/` copied from here.
4. `docs/agent/repo-map.md`, `verification-matrix.md` and `known-non-bugs.md`
   from `templates/docs/agent/`, filled in for the repository.
5. A `justfile` from `templates/just/` and CI from
   `templates/.github/workflows/ci.yml`, with the action pinned to a commit
   SHA of this repository.
6. `.github/dependabot.yml`, `.gitattributes`, and the PR and issue templates.
7. Documents outside the list in `docs/agent/rules/docs.md`: fold what is
   still true into the standard ones, and list the rest under "Other
   documents" in `AGENTS.md` or remove them, with the owner's approval.
8. Settings, done by the owner: squash merge only with the PR title as the
   commit, and `standards`, `check`, `test` and `build` as required checks.

The block in `AGENTS.md` and `docs/agent/rules/` are copies: when they change
here, the repository copies them again in a PR. agent-standards itself skips
steps 2 and 3, because it holds the originals.

## The shared check

Each repository's `standards` job runs this repository as an action, pinned
by commit SHA, so a change here reaches a repository only when it updates
the pin. To run it locally against another repository:

```
just run ../GhostMCP origin/main
```

Working on the check itself: `just check` and `just test` (needs
[uv](https://docs.astral.sh/uv/)).

