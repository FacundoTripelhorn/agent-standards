# Design

<!-- How the system works now, and why. It expands the Architecture section
of AGENTS.md: do not repeat its module order or invariants here, link to
them. State only what is true now; delete what stops being true. -->

## Context

<What problem this solves, for whom, and the constraints that shape it.>

## Components

| Component | Path | Responsibility |
|---|---|---|
| <name> | `<path>` | <one line> |

## Data flow

<The main path a request, command or frame takes through the components.
A short numbered list or one diagram.>

## External systems

| System | Used for | Through | Failure behaviour |
|---|---|---|---|
| <API, store, device> | <what for> | `<module>` | <what happens when it is down> |

## Trade-offs that still hold

<Each choice that looks odd without its reason, and the reason. Remove an
entry when the choice changes.>

- **<Choice>.** <Why, and what would make us revisit it.>
