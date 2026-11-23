# CI and the justfile

<!-- agent-standards v{agent-standards-version} — synced from agent-standards. Edit it there, not here. -->

Read before changing a workflow under `.github/workflows/` or the `justfile`.
Both changes need the owner's approval first (shared rules, "Ask the owner
first").

## Same commands locally and in CI

- The `justfile` is the one place that says how to lint, format, type-check,
  test and build. CI calls its recipes; it never repeats their commands.
  What passes on your machine is what CI runs.
- Every repository has the recipes `check`, `fix`, `test` and `build`. A
  recipe that does not apply to a project prints that and exits 0 (for
  example, a library with nothing to build). A recipe that applies but
  cannot run here exits non-zero with the reason.
- Formatters run in check mode in `just check`. Do not commit unformatted
  code.
- The shared copies are in Prettier's default format. If the repository
  runs Prettier with other Markdown options, its config has an override
  for `AGENTS.md`, `docs/agent/rules/*.md`,
  `.github/pull_request_template.md` and
  `.github/ISSUE_TEMPLATE/work-item.md` that sets `tabWidth: 2`,
  `useTabs: false` and `proseWrap: "preserve"`. Its Prettier then checks
  the copies without rewriting them. Never exclude the copies from it.
- Unity is the one exception to "CI calls the recipe": the editor exists in
  CI only as a Docker image, and GitHub's runners have no editor for
  `just check` or `just test`. Exactly this changes, and nothing else:
  - `test` runs the same Edit Mode tests through GameCI
    (`game-ci/unity-test-runner`) instead of `just test`. That run compiles
    the project first.
  - `check` does not compile a second time. It runs after `test`
    (`needs: test`, `if: always()`) and passes only when `test` succeeded,
    which proves the project compiled.
  - `build` keeps its recipe, and `just check` and `just test` stay the
    local commands.

  agent-standards has both jobs in `templates/.github/workflows/ci.yml`.

- If the repository has an architecture check (import-linter,
  dependency-cruiser, assembly references), `just check` runs it. It is
  optional, so new repositories are not blocked by it.

## Same job names everywhere

Every repository's CI has these jobs, with these names, so every ruleset
requires the same checks:

| Job     | Runs                               |
| ------- | ---------------------------------- |
| `check` | Toolchain setup, then `just check` |
| `test`  | Toolchain setup, then `just test`  |
| `build` | Toolchain setup, then `just build` |

Each of these jobs installs `just` with
`FacundoTripelhorn/agent-standards/setup-just`, pinned to the same commit as
the `standards` job. It installs a pinned `just` release checked against its
sha256, so no third-party action is needed for it.

The shared checks from agent-standards run in a `standards` job that uses
the agent-standards action, pinned by SHA, after a checkout with
`fetch-depth: 0`. It checks `project.yml`, the PR title, file and function
size, suppressions, pinned actions, release tags, secrets (gitleaks), and
that the shared copies (`AGENTS.md` block, `docs/agent/rules/`, the PR
template) match the pinned version: the fix is to run `standards-sync`.
Coding practices that need judgement, such as names over literals, are not
checked by CI; they are reviewed. Findings appear on the lines
of the PR diff, each with the fix and the rule. It starts in `mode: warn`;
the owner switches a repository to `mode: fail` once its warnings are
understood. Secrets fail in either mode. Jobs that
only make sense for one project (a Windows build, a Docker image) are extra
jobs, listed in `docs/agent/verification-matrix.md`.

## Workflow hygiene

- `permissions: contents: read` at the top. Grant more only to the job that
  needs it, with a comment saying why.
- Every job has `timeout-minutes`.
- Pull request runs cancel older runs of the same PR (`concurrency` with
  `cancel-in-progress` on pull requests only).
- Actions are pinned to a commit SHA (`dependencies.md`, GitHub Actions).
- Secrets are read only in the step that needs them, through `env:`.
- Triggers: pull requests and pushes to the default branch. Use
  `workflow_dispatch` only for manual runs; no `schedule:` unless the issue
  asks for one.

## CI is the source of truth

- Every check you are told to run locally also runs in CI.
- A check that could not run must not look like a pass. GitHub counts a
  skipped required job as passing, so a required job is never skipped:
  - When a secret it needs is missing, its first step fails with a message
    that names the secret. Never use `if:` on a secret to skip the job.
    It stays red until the owner adds the secret; there is no opt-out.
  - A required job that depends on another (`needs:`) runs with
    `if: always()` and fails unless that job succeeded.
- A required check proves the tests ran.
