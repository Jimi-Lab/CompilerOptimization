#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/lepton"
BUILD="$BASE/lepton_build"
ART="$BASE/lepton_artifacts"
LOG="$BASE/lepton_log"
STATUS="$BASE/lepton_status"

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

echo "project=lepton" >> "$PROJLOG"
echo "source=$SRC" >> "$PROJLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
echo "policy=README cmake flow; clang-14 only; O2 and g" >> "$PROJLOG"

run rm -rf "$BUILD"
run mkdir -p "$BUILD"

# README CMAKE flow: mkdir build && cmake .. && make -j8
run cmake -S "$SRC" -B "$BUILD" -G "Unix Makefiles" \
  -DCMAKE_C_COMPILER=clang-14 \
  -DCMAKE_CXX_COMPILER=clang++-14 \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS_RELEASE="-O2 -g" \
  -DCMAKE_CXX_FLAGS_RELEASE="-O2 -g" \
  -DCMAKE_C_FLAGS="-std=c99 -DHAVE_CONFIG_H -O2 -g" \
  -DCMAKE_CXX_FLAGS="-std=c++11 -fno-exceptions -fno-rtti -O2 -g" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

run cmake --build "$BUILD" -j"$(nproc)"

run cp -f "$BUILD/compile_commands.json" "$ART/compile_commands.json"

log_cmd python3_recompile_lepton_objects_to_bc
python3 - <<'PY' >> "$PROJLOG" 2>&1
from pathlib import Path
import json
import shlex
import subprocess

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g')
build = base / 'lepton_build'
art = base / 'lepton_artifacts'
bcdir = art / 'bc_objs_lepton'
bcdir.mkdir(parents=True, exist_ok=True)

ccdb = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))
entries = [e for e in ccdb if 'CMakeFiles/lepton.dir/' in e.get('command', '')]
if not entries:
    raise SystemExit('No compile_commands entries found for target lepton')

bc_paths = []
for i, entry in enumerate(entries, start=1):
    if 'arguments' in entry:
        args = list(entry['arguments'])
    else:
        args = shlex.split(entry['command'])

    src = entry['file']
    out_bc = bcdir / f'lepton_obj_{i:03d}.bc'

    filtered = []
    skip_next = False
    for tok in args:
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
        # enforce requested optimization/debug policy in BC regen stage
        if tok.startswith('-O'):
            continue
        if tok == '-g' or tok.startswith('-g'):
            continue
        filtered.append(tok)

    cmd = filtered + ['-O2', '-g', '-emit-llvm', '-c', src, '-o', str(out_bc)]
    subprocess.run(cmd, check=True, cwd=entry['directory'])
    bc_paths.append(out_bc)

(art / 'bc_files_lepton.list').write_text(''.join(str(p) + '\n' for p in bc_paths), encoding='utf-8')
print('lepton_compile_entries', len(entries))
print('generated_bc', len(bc_paths))

contains_o2 = 0
contains_g = 0
for e in entries:
    c = e.get('command', '')
    if ' -O2 ' in f' {c} ':
        contains_o2 += 1
    if ' -g ' in f' {c} ':
        contains_g += 1
print('entries_with_O2', contains_o2)
print('entries_with_g', contains_g)
PY

log_cmd llvm-link-14_lepton_objects
llvm-link-14 $(python3 - <<'PY'
from pathlib import Path
lst = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/bc_files_lepton.list')
for line in lst.read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/lepton_O2_g.bc" >> "$LNKLOG" 2>&1

log_cmd llvm-dis-14_lepton_bc
llvm-dis-14 "$ART/lepton_O2_g.bc" -o "$ART/lepton_O2_g.ll" >> "$LNKLOG" 2>&1

log_cmd llvm-nm-14_main_symbol_check
llvm-nm-14 "$ART/lepton_O2_g.bc" > "$LOG/llvm_nm.log" 2>&1

MAIN_STATUS="$(python3 - <<'PY'
from pathlib import Path
txt = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_log/llvm_nm.log').read_text(encoding='utf-8', errors='replace')
print('present' if any(line.rstrip().endswith(' T main') for line in txt.splitlines()) else 'missing')
PY
)"

{
  echo "binary=$BUILD/lepton"
  echo "artifact_bc=$ART/lepton_O2_g.bc"
  echo "artifact_ll=$ART/lepton_O2_g.ll"
  echo "bc_list=$ART/bc_files_lepton.list"
  echo "main_symbol=$MAIN_STATUS"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
