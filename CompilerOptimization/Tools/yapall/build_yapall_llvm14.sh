#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YAPALL_SRC="${YAPALL_SRC:-$SCRIPT_DIR/yapall}"

cd "$YAPALL_SRC"

command -v cargo >/dev/null 2>&1 || {
  echo "ERROR: cargo is not available in PATH." >&2
  echo "Install Rust/Cargo or provide a prebuilt yapall binary via YAPALL_BIN." >&2
  exit 127
}

command -v llvm-config-14 >/dev/null 2>&1 || {
  echo "ERROR: llvm-config-14 is not available in PATH." >&2
  echo "yapall in this workspace is built against llvm-ir with the llvm-14 feature." >&2
  exit 127
}

LLVM_CONFIG_PATH="${LLVM_CONFIG_PATH:-$(command -v llvm-config-14)}"
export LLVM_CONFIG_PATH

cargo build --release

echo "$YAPALL_SRC/target/release/yapall"
