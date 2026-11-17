#!/usr/bin/env bash
# install.sh <archive-url> <sha256> <dest-dir>
#
# Downloads the just archive, checks it against <sha256>, extracts `just`
# into <dest-dir> and adds that folder to the job's PATH ($GITHUB_PATH).
# Any failure stops before anything is installed.
set -euo pipefail

SUPPORTED_OS=Linux
SUPPORTED_ARCH=X64
BINARY=just
TITLE="title=setup-just"

if [ "$#" -ne 3 ]; then
  echo "usage: install.sh <archive-url> <sha256> <dest-dir>" >&2
  exit 2
fi
url=$1
sha256=$2
dest=$3

if [ "${RUNNER_OS:-}" != "$SUPPORTED_OS" ] || [ "${RUNNER_ARCH:-}" != "$SUPPORTED_ARCH" ]; then
  echo "::error ${TITLE}::Only Linux x64 runners are supported (this one is ${RUNNER_OS:-unknown} ${RUNNER_ARCH:-unknown})."
  exit 1
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
archive="$work/just.tar.gz"

curl -fsSL "$url" -o "$archive"
if ! echo "$sha256  $archive" | sha256sum --check --status -; then
  echo "::error ${TITLE}::The download does not match the pinned sha256; nothing was installed."
  exit 1
fi

tar -xzf "$archive" -C "$work" "$BINARY"
mkdir -p "$dest"
install -m 0755 "$work/$BINARY" "$dest/$BINARY"
echo "$dest" >> "$GITHUB_PATH"
"$dest/$BINARY" --version
