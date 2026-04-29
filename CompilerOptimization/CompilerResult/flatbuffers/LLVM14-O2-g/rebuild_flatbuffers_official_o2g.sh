#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers"
BUILD="$BASE/build"
ART="$BASE/artifacts"
LOG="$BASE/log"
STATUS="$BASE/status"

mkdir -p "$BASE" "$BUILD" "$ART" "$LOG" "$STATUS"

CMDLOG="$LOG/commands.log"
PROJLOG="$LOG/project.log"
LNKLOG="$LOG/llvm_link.log"

: > "$CMDLOG"
: > "$PROJLOG"
: > "$LNKLOG"

log_cmd() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$CMDLOG"
}

run() {
  log_cmd "$*"
  "$@" >> "$PROJLOG" 2>&1
}

echo "project=flatbuffers" >> "$PROJLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
echo "policy=official_cmake_target_flatc; clang-14 only; flags O2 and g only" >> "$PROJLOG"

run cmake -S "$SRC" -B "$BUILD" -G "Unix Makefiles" \
  -DCMAKE_C_COMPILER=clang-14 \
  -DCMAKE_CXX_COMPILER=clang++-14 \
  -DCMAKE_C_FLAGS="-O2 -g" \
  -DCMAKE_CXX_FLAGS="-O2 -g" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# Build only the official compiler target to keep main-containing executable semantics.
run cmake --build "$BUILD" --target flatc -j"$(nproc)"

run cp -f "$BUILD/compile_commands.json" "$ART/compile_commands.json"

log_cmd python3_recompile_flatc_objects_to_bc
python3 - <<'PY' >> "$PROJLOG" 2>&1
from pathlib import Path
import json
import shlex
import subprocess

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g')
build = base / 'build'
art = base / 'artifacts'
bcdir = art / 'bc_objs_flatc'
bcdir.mkdir(parents=True, exist_ok=True)

ccdb = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))
flatc_entries = []
for entry in ccdb:
    cmd_s = entry.get('command', '')
    if 'CMakeFiles/flatc.dir/' in cmd_s:
        flatc_entries.append(entry)

if not flatc_entries:
    raise SystemExit('No compile_commands entries found for target flatc')

bc_paths = []
for i, entry in enumerate(flatc_entries, start=1):
    if 'arguments' in entry:
        args = list(entry['arguments'])
    else:
        args = shlex.split(entry['command'])

    src = entry['file']
    out_bc = bcdir / f'flatc_obj_{i:03d}.bc'

    filtered = []
    skip_next = False
    for idx, tok in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if tok == '-o':
            skip_next = True
            continue
        if tok == '-c':
            continue
        if tok == src:
            continue
        filtered.append(tok)

    cmd = filtered + ['-emit-llvm', '-c', src, '-o', str(out_bc)]
    subprocess.run(cmd, check=True, cwd=entry['directory'])
    bc_paths.append(out_bc)

(art / 'bc_files_flatc.list').write_text(''.join(str(p) + '\n' for p in bc_paths), encoding='utf-8')
print('flatc_compile_entries', len(flatc_entries))
print('generated_bc', len(bc_paths))
PY

log_cmd llvm-link-14_flatc_objects
llvm-link-14 $(python3 - <<'PY'
from pathlib import Path
lst = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_files_flatc.list')
for line in lst.read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/flatbuffers_flatc_O2_g.bc" >> "$LNKLOG" 2>&1

log_cmd llvm-dis-14_flatc_bc
llvm-dis-14 "$ART/flatbuffers_flatc_O2_g.bc" -o "$ART/flatbuffers_flatc_O2_g.ll" >> "$LNKLOG" 2>&1

log_cmd llvm-nm-14_main_symbol_check
llvm-nm-14 "$ART/flatbuffers_flatc_O2_g.bc" > "$LOG/llvm_nm.log" 2>&1

MAIN_STATUS="$(python3 - <<'PY'
from pathlib import Path
txt = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/log/llvm_nm.log').read_text(encoding='utf-8', errors='replace')
print('present' if any(line.rstrip().endswith(' T main') for line in txt.splitlines()) else 'missing')
PY
)"

{
  echo "artifact_bc=$ART/flatbuffers_flatc_O2_g.bc"
  echo "artifact_ll=$ART/flatbuffers_flatc_O2_g.ll"
  echo "bc_list=$ART/bc_files_flatc.list"
  echo "main_symbol=$MAIN_STATUS"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
