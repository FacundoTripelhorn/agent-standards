# agent-standards' own checks. Shared recipes: docs/agent/rules/ci.md.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# The shared Markdown files and templates other repositories copy, kept in
# Prettier's default format so a repository's own Prettier accepts the copies.
# npx, not a dev dependency: this uv repository keeps no npm lockfile.
prettier := "npx --yes prettier@3.10.1 --no-config"
shared_markdown := "AGENTS.base.md 'docs/agent/rules/*.md' .github/pull_request_template.md '.github/ISSUE_TEMPLATE/*.md' 'templates/**/*.md'"

# List the recipes
default:
    @just --list

# Lint, format check and type check
check:
    uv run --locked ruff check .
    uv run --locked ruff format --check .
    uv run --locked mypy
    {{prettier}} --check {{shared_markdown}}

# Formatter and lint autofixes
fix:
    uv run --locked ruff format .
    uv run --locked ruff check --fix .
    {{prettier}} --write {{shared_markdown}}

# Run the tests
test:
    uv run --locked pytest

# Nothing is built: the action runs from source
build:
    @echo "Nothing to build: the action runs from source with uv."

# Run the shared checks on another repository, e.g. just run ../GhostMCP origin/main
run repo base:
    uv run --locked python -m standards --repo {{repo}} --base {{base}}
