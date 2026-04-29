#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/Tengine"
BUILD="$BASE/build"
INSTALL="$BASE/install"
ART="$BASE/artifacts"
LOG="$BASE/log"
STATUS="$BASE/status"

mkdir -p "$BASE" "$BUILD" "$INSTALL" "$ART" "$LOG" "$STATUS"

CMDLOG="$LOG/commands.log"
PROJLOG="$LOG/project.log"

: > "$CMDLOG"
: > "$PROJLOG"

log_cmd() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$CMDLOG"
}

run() {
  log_cmd "$*"
  "$@" >> "$PROJLOG" 2>&1
}

echo "project=tengine" >> "$PROJLOG"
echo "source=$SRC" >> "$PROJLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
echo "policy=official README cmake flow; CMAKE_BUILD_TYPE=Debug; clang-14; O2 and g requested" >> "$PROJLOG"

run rm -rf "$BUILD" "$INSTALL"
run mkdir -p "$BUILD" "$INSTALL"

run cmake -S "$SRC" -B "$BUILD" -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_COMPILER=clang-14 \
  -DCMAKE_CXX_COMPILER=clang++-14 \
  -DCMAKE_C_FLAGS="-O2 -g" \
  -DCMAKE_CXX_FLAGS="-O2 -g" \
  -DCMAKE_C_FLAGS_DEBUG="-O2 -g" \
  -DCMAKE_CXX_FLAGS_DEBUG="-O2 -g" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_INSTALL_PREFIX="$INSTALL"

run cmake --build "$BUILD" -j"$(nproc)"
run cmake --install "$BUILD"

run cp -f "$BUILD/compile_commands.json" "$ART/compile_commands.json"

log_cmd python3_check_compile_flags
python3 - <<'PY' > "$ART/compile_flag_check.txt"
from pathlib import Path
import json

cc = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/compile_commands.json')
db = json.loads(cc.read_text(encoding='utf-8'))

total = len(db)
has_o2 = 0
has_g = 0
has_o0 = 0
has_clang14 = 0
for e in db:
    cmd = e.get('command', '')
    sp = f' {cmd} '
    if ' -O2 ' in sp:
        has_o2 += 1
    if ' -g ' in sp or ' -g3 ' in sp:
        has_g += 1
    if ' -O0 ' in sp:
        has_o0 += 1
    if 'clang-14' in cmd or 'clang++-14' in cmd:
        has_clang14 += 1

print(f'total_entries={total}')
print(f'entries_with_O2={has_o2}')
print(f'entries_with_g={has_g}')
print(f'entries_with_O0={has_o0}')
print(f'entries_with_clang14={has_clang14}')
PY

{
  echo "build_dir=$BUILD"
  echo "install_dir=$INSTALL"
  echo "compile_db=$ART/compile_commands.json"
  echo "compile_flag_check=$ART/compile_flag_check.txt"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
