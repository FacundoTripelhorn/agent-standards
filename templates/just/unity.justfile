# justfile for a Unity project. Copy to the repository root as `justfile`.
# The recipes need a local Unity editor of the version in
# ProjectSettings/ProjectVersion.txt: set UNITY_PATH to its executable, e.g.
#   Windows: C:\Program Files\Unity\Hub\Editor\<version>\Editor\Unity.exe
#   macOS:   /Applications/Unity/Hub/Editor/<version>/Unity.app/Contents/MacOS/Unity
# Without it they stop with a message: report those checks as "not run".
# In CI the same EditMode tests run through GameCI. Shared recipes:
# docs/agent/rules/ci.md.

set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

unity := env("UNITY_PATH", "")
missing := "UNITY_PATH is not set, so this needs a local Unity editor. Report it as not run."

# List the recipes
default:
    @just --list

# Compile all scripts in batch mode; fails on compiler errors
[unix]
check:
    {{ if unity == "" { error(missing) } else { "" } }}
    "{{unity}}" -batchmode -nographics -quit -projectPath . -logFile -

[windows]
check:
    {{ if unity == "" { error(missing) } else { "" } }}
    & "{{unity}}" -batchmode -nographics -quit -projectPath . -logFile - | Out-Default; exit $LASTEXITCODE

# Nothing to autofix outside the editor
fix:
    @echo "No formatter is configured outside the Unity editor."

# Run the Edit Mode tests; results in artifacts/editmode-results.xml
[unix]
test:
    {{ if unity == "" { error(missing) } else { "" } }}
    "{{unity}}" -batchmode -nographics -projectPath . -runTests -testPlatform EditMode -testResults artifacts/editmode-results.xml -logFile -

[windows]
test:
    {{ if unity == "" { error(missing) } else { "" } }}
    & "{{unity}}" -batchmode -nographics -projectPath . -runTests -testPlatform EditMode -testResults artifacts/editmode-results.xml -logFile - | Out-Default; exit $LASTEXITCODE

# Player builds are made from the editor; no build is automated yet
build:
    @echo "No player build is automated yet. Builds are made from the Unity editor."
