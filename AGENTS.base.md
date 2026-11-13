<!-- agent-standards:base v0.7 — synced from agent-standards. Edit it there, not here. -->
## Shared rules

These rules apply to all of the owner's repositories. The project sections
above this block come first: if one of them disagrees with a shared rule,
follow the project section and point out the conflict in your PR.

`project.yml` gives the project key (`FAC`, `GHOST`…), the language for
PRs, issues and docs, the issue tracker, the package manager and where the
version lives.

### Commands

Every repository runs its checks with [just](https://just.systems), under
the same names:

| Command | What it runs |
|---|---|
| `just check` | Lint, format check, type check |
| `just fix` | Formatter and lint autofixes |
| `just test` | The tests |
| `just build` | The build |

`just --list` shows the project's other recipes. When a recipe cannot run
here (for example, there is no Unity editor), it stops with a message that
says so. Report that check as "not run", never as passed.

### Before you start

- Work on one issue only. If you find something else that needs fixing,
  mention it in the PR instead of fixing it.
- Read `docs/agent/repo-map.md` to find where things live,
  `docs/agent/verification-matrix.md` to see what to run, and
  `docs/agent/known-non-bugs.md` to see what is intended.
- Before some kinds of work, also read the rule file for it:

  | Before you… | Read |
  |---|---|
  | write or change code | `docs/agent/rules/code.md` |
  | handle input, files, secrets or saved data | `docs/agent/rules/security.md` |
  | create a branch, commit, open a PR or release | `docs/agent/rules/workflow.md` |
  | add, remove or upgrade a dependency | `docs/agent/rules/dependencies.md` |
  | change a workflow or a `justfile` | `docs/agent/rules/ci.md` |
  | add, move or edit a document | `docs/agent/rules/docs.md` |

### Code

- Files and functions stay under the limits in
  `docs/agent/rules/thresholds.md`. If a file is already over its limit,
  move code out of it before you add anything.
- Use a named constant or enum for every value the code compares, branches
  on, stores or sends, even if it appears only once: `Status.PAID`, not
  `"paid"`. Each value gets one name: copying it into a second constant to
  get past the check breaks this rule.
- Type all new code. Do not add `Any`, `@ts-nocheck`, `@ts-ignore` or
  `#pragma warning disable`.
- Handle every error or let it propagate. Never catch an error and do
  nothing with it.
- Each piece of logic lives in one place. If two languages share a data
  format, generate one side from the other, or add a test that checks
  they still match.
- Respect the module boundaries in this file's Architecture section.
- Every change comes with tests. A bug fix includes a test that fails
  without the fix.

### Input and user data

- Treat all outside input as untrusted. That includes requests, files, env
  vars, CLI arguments, API and LLM responses, and rows that users wrote.
  Validate it with a schema where it enters.
- Escape or encode input for where it is used: SQL parameters, argument
  lists for subprocesses, template escaping. Never put input in a message
  you show back or in a redirect target.
- If saved user data cannot be read, keep the file and report the error.
  Never delete or overwrite it.

### Branches, commits and PRs

- Branch name is the issue ID: `GHOST-47`. Use `claude/GHOST-47` only when
  the platform requires a prefix.
- PR title is the ID plus the issue title: `GHOST-47 Compare two armour
  instances`. It becomes the single squash commit.
- In the PR, list every check you ran with its real result. Write "not run"
  and the reason for any check you skipped.
- When code changes a fact that a doc states, update that doc in the same
  PR.

### Ask the owner first

- Adding, removing or upgrading a dependency.
- Changing CI, the `justfile`, linter or formatter settings, or repository
  settings.
- Creating a new document outside the list in `docs/agent/rules/docs.md`.

### Never

- Commit secrets, tokens or real personal data, including in test fixtures.
  Never write them to logs either.
- Push to the default branch, rewrite history on a branch you did not
  create, or merge a PR.
- Change the version unless the issue is a release. Never create tags: the
  owner tags releases.
- Skip, disable or delete a test to make CI pass.
- Edit this block or `docs/agent/rules/` in this repository. Change them in
  agent-standards.
<!-- /agent-standards:base -->
