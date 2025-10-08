#!/usr/bin/env bash
set -euo pipefail

# Example usage:
# OSS_CAD_URL=https://example.com/oss-cad-suite.tar.gz OSS_CAD_SHA256=<sha256> ./tools/setup_tools.sh

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DST="$ROOT/tools/oss-cad-suite"
TMP_ARCHIVE="/tmp/oss-cad-suite.tar.gz"

: "${OSS_CAD_URL:??Need to set OSS_CAD_URL (ex: export OSS_CAD_URL=https://...) }"
: "${OSS_CAD_SHA256:-}"

echo "==> Root: $ROOT"
echo "==> Destination: $DST"
echo "==> Downloading OSS-CAD Suite from: $OSS_CAD_URL"

mkdir -p "$ROOT/tools"
rm -f "$TMP_ARCHIVE"
curl -L --fail --progress-bar "$OSS_CAD_URL" -o "$TMP_ARCHIVE"

if [ -n "${OSS_CAD_SHA256:-}" ]; then
  echo "==> Verifying SHA256..."
  echo "${OSS_CAD_SHA256}  $TMP_ARCHIVE" | sha256sum -c -
fi

echo "==> Extracting archive to $ROOT/tools ..."
# Try to extract safely. If the archive contains a top-level directory 'oss-cad-suite' it will be placed here.
mkdir -p "$DST"
tar -xzf "$TMP_ARCHIVE" -C "$ROOT/tools"

# Ensure executables are executable
if [ -d "$DST/bin" ]; then
  chmod -R a+rx "$DST/bin" || true
fi
if [ -d "$DST/libexec" ]; then
  chmod -R a+rx "$DST/libexec" || true
fi
if [ -d "$DST/py3bin" ]; then
  chmod -R a+rx "$DST/py3bin" || true
fi

rm -f "$TMP_ARCHIVE"

echo
echo "==> Done. Add OSS-CAD Suite to PATH for this shell with:"
echo "    export PATH=\"$ROOT/tools/oss-cad-suite/bin:$ROOT/tools/oss-cad-suite/py3bin:\$PATH\""
echo
echo "Optional: extract riscv toolchain if you put riscv tar in tools/:"
echo "    if [ -f \"$ROOT/tools/riscv32-toolchain.tar.gz\" ]; then mkdir -p \"$ROOT/tools/riscv32-toolchain\"; tar -xzf \"$ROOT/tools/riscv32-toolchain.tar.gz\" -C \"$ROOT/tools/riscv32-toolchain\" --strip-components=1; fi"
echo
echo "Now you can run: tools/oss-cad-suite/bin/openFPGALoader --detect -v"