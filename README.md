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

- Branch: the issue ID (`KEY-12`), or `<platform>/<ID>` when an agent
  platform needs its prefix (`claude/KEY-12`).
- PR title and the one commit that lands: `<ID> <issue title>`.
- Squash merge only; the squash commit uses the PR title, with no body.
- Every repository runs `just check`, `just fix`, `just test` and `just build`,
  locally and in CI. Install [just](https://just.systems) once, at the
  version CI uses (`setup-just/action.yml`):
  `uv tool install rust-just==1.59.0` on any system,
  `winget install Casey.Just --version 1.59.0` on Windows, or
  `cargo install just --version 1.59.0 --locked`. Homebrew cannot install
  a given version, so on macOS use `uv`.
- Versions are SemVer, written only in `version_file`; the owner tags
  releases `v<version>`. No changelog file.

## Adopting in a repository

One PR per repository, for its own issue (`<KEY>-<n> Adopt the shared rules`):

1. `project.yml` from `project.example.yml`.
2. `AGENTS.md`: the project part from `templates/AGENTS.md`. With Claude
   Code, a `CLAUDE.md` containing `@AGENTS.md`.
3. The shared copies, written by `standards-sync` from the version the
   repository pins: the block in `AGENTS.md`, `docs/agent/rules/` and the PR
   template.

   ```
   uvx --from git+https://github.com/FacundoTripelhorn/agent-standards@<sha> standards-sync
   ```
4. `docs/agent/repo-map.md`, `verification-matrix.md` and `known-non-bugs.md`
   from `templates/docs/agent/`, filled in for the repository.
5. A `justfile` from `templates/just/` and CI from
   `templates/.github/workflows/ci.yml`, with both actions from this
   repository (the checks and `setup-just`) pinned to the same commit SHA.
6. `.github/dependabot.yml`, `.gitattributes`, and the issue template. Where
   the repository already has one of these files, add the template's lines
   to it; never replace it (an existing `.gitattributes` may hold
   rules the build depends on).
7. Documents outside the list in `docs/agent/rules/docs.md`: fold what is
   still true into the standard ones, and list the rest under "Other
   documents" in `AGENTS.md` or remove them, with the owner's approval.
8. Settings, done by the owner: squash merge only with the PR title as the
   commit, and `standards`, `check`, `test` and `build` as required checks.
   If the repository limits which actions may run (Settings → Actions →
   General), allow `FacundoTripelhorn/agent-standards` and its subpaths
   (`FacundoTripelhorn/*` covers both), besides the toolchain's own actions.

The shared copies are real files, because agents only reliably read what is
in the repository they work on. Their headers name the agent-standards
release line (`MAJOR.MINOR`), rendered by `standards-sync`; the originals
here keep a placeholder. A patch release only fixes the check, so it leaves
the copies as they are. The canonical `.github/pull_request_template.md` is
owned by the sync in every repository; project-specific alternatives use
other names under `.github/PULL_REQUEST_TEMPLATE/`. Copies are never edited
by hand: the `standards` job reports drift, and `standards-sync` rewrites
them. To move a repository to a new release, update the action's pin
(Dependabot proposes it) and run `standards-sync` with the same commit in
that PR. agent-standards itself skips step 3, because it holds the
originals.

The copies are already in Prettier's default format, so a repository whose
Prettier checks Markdown with the default settings needs nothing for them.
If its settings change how Markdown is written (a `tabWidth` other than 2,
or `proseWrap` set to `always` or `never`), its Prettier config applies the
defaults to the copies with an override, so they are still checked and the
rest of the repository keeps its own style (`ci.md`, "Same commands locally
and in CI"):

```json
"overrides": [
  {
    "files": [
      "AGENTS.md",
      "docs/agent/rules/*.md",
      ".github/pull_request_template.md",
      ".github/ISSUE_TEMPLATE/work-item.md"
    ],
    "options": { "tabWidth": 2, "useTabs": false, "proseWrap": "preserve" }
  }
]
```

Do not list the copies in `.prettierignore` instead: they would no longer be
checked. Any Prettier 3 release accepts the copies.

## The shared check

Each repository's `standards` job runs this repository as an action, pinned
by commit SHA, so a change here reaches a repository only when it updates
the pin. To run it locally against another repository:

```
just run ../GhostMCP origin/main
```

Working on the check itself: `just check` and `just test` (needs
[uv](https://docs.astral.sh/uv/)).

## Installing just in CI

`setup-just/` is a second action here. It installs one pinned `just` release
for the `check`, `test` and `build` jobs, checked against its sha256 before
anything is installed, so repositories need no third-party action for it. It
runs on Linux x64 runners only. To move to a new `just` release, change
`JUST_VERSION` and `JUST_SHA256` in `setup-just/action.yml` together, taking
the checksum from that release's `SHA256SUMS` file, and the version in the
local install commands under "Conventions in one line each" (a test checks
they match). Repositories get it when they update their pin.

