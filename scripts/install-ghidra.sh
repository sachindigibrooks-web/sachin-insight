#!/usr/bin/env bash
# Installs Ghidra for REA native decompilation. Safe to re-run.
# Requires a 64-bit JDK 21+. Set GHIDRA_INSTALL_DIR=/opt/ghidra_12.1.4_PUBLIC
# in the environment so the REA MCP server can find it.
set -euo pipefail

VERSION=12.1.4
BUILD_DATE=20260921
SHA256=ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db
PREFIX=${GHIDRA_PREFIX:-/opt}
DEST="$PREFIX/ghidra_${VERSION}_PUBLIC"

if [ -x "$DEST/support/analyzeHeadless" ]; then
  echo "Ghidra $VERSION already installed at $DEST"
  exit 0
fi

ZIP=$(mktemp --suffix=.zip)
trap 'rm -f "$ZIP"' EXIT

curl -sSfL -o "$ZIP" \
  "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${VERSION}_build/ghidra_${VERSION}_PUBLIC_${BUILD_DATE}.zip"
echo "$SHA256  $ZIP" | sha256sum -c -
unzip -q "$ZIP" -d "$PREFIX"

echo "Installed Ghidra $VERSION at $DEST"
