#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile"
BUILD="$BASE/CMakeBuild"
ART="$BASE/artifacts"
LOG="$BASE/log"
STATUS="$BASE/status"

mkdir -p "$BASE" "$ART" "$LOG" "$STATUS"

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

echo "project=libsndfile" >> "$PROJLOG"
echo "source=$SRC" >> "$PROJLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
echo "policy=README cmake flow (mkdir CMakeBuild; cmake ..; cmake --build .) with clang-14 -O2 -g" >> "$PROJLOG"

run rm -rf "$BUILD"
run mkdir -p "$BUILD"

run cmake -S "$SRC" -B "$BUILD" -G "Unix Makefiles" \
  -DCMAKE_C_COMPILER=clang-14 \
  -DCMAKE_CXX_COMPILER=clang++-14 \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_C_FLAGS_DEBUG="-O2 -g" \
  -DCMAKE_CXX_FLAGS_DEBUG="-O2 -g" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

run cmake --build "$BUILD" -j"$(nproc)"

run cp -f "$BUILD/compile_commands.json" "$ART/compile_commands.json"

log_cmd python3_verify_flags_and_collect_outputs
python3 - <<'PY' >> "$PROJLOG" 2>&1
from pathlib import Path
import json

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g')
build = base / 'CMakeBuild'
art = base / 'artifacts'

ccdb = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))
total = len(ccdb)
with_o2 = 0
with_g = 0
with_o3 = 0
for e in ccdb:
    cmd = e.get('command', '')
    if ' -O2 ' in f' {cmd} ':
        with_o2 += 1
    if ' -g ' in f' {cmd} ':
        with_g += 1
    if ' -O3 ' in f' {cmd} ':
        with_o3 += 1

manifest = []
for p in sorted(build.rglob('*')):
    if not p.is_file():
        continue
    name = p.name
    if name.startswith('libsndfile') or name.startswith('sndfile-') or name in ('sndfile-convert', 'sndfile-cmp', 'sndfile-info', 'sndfile-play', 'sndfile-metadata-get', 'sndfile-metadata-set'):
        manifest.append(str(p))

(art / 'build_outputs.list').write_text(''.join(x + '\n' for x in manifest), encoding='utf-8')
(art / 'compile_flag_check.txt').write_text(
    f'total_compile_commands={total}\n'
    f'commands_with_O2={with_o2}\n'
    f'commands_with_g={with_g}\n'
    f'commands_with_O3={with_o3}\n',
    encoding='utf-8',
)

print('total_compile_commands', total)
print('commands_with_O2', with_o2)
print('commands_with_g', with_g)
print('commands_with_O3', with_o3)
print('selected_outputs', len(manifest))
PY

{
  echo "build_dir=$BUILD"
  echo "compile_commands=$ART/compile_commands.json"
  echo "flag_check=$ART/compile_flag_check.txt"
  echo "outputs_manifest=$ART/build_outputs.list"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
