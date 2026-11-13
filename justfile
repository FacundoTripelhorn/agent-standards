# agent-standards' own checks. Shared recipes: docs/agent/rules/ci.md.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# List the recipes
default:
    @just --list

# Lint, format check and type check
check:
    uv run --locked ruff check .
    uv run --locked ruff format --check .
    uv run --locked mypy

# Formatter and lint autofixes
fix:
    uv run --locked ruff format .
    uv run --locked ruff check --fix .

# Run the tests
test:
    uv run --locked pytest

# Nothing is built: the action runs from source
build:
    @echo "Nothing to build: the action runs from source with uv."

# Run the shared checks on another repository, e.g. just run ../GhostMCP origin/main
run repo base:
    uv run --locked python -m standards --repo {{repo}} --base {{base}}
