# Verification matrix

Which checks to run for which kind of change. CI runs the full set on every
PR; this page tells you what to run while working and what CI cannot prove.

## Default order

| Step | Command | When |
|---|---|---|
| Lint and format | `make fix`, then `make check` | Every change |
| Tests | `make test` | Every change |
| Build | `<command>` | Changes to packaging or the build |

## Narrow checks by task type

| Task type | Paths | Run |
|---|---|---|
| <Area> | `<paths>` | `<test command for just that area>` |
| Docs only | `docs/`, `AGENTS.md` | None; check links |

## What only the owner can verify

Checks that need real credentials, real devices or a human judgement. An
agent says "not run" for these and lists them in the PR.

| Check | When it is needed | How |
|---|---|---|
| <e.g. login against the real provider> | <changes to auth> | <steps or link> |
