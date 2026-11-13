# justfile for a TypeScript project. Copy to the repository root as
# `justfile` and set `pm` to the package_manager in project.yml.
# The recipes call package.json scripts, which must exist: lint,
# lint:fix, format:check, format, typecheck, test, build. Shared recipes:
# docs/agent/rules/ci.md.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

pm := "pnpm"

# List the recipes
default:
    @just --list

# Lint, format check and type check
check:
    {{pm}} run lint
    {{pm}} run format:check
    {{pm}} run typecheck

# Formatter and lint autofixes
fix:
    {{pm}} run format
    {{pm}} run lint:fix

# Run the tests
test:
    {{pm}} run test

# Build
build:
    {{pm}} run build
