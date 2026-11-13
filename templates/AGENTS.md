# <Project name>

<!-- Project part: written per repository, kept short. Only what an agent
cannot guess from the code or from the shared rules below. Add a rule here
when an agent repeats a mistake, not before. Delete these comments. -->

<One or two sentences: what this is, who uses it, the stack.>

## Commands

`just check`, `just fix`, `just test` and `just build` are described in the
shared rules below. This project also has:

| Do this | Command |
|---|---|
| Run the app | `just dev` |

## Architecture

<!-- At most 10 lines. The detail lives in docs/design.md. -->

- **Modules:** `<a>` → `<b>` → `<c>`. Imports only go in the direction of
  the arrows.
- **External systems:** <APIs, stores, hardware it talks to, and through
  which module>.
- **Invariants:** <the 3 to 5 things that must never break, each with a
  one-line reason. For example: "Money is `Decimal`, never `float`: the
  tax authority rejects rounding differences.">

## Versioning and release

- The version lives in `<version_file from project.yml>`.
- A release is the tag `v<version>` on the default branch.
- <How it ships: installer, package registry, store build, or not at all.>

## Project rules

<!-- Only conventions specific to this project, each with a one-line reason
or an example. -->

- <rule>

## Other documents

<!-- Documents beyond the standard set in docs/agent/rules/docs.md, each
with its one job. The owner approves additions. Delete the section if
there are none. -->

| File | Its one job |
|---|---|
| | |

<!-- agent-standards:base — the shared block is inserted here by the sync. -->
