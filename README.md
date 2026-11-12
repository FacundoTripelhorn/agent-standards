# agent-standards

Shared working rules for every repository: what agents and people read
(`AGENTS.base.md` and `docs/agent/rules/`), how each project describes
itself (`project.yml`), the issue and PR templates, and the size thresholds.

## Contents

| Path | What it is |
|---|---|
| `AGENTS.base.md` | The shared block synced into every repository's `AGENTS.md`, below the project part. |
| `templates/AGENTS.md` | The project part of `AGENTS.md`: summary, commands, project rules, other documents. |
| `docs/agent/rules/` | The detail behind each base rule, synced into every repository and read on demand: `code.md`, `security.md`, `workflow.md`, `docs.md`, `thresholds.md`. |
| `project.example.yml` | The `project.yml` every repository has at its root. |
| `.github/pull_request_template.md` | PR template every repository uses. |
| `.github/ISSUE_TEMPLATE/work-item.md` | Issue template for GitHub-tracked projects (same fields in Linear). |
| `templates/docs/agent/` | Starting points for the three agent docs every repository has. |

## Projects

| Repository | Key | Tracker | Language | Docs language | Default branch | Status |
|---|---|---|---|---|---|---|
| facturadorE | `FAC` | Linear | es-AR | es-AR | master | active |
| CoastKids | `CK` | GitHub | es-AR | en | main | active |
| DeskPet | `DPET` | GitHub | en | en | main | active |
| GhostMCP | `GHOST` | GitHub | en | en | main | active |
| GroceryAgent | `GA` | Linear | en | en | master | paused |

Each project numbers its own issues: `FAC` and `GA` in Linear, the others in
GitHub Issues of their repository.

## Conventions in one line each

- Branch: the issue ID (`GHOST-47`), or `<platform>/<ID>` when an agent
  platform needs its prefix (`claude/GHOST-47`).
- PR title and the one commit that lands: `<ID> <issue title>`.
- Squash merge only; the squash commit uses the PR title, with no body.
- Every repository exposes `make check`, `make fix` and `make test`.
