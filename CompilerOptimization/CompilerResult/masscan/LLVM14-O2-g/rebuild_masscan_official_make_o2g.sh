#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/masscan"
WORK="$BASE/work/masscan-src"
ART="$BASE/artifacts"
LOG="$BASE/log"
STATUS="$BASE/status"

mkdir -p "$BASE" "$ART" "$LOG" "$STATUS" "$BASE/work"

CMDLOG="$LOG/commands.log"
BUILDLOG="$LOG/build.log"
BCLOG="$LOG/bc.log"

: > "$CMDLOG"
: > "$BUILDLOG"
: > "$BCLOG"

log_cmd() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$CMDLOG"
}

run_build() {
  log_cmd "$*"
  "$@" >> "$BUILDLOG" 2>&1
}

echo "project=masscan" >> "$BUILDLOG"
echo "source=$SRC" >> "$BUILDLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$BUILDLOG"
echo "policy=README make flow; clang-14 only; -O2 -g" >> "$BUILDLOG"

if [[ -d "$WORK" ]]; then
  log_cmd chmod_existing_work_uplusw
  chmod -R u+w "$WORK" >> "$BUILDLOG" 2>&1 || true
fi
run_build rm -rf "$WORK"
run_build mkdir -p "$WORK"
run_build cp -a "$SRC/." "$WORK/"
run_build chmod -R u+w "$WORK"

# Official README build is `make`; enforce clang-14 and required flags.
run_build make -C "$WORK" clean
run_build make -C "$WORK" CC=clang-14 CFLAGS="-g -ggdb -Wall -O2" -j"$(nproc)"

log_cmd cp_masscan_binary
cp -f "$WORK/bin/masscan" "$ART/masscan_O2_g" >> "$BUILDLOG" 2>&1

log_cmd python3_generate_bc_objs
python3 - <<'PY' >> "$BCLOG" 2>&1
from pathlib import Path
import subprocess

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g')
work = base / 'work' / 'masscan-src'
art = base / 'artifacts'
bcdir = art / 'bc_objs'
bcdir.mkdir(parents=True, exist_ok=True)

sources = sorted((work / 'src').glob('*.c'))
if not sources:
    raise SystemExit('No source files found in src/*.c')

bc_paths = []
for src in sources:
    out = bcdir / (src.stem + '.bc')
    cmd = ['clang-14', '-O2', '-g', '-Wall', '-emit-llvm', '-c', str(src), '-o', str(out)]
    # keep GIT define semantics used by Makefile for main-conf.c
    if src.name == 'main-conf.c':
        cmd.append('-DGIT="unknown"')
    subprocess.run(cmd, check=True)
    bc_paths.append(out)

(art / 'bc_files.list').write_text(''.join(str(p) + '\n' for p in bc_paths), encoding='utf-8')
print('src_count', len(sources))
print('bc_count', len(bc_paths))
PY

log_cmd llvm-link-14_masscan_bc
llvm-link-14 $(python3 - <<'PY'
from pathlib import Path
lst = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/bc_files.list')
for line in lst.read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/masscan_O2_g.bc" >> "$BCLOG" 2>&1

log_cmd llvm-dis-14_masscan_bc
llvm-dis-14 "$ART/masscan_O2_g.bc" -o "$ART/masscan_O2_g.ll" >> "$BCLOG" 2>&1

log_cmd llvm-nm-14_main_check
llvm-nm-14 "$ART/masscan_O2_g.bc" > "$LOG/llvm_nm.log" 2>&1

MAIN_STATUS="$(python3 - <<'PY'
from pathlib import Path
txt = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/log/llvm_nm.log').read_text(encoding='utf-8', errors='replace')
print('present' if any(line.rstrip().endswith(' T main') for line in txt.splitlines()) else 'missing')
PY
)"

{
  echo "binary=$ART/masscan_O2_g"
  echo "bc=$ART/masscan_O2_g.bc"
  echo "ll=$ART/masscan_O2_g.ll"
  echo "bc_list=$ART/bc_files.list"
  echo "main_symbol=$MAIN_STATUS"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$BUILDLOG"
