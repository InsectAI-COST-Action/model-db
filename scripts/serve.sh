#!/usr/bin/env bash
#
# Start the local preview.
#
# There is no separate check to run first: Hugo validates every model card
# against data/schema.toml as it renders it, so a card with a missing required
# field or an unknown value stops the server here, with a message naming the
# file and the field.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

# Prefer the binary fetch-hugo.sh installed, but accept one from PATH. On macOS
# and Windows the package manager is the supported route, and fetch-hugo.sh only
# knows how to build Linux tarballs - so insisting on ./bin/hugo would turn away
# a contributor who already has the right binary.
HUGO="./bin/hugo"
if [[ ! -x "${HUGO}" ]]; then
  if command -v hugo >/dev/null 2>&1; then
    HUGO="$(command -v hugo)"
  else
    echo "No Hugo found. Run ./scripts/fetch-hugo.sh, or install Hugo extended." >&2
    exit 1
  fi
fi

echo "Serving on http://localhost:1313/  (Ctrl-C to stop)"
echo

# --baseURL is overridden to localhost so the preview lives at the site root.
# hugo.toml carries the real GitHub Pages subpath, and without this override the
# dev server would serve it under /insect-model-zoo/ as well. All internal links
# go through relURL, so both work - this is purely about the address you type.
exec "${HUGO}" server \
  --port 1313 \
  --bind 127.0.0.1 \
  --baseURL "http://localhost:1313/" \
  "$@"
