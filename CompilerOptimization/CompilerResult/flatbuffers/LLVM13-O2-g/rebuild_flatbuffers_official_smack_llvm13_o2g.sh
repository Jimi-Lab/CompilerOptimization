#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers"
BUILD="$BASE/build"
ART="$BASE/artifacts"
LOG="$BASE/log"
STATUS="$BASE/status"

mkdir -p "$BASE" "$ART" "$LOG" "$STATUS"

CMDLOG="$LOG/commands.log"
PROJLOG="$LOG/project.log"
BCLOG="$LOG/bc_build.log"
LNKLOG="$LOG/llvm_link.log"

: > "$CMDLOG"
: > "$PROJLOG"
: > "$BCLOG"
: > "$LNKLOG"

log_cmd() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$CMDLOG"
}

run() {
  log_cmd "$*"
  "$@" >> "$PROJLOG" 2>&1
}

echo "project=flatbuffers" >> "$PROJLOG"
echo "source=$SRC" >> "$PROJLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
echo "policy=official cmake flow for flatc in SMACK llvm13; flags -O2 -g only; program-level bc" >> "$PROJLOG"

run rm -rf "$BUILD"

run cmake -S "$SRC" -B "$BUILD" -G "Unix Makefiles" \
  -DCMAKE_C_COMPILER=clang-13 \
  -DCMAKE_CXX_COMPILER=clang++-13 \
  -DCMAKE_C_FLAGS="-O2 -g" \
  -DCMAKE_CXX_FLAGS="-O2 -g" \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

run cmake --build "$BUILD" --target flatc -j"$(nproc)"

run cp -f "$BUILD/compile_commands.json" "$ART/compile_commands.json"
run cp -f "$BUILD/flatc" "$ART/flatc_O2_g"

log_cmd python3_recompile_flatc_objects_to_program_bc
python3 - <<'PY' >> "$BCLOG" 2>&1
from pathlib import Path
import json
import shlex
import subprocess

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g')
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
flag_rows = []
for i, entry in enumerate(flatc_entries, start=1):
    if 'arguments' in entry:
        args = list(entry['arguments'])
    else:
        args = shlex.split(entry['command'])

    src = entry['file']
    out_bc = bcdir / f'flatc_obj_{i:03d}.bc'

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
        if tok.startswith('-O'):
            continue
        if tok == '-g' or tok.startswith('-g'):
            continue
        filtered.append(tok)

    cmd = filtered + ['-O2', '-g', '-emit-llvm', '-c', src, '-o', str(out_bc)]
    subprocess.run(cmd, check=True, cwd=entry['directory'])
    bc_paths.append(out_bc)
    cmd_s = ' '.join(cmd)
    flag_rows.append((src, '-O2' in cmd_s, ' -g' in f' {cmd_s} ', '-O3' in cmd_s))

(art / 'bc_files_flatc.list').write_text(''.join(str(p) + '\n' for p in bc_paths), encoding='utf-8')
(art / 'bc_flag_audit.csv').write_text('file,has_O2,has_g,has_O3\n' + ''.join(f'{f},{int(o2)},{int(g)},{int(o3)}\n' for f, o2, g, o3 in flag_rows), encoding='utf-8')
print('flatc_compile_entries', len(flatc_entries))
print('generated_bc', len(bc_paths))
PY

log_cmd llvm-link-13_flatc_objects
llvm-link-13 $(python3 - <<'PY'
from pathlib import Path
lst = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/artifacts/bc_files_flatc.list')
for line in lst.read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/flatbuffers_flatc_O2_g.bc" >> "$LNKLOG" 2>&1

log_cmd llvm-dis-13_flatc_bc
llvm-dis-13 "$ART/flatbuffers_flatc_O2_g.bc" -o "$ART/flatbuffers_flatc_O2_g.ll" >> "$LNKLOG" 2>&1

log_cmd llvm-nm-13_symbol_check
llvm-nm-13 "$ART/flatbuffers_flatc_O2_g.bc" > "$LOG/llvm_nm.log" 2>&1

log_cmd llvm-nm-13_undefined_check
llvm-nm-13 --undefined-only "$ART/flatbuffers_flatc_O2_g.bc" > "$LOG/undefined_symbols.log" 2>&1

MAIN_STATUS="$(python3 - <<'PY'
from pathlib import Path
txt = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/log/llvm_nm.log').read_text(encoding='utf-8', errors='replace')
print('present' if any(line.rstrip().endswith(' T main') or line.rstrip().endswith(' t main') for line in txt.splitlines()) else 'missing')
PY
)"

UNDEFINED_COUNT="$(python3 - <<'PY'
from pathlib import Path
lines = [ln for ln in Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/log/undefined_symbols.log').read_text(encoding='utf-8', errors='replace').splitlines() if ln.strip()]
print(len(lines))
PY
)"

{
  echo "binary=$ART/flatc_O2_g"
  echo "artifact_bc=$ART/flatbuffers_flatc_O2_g.bc"
  echo "artifact_ll=$ART/flatbuffers_flatc_O2_g.ll"
  echo "bc_list=$ART/bc_files_flatc.list"
  echo "flag_audit=$ART/bc_flag_audit.csv"
  echo "main_symbol=$MAIN_STATUS"
  echo "undefined_symbol_count=$UNDEFINED_COUNT"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
