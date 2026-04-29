#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/lepton"
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

echo "project=lepton" >> "$PROJLOG"
echo "source=$SRC" >> "$PROJLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
echo "policy=README Using CMAKE flow (mkdir -p build; cd build; cmake ..; make -j8) in SMACK llvm13; force -O2 -g; program-level bc" >> "$PROJLOG"

run rm -rf "$BUILD"
run mkdir -p "$BUILD"

# Follow README CMAKE flow while preventing injected -O3/-DNDEBUG defaults.
run bash -lc "cd '$BUILD' && cmake '$SRC' -DCMAKE_C_COMPILER=clang-13 -DCMAKE_CXX_COMPILER=clang++-13 -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS_RELEASE='-O2 -g' -DCMAKE_CXX_FLAGS_RELEASE='-O2 -g' -DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
run bash -lc "cd '$BUILD' && make -j8"

run cp -f "$BUILD/compile_commands.json" "$ART/compile_commands.json"
run cp -f "$BUILD/lepton" "$ART/lepton_O2_g"

log_cmd python3_recompile_lepton_and_local_libs_to_program_bc
python3 - <<'PY' >> "$BCLOG" 2>&1
from pathlib import Path
import csv
import json
import shlex
import subprocess

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g')
build = base / 'build'
art = base / 'artifacts'
bcdir = art / 'bc_objs_lepton'
bcdir.mkdir(parents=True, exist_ok=True)

ccdb = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))
selected = []
for entry in ccdb:
    cmd = entry.get('command', '')
    if any(tag in cmd for tag in ('CMakeFiles/lepton.dir/', 'CMakeFiles/localmd5.dir/', 'CMakeFiles/localzlib.dir/', 'CMakeFiles/localbrotli.dir/')):
        selected.append(entry)

if not selected:
    raise SystemExit('No compile_commands entries found for lepton program and local dependency libraries')

bc_paths = []
audit_rows = []
for i, entry in enumerate(selected, start=1):
    args = list(entry['arguments']) if 'arguments' in entry else shlex.split(entry['command'])
    src = entry['file']
    out_bc = bcdir / f'lepton_obj_{i:04d}.bc'

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
    joined = ' '.join(cmd)
    audit_rows.append((src, int('-O2' in joined), int(' -g' in f' {joined} '), int('-O3' in joined)))

(art / 'bc_files_lepton_program.list').write_text(''.join(str(p) + '\n' for p in bc_paths), encoding='utf-8')
with (art / 'bc_flag_audit.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['file', 'has_O2', 'has_g', 'has_O3'])
    w.writerows(audit_rows)

print('selected_compile_entries', len(selected))
print('generated_bc_files', len(bc_paths))
PY

log_cmd llvm-link-13_lepton_program_bc
llvm-link-13 $(python3 - <<'PY'
from pathlib import Path
lst = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/artifacts/bc_files_lepton_program.list')
for line in lst.read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/lepton_O2_g.bc" >> "$LNKLOG" 2>&1

log_cmd llvm-dis-13_lepton_program_bc
llvm-dis-13 "$ART/lepton_O2_g.bc" -o "$ART/lepton_O2_g.ll" >> "$LNKLOG" 2>&1

log_cmd llvm-nm-13_symbol_check
llvm-nm-13 "$ART/lepton_O2_g.bc" > "$LOG/llvm_nm.log" 2>&1

log_cmd llvm-nm-13_undefined_check
llvm-nm-13 --undefined-only "$ART/lepton_O2_g.bc" > "$LOG/undefined_symbols.log" 2>&1

MAIN_STATUS="$(python3 - <<'PY'
from pathlib import Path
txt = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/log/llvm_nm.log').read_text(encoding='utf-8', errors='replace')
print('present' if any(line.rstrip().endswith(' T main') or line.rstrip().endswith(' t main') for line in txt.splitlines()) else 'missing')
PY
)"

UNDEFINED_COUNT="$(python3 - <<'PY'
from pathlib import Path
lines = [ln for ln in Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/log/undefined_symbols.log').read_text(encoding='utf-8', errors='replace').splitlines() if ln.strip()]
print(len(lines))
PY
)"

{
  echo "binary=$ART/lepton_O2_g"
  echo "artifact_bc=$ART/lepton_O2_g.bc"
  echo "artifact_ll=$ART/lepton_O2_g.ll"
  echo "bc_list=$ART/bc_files_lepton_program.list"
  echo "flag_audit=$ART/bc_flag_audit.csv"
  echo "main_symbol=$MAIN_STATUS"
  echo "undefined_symbol_count=$UNDEFINED_COUNT"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$PROJLOG"
