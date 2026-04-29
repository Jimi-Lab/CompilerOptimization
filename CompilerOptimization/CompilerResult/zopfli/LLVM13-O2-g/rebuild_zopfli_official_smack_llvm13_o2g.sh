#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/zopfli"
WORK="$BASE/work/zopfli-src"
ART="$BASE/artifacts"
LOG="$BASE/log"
STATUS="$BASE/status"

mkdir -p "$BASE" "$ART" "$LOG" "$STATUS" "$BASE/work"

CMDLOG="$LOG/commands.log"
BUILDLOG="$LOG/build.log"
BCLOG="$LOG/bc_build.log"
LNKLOG="$LOG/bc_link.log"

: > "$CMDLOG"
: > "$BUILDLOG"
: > "$BCLOG"
: > "$LNKLOG"

log_cmd() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$CMDLOG"
}

run() {
  log_cmd "$*"
  "$@" >> "$BUILDLOG" 2>&1
}

echo "project=zopfli" >> "$BUILDLOG"
echo "source=$SRC" >> "$BUILDLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$BUILDLOG"
echo "policy=README direct compile of src/zopfli/*.c with clang-13; -O2 -g; program-level bc" >> "$BUILDLOG"

if [[ -d "$WORK" ]]; then
  log_cmd chmod_existing_work_tree
  chmod -R u+w "$WORK" >> "$BUILDLOG" 2>&1 || true
fi

run rm -rf "$WORK"
run mkdir -p "$WORK"
run cp -a "$SRC/." "$WORK/"
run chmod -R u+w "$WORK"

log_cmd clang13_build_zopfli_binary
python3 - <<'PY' >> "$BUILDLOG" 2>&1
from pathlib import Path
import subprocess

work = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/work/zopfli-src')
art = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/artifacts')
sources = sorted((work / 'src' / 'zopfli').glob('*.c'))
if not sources:
    raise SystemExit('No zopfli C sources found under src/zopfli')
cmd = ['clang-13'] + [str(s) for s in sources] + ['-O2', '-g', '-W', '-Wall', '-Wextra', '-Wno-unused-function', '-ansi', '-pedantic', '-lm', '-o', str(art / 'zopfli_O2_g')]
subprocess.run(cmd, check=True, cwd=work)
print('source_count', len(sources))
print('binary', art / 'zopfli_O2_g')
PY

log_cmd python3_generate_program_bc
python3 - <<'PY' >> "$BCLOG" 2>&1
from pathlib import Path
import csv
import subprocess

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g')
work = base / 'work' / 'zopfli-src'
art = base / 'artifacts'
bcdir = art / 'bc_objs'
bcdir.mkdir(parents=True, exist_ok=True)

sources = sorted((work / 'src' / 'zopfli').glob('*.c'))
if not sources:
    raise SystemExit('No zopfli C sources found under src/zopfli')

bc_paths = []
audit_rows = []
for src in sources:
    out = bcdir / (src.stem + '.bc')
    cmd = ['clang-13', str(src), '-O2', '-g', '-W', '-Wall', '-Wextra', '-Wno-unused-function', '-ansi', '-pedantic', '-emit-llvm', '-c', '-o', str(out)]
    subprocess.run(cmd, check=True, cwd=work)
    bc_paths.append(out)
    joined = ' '.join(cmd)
    audit_rows.append((str(src), int('-O2' in joined), int(' -g' in f' {joined} '), int('-O3' in joined)))

(art / 'bc_files_zopfli_program.list').write_text(''.join(str(p) + '\n' for p in bc_paths), encoding='utf-8')
with (art / 'bc_flag_audit.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['file', 'has_O2', 'has_g', 'has_O3'])
    w.writerows(audit_rows)

print('source_count', len(sources))
print('bc_count', len(bc_paths))
PY

log_cmd llvm-link-13_program_bc
llvm-link-13 $(python3 - <<'PY'
from pathlib import Path
lst = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/artifacts/bc_files_zopfli_program.list')
for line in lst.read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/zopfli_O2_g.bc" >> "$LNKLOG" 2>&1

log_cmd llvm-dis-13_program_bc
llvm-dis-13 "$ART/zopfli_O2_g.bc" -o "$ART/zopfli_O2_g.ll" >> "$LNKLOG" 2>&1

log_cmd llvm-nm-13_main_check
llvm-nm-13 "$ART/zopfli_O2_g.bc" > "$LOG/llvm_nm.log" 2>&1

log_cmd llvm-nm-13_undefined_check
llvm-nm-13 --undefined-only "$ART/zopfli_O2_g.bc" > "$LOG/undefined_symbols.log" 2>&1

MAIN_STATUS="$(python3 - <<'PY'
from pathlib import Path
txt = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/log/llvm_nm.log').read_text(encoding='utf-8', errors='replace')
print('present' if any(line.rstrip().endswith(' T main') or line.rstrip().endswith(' t main') for line in txt.splitlines()) else 'missing')
PY
)"

UNDEFINED_COUNT="$(python3 - <<'PY'
from pathlib import Path
lines = [ln for ln in Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/log/undefined_symbols.log').read_text(encoding='utf-8', errors='replace').splitlines() if ln.strip()]
print(len(lines))
PY
)"

{
  echo "binary=$ART/zopfli_O2_g"
  echo "artifact_bc=$ART/zopfli_O2_g.bc"
  echo "artifact_ll=$ART/zopfli_O2_g.ll"
  echo "bc_list=$ART/bc_files_zopfli_program.list"
  echo "flag_audit=$ART/bc_flag_audit.csv"
  echo "main_symbol=$MAIN_STATUS"
  echo "undefined_symbol_count=$UNDEFINED_COUNT"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$BUILDLOG"
