#!/usr/bin/env bash
#
# Download the standalone Hugo extended binary into ./bin/hugo.
#
# The checksum is verified against the release's own published checksum file
# rather than a hash pinned in this repo, so the script does not rot when Hugo
# publishes a new patch release.

set -euo pipefail

VER="${HUGO_VERSION:-0.166.0}"
ARCH="${HUGO_ARCH:-linux-amd64}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="${ROOT}/bin"
TARBALL="hugo_extended_${VER}_${ARCH}.tar.gz"
BASE="https://github.com/gohugoio/hugo/releases/download/v${VER}"

if [[ -x "${BIN}/hugo" ]] && "${BIN}/hugo" version 2>/dev/null | grep -q "v${VER}"; then
  echo "hugo v${VER} already present at bin/hugo - nothing to do."
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

echo "==> Downloading hugo extended v${VER} (${ARCH})"
curl -fsSL -o "${TMP}/${TARBALL}" "${BASE}/${TARBALL}"
curl -fsSL -o "${TMP}/checksums.txt" "${BASE}/hugo_${VER}_checksums.txt"

echo "==> Verifying SHA-256"
grep " ${TARBALL}\$" "${TMP}/checksums.txt" > "${TMP}/expected.sum" || {
  echo "ERROR: ${TARBALL} not found in the published checksum file." >&2
  exit 1
}
(cd "${TMP}" && sha256sum -c expected.sum)

echo "==> Extracting to bin/"
mkdir -p "${BIN}"
tar -xzf "${TMP}/${TARBALL}" -C "${BIN}" hugo
chmod +x "${BIN}/hugo"

echo "==> Installed:"
"${BIN}/hugo" version

if ! "${BIN}/hugo" version | grep -q '+extended'; then
  echo "WARNING: this is not the extended build; asset pipeline features may be missing." >&2
fi

echo
echo "Run './scripts/serve.sh' to start the local preview."
