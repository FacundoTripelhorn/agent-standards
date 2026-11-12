<!-- Title: "<KEY>-<number> <issue title>", e.g. "GHOST-47 Compare two armour instances".
It becomes the one-line commit on the default branch (squash merge).
Closing line: "Closes #47" for a GitHub issue, "Closes FAC-104" for a Linear issue. -->

Closes 

## What and why

<!-- One issue per PR. Write in the `language` set in project.yml. -->

## How I verified it

<!-- Exact commands and real results. Write "not run" and the reason for
anything you did not run. For a refactor, say how you know behaviour did
not change. -->

| Check | Result |
|---|---|
| Lint | |
| Format (check mode) | |
| Types | |
| Tests | |
| Build | |

## Base rules checklist

- [ ] No file or function grew past its limit (`docs/agent/rules/thresholds.md`), or the exception is listed in `size-exceptions.txt` with a reason
- [ ] No new bare literals for values the code compares, stores or sends; they are constants or enums
- [ ] No new `Any`, `@ts-nocheck`, `@ts-ignore` or warning suppressions
- [ ] No silently swallowed errors
- [ ] User data is never deleted or overwritten when it cannot be read
- [ ] Nothing from the request is shown to the user as a message or used as a redirect target
- [ ] Tests added or updated for the change; a bug fix has a test that fails without it
- [ ] Docs updated if behaviour, setup or an interface changed
- [ ] No secrets, tokens or real personal identifiers in code, fixtures, logs or this PR
