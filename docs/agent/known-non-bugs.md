# Known non-bugs

Behaviour that looks wrong but is intended. Before "fixing" something on this
list, ask.

## Literals and duplicate constants are not checked

- **What you see:** a bare string comparison passes CI.
- **Why it is intended:** names over literals is a practice, reviewed by a
  person. The owner decided CI checks only mechanical rules.
- **Do not:** add a literal or duplicate-value check, or turn on ruff
  `allow-magic-value-types = []`.

## The branch name is not checked

- **What you see:** a branch like `claude/exciting-curie-0e7103` passes.
- **Why it is intended:** agent platforms choose their own branch names. The
  PR title is what lands on the default branch, and that is checked.
- **Do not:** add a branch-name check.

## No size or suppression findings without a base commit

- **What you see:** a first push, or a run with no `--base`, reports only
  `project.yml`, PR title and release tag.
- **Why it is intended:** the ratchet compares with the base; without one it
  cannot tell old debt from new, so it skips instead of reporting everything.
- **Do not:** fall back to checking every file against the limits.

## Function size is skipped in test files

- **What you see:** a 400-line `describe` callback passes.
- **Why it is intended:** a test suite is one long callback by design. File
  size still applies.
- **Do not:** remove the test-path exemption.

## Rule files say "synced from agent-standards" here too

- **What you see:** files in `docs/agent/rules/` and `AGENTS.base.md` say to
  edit them in agent-standards, and this is agent-standards. Their header
  shows `{agent-standards-version}` instead of a version.
- **Why it is intended:** the header is written for the copies in other
  repositories; `standards-sync` replaces the placeholder with the release
  line when it writes them. Here, edit the files in place.
- **Do not:** remove the header or write a version over the placeholder.

## No drift check here, nor without project.yml

- **What you see:** the shared-copy check reports nothing in agent-standards,
  and nothing in a repository that has no `project.yml` yet.
- **Why it is intended:** agent-standards holds the originals, not copies. A
  repository without `project.yml` has not adopted the rules; its
  `project.yml` finding already says so.
- **Do not:** compare the originals with themselves, or flood an unadopted
  repository with one finding per missing copy.

## Quick triage

| Observation | Likely cause | Action |
|---|---|---|
| `project.yml` finding in a repository without one | Not adopted yet | Expected until its adoption PR |
| Suppression finding on a deliberate `Any` | No reason given | Add `allow-suppression: <why>` on its line |
| `standards` passes here but fails elsewhere | That repository pins an older SHA | Update the pin in that repository |
| Shared-copy finding after a Dependabot pin update | The copies are still the old version | Run `standards-sync` with the new commit in that PR |
