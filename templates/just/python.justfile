# justfile for a Python project managed with uv. Copy to the repository root
# as `justfile`. Shared recipes: docs/agent/rules/ci.md.

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

# Build the wheel and sdist into dist/
build:
    uv build
