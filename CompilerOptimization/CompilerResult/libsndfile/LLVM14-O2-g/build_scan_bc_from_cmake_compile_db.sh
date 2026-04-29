#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g"
BUILD="$BASE/CMakeBuild"
ART="$BASE/artifacts"
LOG="$BASE/log"
STATUS="$BASE/status"

mkdir -p "$ART" "$LOG" "$STATUS"

CMDLOG="$LOG/bc_commands.log"
BCLOG="$LOG/bc_build.log"
LNKLOG="$LOG/bc_link.log"

: > "$CMDLOG"
: > "$BCLOG"
: > "$LNKLOG"

log_cmd() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$CMDLOG"
}

if [[ ! -f "$BUILD/compile_commands.json" ]]; then
  echo "missing compile_commands.json: $BUILD/compile_commands.json" >&2
  exit 1
fi

log_cmd "python3 recompile selected targets to bitcode"
python3 - <<'PY' >> "$BCLOG" 2>&1
from pathlib import Path
import json
import shlex
import subprocess

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g')
build = base / 'CMakeBuild'
art = base / 'artifacts'
bcdir = art / 'bc_objs'
bcdir.mkdir(parents=True, exist_ok=True)

ccdb = json.loads((build / 'compile_commands.json').read_text(encoding='utf-8'))

sndfile_entries = []
tool_entries = []
for e in ccdb:
    cmd = e.get('command', '')
    if 'CMakeFiles/sndfile.dir/' in cmd:
        sndfile_entries.append(e)
    elif 'CMakeFiles/sndfile-convert.dir/' in cmd:
        tool_entries.append(e)

if not sndfile_entries:
    raise SystemExit('No compile_commands entries for CMakeFiles/sndfile.dir')
if not tool_entries:
    raise SystemExit('No compile_commands entries for CMakeFiles/sndfile-convert.dir')

def regen_bc(entries, prefix):
    out_list = []
    for idx, entry in enumerate(entries, start=1):
        if 'arguments' in entry:
            args = list(entry['arguments'])
        else:
            args = shlex.split(entry['command'])
        src = entry['file']
        out_bc = bcdir / f'{prefix}_{idx:04d}.bc'

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
        out_list.append(out_bc)
    return out_list

sndfile_bcs = regen_bc(sndfile_entries, 'sndfile')
tool_bcs = regen_bc(tool_entries, 'sndfile_convert')

(art / 'bc_files_sndfile.list').write_text(''.join(str(p) + '\n' for p in sndfile_bcs), encoding='utf-8')
(art / 'bc_files_sndfile_convert.list').write_text(''.join(str(p) + '\n' for p in tool_bcs), encoding='utf-8')
(art / 'bc_files_scan_merged.list').write_text(''.join(str(p) + '\n' for p in (sndfile_bcs + tool_bcs)), encoding='utf-8')

print('sndfile_entries', len(sndfile_entries))
print('sndfile_convert_entries', len(tool_entries))
print('generated_bc_total', len(sndfile_bcs) + len(tool_bcs))
PY

log_cmd "llvm-link-14 library bitcode"
llvm-link-14 $(python3 - <<'PY'
from pathlib import Path
for line in Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/bc_files_sndfile.list').read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/libsndfile_O2_g.bc" >> "$LNKLOG" 2>&1

log_cmd "llvm-dis-14 library bitcode"
llvm-dis-14 "$ART/libsndfile_O2_g.bc" -o "$ART/libsndfile_O2_g.ll" >> "$LNKLOG" 2>&1

log_cmd "llvm-link-14 merged scan bitcode"
llvm-link-14 $(python3 - <<'PY'
from pathlib import Path
for line in Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/bc_files_scan_merged.list').read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/libsndfile_sndfile_convert_O2_g.bc" >> "$LNKLOG" 2>&1

log_cmd "llvm-dis-14 merged scan bitcode"
llvm-dis-14 "$ART/libsndfile_sndfile_convert_O2_g.bc" -o "$ART/libsndfile_sndfile_convert_O2_g.ll" >> "$LNKLOG" 2>&1

log_cmd "llvm-nm-14 main symbol check"
llvm-nm-14 "$ART/libsndfile_sndfile_convert_O2_g.bc" > "$LOG/llvm_nm_scan_merged.log" 2>&1

MAIN_STATUS="$(python3 - <<'PY'
from pathlib import Path
txt = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/log/llvm_nm_scan_merged.log').read_text(encoding='utf-8', errors='replace')
print('present' if any(line.rstrip().endswith(' T main') for line in txt.splitlines()) else 'missing')
PY
)"

{
  echo "library_bc=$ART/libsndfile_O2_g.bc"
  echo "scan_merged_bc=$ART/libsndfile_sndfile_convert_O2_g.bc"
  echo "scan_merged_ll=$ART/libsndfile_sndfile_convert_O2_g.ll"
  echo "main_symbol=$MAIN_STATUS"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/bc_success.marker"

rm -f "$STATUS/bc_failed.marker"
