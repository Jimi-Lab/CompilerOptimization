#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="/work/PaperExperiment/CompilerOptimization/Target"
RESULT_ROOT="/work/PaperExperiment/CompilerOptimization/Result"
LLVM_LINK="/usr/lib/llvm-16/bin/llvm-link"
LLVM_DIS="/usr/lib/llvm-16/bin/llvm-dis"
IFDS_TIMEOUT_SEC="${IFDS_TIMEOUT_SEC:-420}"
PROFILE_DIR_NAME="${PROFILE_DIR_NAME:-phasar_O2_RelWithDebInfo}"
LOG_DIR_NAME="${LOG_DIR_NAME:-logs}"
SUMMARY_FILE_NAME="${SUMMARY_FILE_NAME:-phasar_o2_linecheck_summary.csv}"
O2G_ONLY="${O2G_ONLY:-0}"

PROJECTS=(
  Curl
  Tengine
  WasmEdge
  duckdb
  flatbuffers
  flite
  grpc
  lepton
  leveldb
  libco
  libsndfile
  masscan
  opencv
  rapidjson
  redis
  rethinkdb
  zfp
  zopfli
)

map_project_key() {
  local name="$1"
  if [ "$name" = "Curl" ]; then
    echo "curl"
  else
    echo "$name" | tr '[:upper:]' '[:lower:]'
  fi
}

map_source_root() {
  local name="$1"
  case "$name" in
    Curl)
      echo "$TARGET_ROOT/Curl/7.68.0/curl-curl-7_68_0"
      ;;
    *)
      echo "$TARGET_ROOT/$name"
      ;;
  esac
}

run_and_log() {
  local cmd="$1"
  local cmdlog="$2"
  local outlog="$3"
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$cmd" >> "$cmdlog"
  bash -lc "$cmd" >> "$outlog" 2>&1
}

run_and_log_allow_fail() {
  local cmd="$1"
  local cmdlog="$2"
  local outlog="$3"
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$cmd" >> "$cmdlog"
  set +e
  bash -lc "$cmd" >> "$outlog" 2>&1
  local ec=$?
  set -e
  return $ec
}

generate_bc_from_compile_db() {
  local project="$1"
  local o2dir="$2"
  local mode="$3"
  python3 - <<'PYEOF'
import hashlib
import json
import os
import shlex
import subprocess
from pathlib import Path

project = os.environ['PROJECT']
o2dir = Path(os.environ['O2DIR'])
mode = os.environ['MODE']
ccdb = o2dir / 'build' / 'compile_commands.json'
objdir = o2dir / 'artifacts' / 'bc_objs'
list_path = o2dir / 'artifacts' / 'bc_files.list'

entries = json.load(ccdb.open())
outs = []
seen = set()

build_dir = o2dir / 'build'
link_txts = list(build_dir.glob('**/link.txt'))
selected_obj_names = set()
best = []
for lt in link_txts:
    txt = lt.read_text(encoding='utf-8', errors='ignore')
    toks = shlex.split(txt)
    objs = [Path(t).name for t in toks if t.endswith('.o')]
    if len(objs) > len(best):
        best = objs
if best:
    selected_obj_names = set(best)

exclude_marks = ('/test/', '/tests/', '/benchmark/', '/bench/', '/examples/', '/example/', '/docs/', '/fuzz/')

for i, e in enumerate(entries):
    cmd = shlex.split(e['command'])
    directory = e['directory']
    src = e['file']
    out_obj = None
    if e.get('output'):
        out_obj = Path(e['output']).name
    else:
        for j, t in enumerate(cmd):
            if t == '-o' and j + 1 < len(cmd):
                out_obj = Path(cmd[j + 1]).name
                break
            if t.startswith('-o') and t != '-o':
                out_obj = Path(t[2:]).name
                break

    if selected_obj_names and out_obj and out_obj not in selected_obj_names:
        continue

    src_abs = str((Path(directory) / src).resolve()) if not Path(src).is_absolute() else str(Path(src).resolve())
    lsrc = src_abs.lower()
    if any(m in lsrc for m in exclude_marks):
        continue
    if src_abs in seen:
        continue
    seen.add(src_abs)

    out = objdir / (hashlib.sha1((str(i) + '|' + src_abs).encode()).hexdigest()[:16] + '.bc')

    new = []
    skip = False
    for t in cmd:
      if skip:
        skip = False
        continue
      if t == '-o':
        skip = True
        continue
      if t.startswith('-o') and t != '-o':
        continue
      if t in ('-MD', '-MMD'):
        continue
      if t in ('-MF', '-MT', '-MQ'):
        skip = True
        continue
      new.append(t)
    if '-c' not in new:
      new.append('-c')
    new.extend(['-emit-llvm', '-o', str(out)])
    try:
      subprocess.run(new, cwd=directory, check=True)
      outs.append(str(out))
    except subprocess.CalledProcessError:
      pass

with list_path.open('w') as f:
  for p in outs:
    f.write(p + '\n')

print('mode', mode)
print('compile_db_entries', len(entries))
print('selected_link_objs', len(selected_obj_names))
print('selected_sources', len(seen))
print('generated_bc', len(outs))
PYEOF
}

generate_bc_from_make_dryrun() {
  local o2dir="$1"
  local srcdir="$2"
  python3 - <<'PYEOF'
import hashlib
import os
import re
import shlex
import subprocess
from pathlib import Path

o2dir = Path(os.environ['O2DIR'])
srcdir = Path(os.environ['SRCDIR'])
dryrun = o2dir / 'logs' / 'make_dryrun.log'
objdir = o2dir / 'artifacts' / 'bc_objs'
list_path = o2dir / 'artifacts' / 'bc_files.list'

text = dryrun.read_text(encoding='utf-8', errors='ignore').splitlines()
clang_frag_re = re.compile(r'(?:^|;)\s*(?:/usr/bin/)?clang(?:\+\+)?-?16\b[^;]*\s-c\s[^;]*')
link_frag_re = re.compile(r'(?:^|;)\s*(?:/usr/bin/)?clang(?:\+\+)?-?16\b[^;]*\s-o\s+[^;]+')

link_objs = []
for line in text:
  for m in link_frag_re.finditer(line):
    frag = m.group(0).lstrip(';').strip()
    try:
      toks = shlex.split(frag)
    except Exception:
      continue
    objs = [Path(t).name for t in toks if t.endswith('.o')]
    if objs:
      link_objs.append(objs)

selected_obj_set = set(max(link_objs, key=len)) if link_objs else None

exclude_marks = ('/test/', '/tests/', '/benchmark/', '/bench/', '/examples/', '/example/', '/docs/', '/fuzz/')
seen_src = set()
outs = []

for i, line in enumerate(text):
  for m in clang_frag_re.finditer(line):
    frag = m.group(0).lstrip(';').strip()
    try:
      toks = shlex.split(frag)
    except Exception:
      continue

    out_obj = None
    for j, t in enumerate(toks):
      if t == '-o' and j + 1 < len(toks):
        out_obj = Path(toks[j + 1]).name
        break
      if t.startswith('-o') and t != '-o':
        out_obj = Path(t[2:]).name
        break

    if selected_obj_set and out_obj and out_obj not in selected_obj_set:
      continue

    src = None
    for t in reversed(toks):
      if t.endswith(('.c', '.cc', '.cpp', '.cxx')):
        src = t
        break
    if not src:
      continue

    src_abs = str((srcdir / src).resolve()) if not Path(src).is_absolute() else str(Path(src).resolve())
    lsrc = src_abs.lower()
    if any(m in lsrc for m in exclude_marks):
      continue
    if src_abs in seen_src:
      continue
    seen_src.add(src_abs)

    out_bc = objdir / (hashlib.sha1((str(i) + '|' + src_abs).encode()).hexdigest()[:16] + '.bc')

    new = []
    skip = False
    for t in toks:
      if skip:
        skip = False
        continue
      if t == '-o':
        skip = True
        continue
      if t.startswith('-o') and t != '-o':
        continue
      if t in ('-MMD', '-MD'):
        continue
      if t in ('-MF', '-MT', '-MQ'):
        skip = True
        continue
      new.append(t)

    if '-c' not in new:
      new.append('-c')
    new.extend(['-emit-llvm', '-o', str(out_bc)])
    try:
      subprocess.run(new, cwd=srcdir, check=True)
      outs.append(str(out_bc))
    except subprocess.CalledProcessError:
      pass

with list_path.open('w') as f:
  for p in outs:
    f.write(p + '\n')

print('dryrun_lines', len(text))
print('selected_obj_count', len(selected_obj_set) if selected_obj_set else 0)
print('selected_sources', len(seen_src))
print('generated_bc', len(outs))
PYEOF
}

link_whole_program_bc() {
  local o2dir="$1"
  local bcname="$2"
  python3 - <<'PYEOF'
import os
import subprocess
from pathlib import Path

o2dir = Path(os.environ['O2DIR'])
bcname = os.environ['BCNAME']
art = o2dir / 'artifacts'
files = [x.strip() for x in (art / 'bc_files.list').read_text().splitlines() if x.strip()]
if not files:
  raise SystemExit('no bc files generated')

bc_out = art / f'{bcname}.bc'
ll_out = art / f'{bcname}.ll'

subprocess.run(['/usr/lib/llvm-16/bin/llvm-link', *files, '-o', str(bc_out)], check=True)
subprocess.run(['/usr/lib/llvm-16/bin/llvm-dis', str(bc_out), '-o', str(ll_out)], check=True)
print(bc_out)
print(ll_out)
PYEOF
}

verify_ir() {
  local o2dir="$1"
  local bcname="$2"
  python3 - <<'PYEOF'
import os
from pathlib import Path

o2dir = Path(os.environ['O2DIR'])
bcname = os.environ['BCNAME']
ll = o2dir / 'artifacts' / f'{bcname}.ll'
txt = ll.read_text(encoding='utf-8', errors='ignore')
print('phi:', txt.count('= phi '))
print('alloca:', txt.count('alloca '))
print('debug:', txt.count('!DISubprogram') + txt.count('!DILocation') + txt.count('!DIFile'))
print('ll:', ll)
PYEOF
}

linecheck_report() {
  local report="$1"
  local source_root="$2"
  local out_csv="$3"
  local out_json="$4"
  python3 - <<'PYEOF'
import csv
import json
import os
import re
from pathlib import Path

report = Path(os.environ['REPORT'])
source_root = str(Path(os.environ['SOURCE_ROOT']).resolve()) + '/'
out_csv = Path(os.environ['OUT_CSV'])
out_json = Path(os.environ['OUT_JSON'])

text = report.read_text(encoding='utf-8', errors='ignore').splitlines()
use_header = re.compile(r'^-+\s+(\d+)\. Use')
line_inline = re.compile(r'\bLine\s*:\s*(\d+)')

rows = []
cur = None
for ln in text:
  m = use_header.match(ln)
  if m:
    if cur:
      rows.append(cur)
    cur = {'case': int(m.group(1)), 'file': None, 'line': None, 'source': ''}
    continue
  if cur is None:
    continue
  if ln.startswith('File'):
    cur['file'] = ln.split(':', 1)[1].strip()
  elif ln.startswith('Line'):
    try:
      cur['line'] = int(ln.split(':', 1)[1].strip())
    except Exception:
      cur['line'] = None
  elif 'Line' in ln and ':' in ln:
    m2 = line_inline.search(ln)
    if m2:
      try:
        cur['line'] = int(m2.group(1))
      except Exception:
        pass
  elif ln.startswith('Source code'):
    cur['source'] = ln.split(':', 1)[1].strip()
if cur:
  rows.append(cur)

out = []
for r in rows:
  f = r['file'] or ''
  if not f.startswith(source_root):
    continue
  rel = f[len(source_root):]
  hp = Path(source_root) / rel
  status = 'unknown'
  reason = ''
  actual = ''
  line = r['line'] or 0
  if not hp.exists():
    status = 'missing_file'
    reason = 'file not found'
  else:
    src_lines = hp.read_text(encoding='utf-8', errors='ignore').splitlines()
    if line < 1 or line > len(src_lines):
      status = 'line_oob'
      reason = f'line {line} out of range (1..{len(src_lines)})'
    else:
      actual = src_lines[line-1]
      if actual.strip() == (r['source'] or '').strip():
        status = 'match'
      else:
        status = 'mismatch'
        reason = 'source text mismatch'
  out.append({
    'case': r['case'],
    'file': rel,
    'line': line,
    'status': status,
    'report_source': r['source'],
    'actual_source': actual,
    'reason': reason,
  })

out_json.write_text(json.dumps(out, indent=2), encoding='utf-8')
with out_csv.open('w', newline='', encoding='utf-8') as f:
  w = csv.DictWriter(f, fieldnames=['case','file','line','status','report_source','actual_source','reason'])
  w.writeheader()
  w.writerows(out)

print('linecheck_rows', len(out))
PYEOF
}

project_summary_update() {
  local project_key="$1"
  local o2dir="$2"
  PROJECT_KEY="$project_key" O2DIR="$o2dir" SUMMARY_FILE_NAME="$SUMMARY_FILE_NAME" python3 - <<'PYEOF'
import csv
from pathlib import Path
import os

project_key = os.environ['PROJECT_KEY']
o2dir = Path(os.environ['O2DIR'])
csv_path = o2dir / 'runs' / 'ifds-uninit' / 'target_linecheck.csv'
summary_path = Path('/work/PaperExperiment/CompilerOptimization/Result') / os.environ['SUMMARY_FILE_NAME']

total = match = mismatch = line_oob = 0
if csv_path.exists():
  with csv_path.open(newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
      total += 1
      st = row.get('status', '')
      if st == 'match':
        match += 1
      elif st == 'mismatch':
        mismatch += 1
      elif st == 'line_oob':
        line_oob += 1

rows = []
if summary_path.exists():
  with summary_path.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

rows = [r for r in rows if r.get('project') != project_key]
oob_rate = (line_oob / total * 100.0) if total else 0.0
rows.append({
  'project': project_key,
  'total_uses': str(total),
  'match': str(match),
  'mismatch': str(mismatch),
  'line_oob': str(line_oob),
  'oob_rate': f'{oob_rate:.2f}'
})

rows.sort(key=lambda x: x['project'])
with summary_path.open('w', newline='', encoding='utf-8') as f:
  w = csv.DictWriter(f, fieldnames=['project','total_uses','match','mismatch','line_oob','oob_rate'])
  w.writeheader()
  w.writerows(rows)
print(summary_path)
PYEOF
}

run_project() {
  local project="$1"
  local project_key="$2"
  local source_root="$3"
  local o2dir="$RESULT_ROOT/$project_key/phasar/$PROFILE_DIR_NAME"
  local build="$o2dir/build"
  local artifacts="$o2dir/artifacts"
  local logs="$o2dir/$LOG_DIR_NAME"
  local runs="$o2dir/runs"
  local status_dir="$o2dir/status"
  local success_marker="$status_dir/success.marker"
  local cmdlog="$logs/commands.log"
  local projlog="$logs/project.log"
  local bcname="${project_key}_O2_g"

  mkdir -p "$build" "$artifacts/bc_objs" "$runs/ifds-uninit" "$logs" "$status_dir" "$o2dir/work"
  : > "$cmdlog"
  : > "$projlog"

  ensure_existing_linecheck() {
    local latest
    if [ -f "$runs/ifds-uninit/target_linecheck.csv" ]; then
      PROJECT_KEY="$project_key" O2DIR="$o2dir" project_summary_update "$project_key" "$o2dir" >> "$projlog" 2>&1 || true
      return
    fi
    latest=$(RUNROOT="$runs/ifds-uninit" python3 - <<'PYEOF'
from pathlib import Path
import os
runroot = Path(os.environ['RUNROOT'])
subs=[p for p in runroot.iterdir() if p.is_dir()]
subs.sort(key=lambda p:p.stat().st_mtime, reverse=True)
print(subs[0] if subs else '')
PYEOF
)
    if [ -n "$latest" ] && [ -f "$latest/psr-report.txt" ]; then
      REPORT="$latest/psr-report.txt" SOURCE_ROOT="$source_root" OUT_CSV="$runs/ifds-uninit/target_linecheck.csv" OUT_JSON="$runs/ifds-uninit/target_linecheck.json" \
        linecheck_report "$latest/psr-report.txt" "$source_root" "$runs/ifds-uninit/target_linecheck.csv" "$runs/ifds-uninit/target_linecheck.json" >> "$projlog" 2>&1 || true
    fi
    PROJECT_KEY="$project_key" O2DIR="$o2dir" project_summary_update "$project_key" "$o2dir" >> "$projlog" 2>&1 || true
  }

  if [ -f "$success_marker" ]; then
    echo "[SKIP] $project_key already marked success"
    ensure_existing_linecheck
    return 0
  fi

  # legacy success detection (for already completed runs)
  if [ -f "$logs/summary.csv" ] && grep -q '^ifds-uninit,0,ok' "$logs/summary.csv"; then
    echo "legacy summary indicates success" > "$success_marker"
    echo "[SKIP] $project_key legacy success detected"
    ensure_existing_linecheck
    return 0
  fi

  echo "project=$project" >> "$projlog"
  echo "project_key=$project_key" >> "$projlog"
  echo "source_root=$source_root" >> "$projlog"
  echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$projlog"

  local mode=""
  if [ -f "$source_root/CMakeLists.txt" ]; then
    mode="cmake"
  elif [ -f "$source_root/Makefile" ] || [ "$project" = "redis" ]; then
    mode="make"
  else
    mode="unsupported"
  fi
  echo "build_mode=$mode" >> "$projlog"

  if [ "$mode" = "unsupported" ]; then
    echo "unsupported build system" > "$status_dir/failed.marker"
    return 0
  fi

  if [ "$mode" = "cmake" ]; then
    if [ "$O2G_ONLY" = "1" ]; then
      run_and_log "cmake -S '$source_root' -B '$build' -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=clang-16 -DCMAKE_CXX_COMPILER=clang++-16 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_C_FLAGS='-O2 -g' -DCMAKE_CXX_FLAGS='-O2 -g' -DBUILD_TESTING=OFF -DBUILD_TESTS=OFF" "$cmdlog" "$projlog" || {
        echo "cmake configure failed" > "$status_dir/failed.marker"
        return 0
      }
    else
      run_and_log "cmake -S '$source_root' -B '$build' -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_C_COMPILER=clang-16 -DCMAKE_CXX_COMPILER=clang++-16 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_C_FLAGS_RELWITHDEBINFO='-O2 -g -DNDEBUG' -DCMAKE_CXX_FLAGS_RELWITHDEBINFO='-O2 -g -DNDEBUG' -DBUILD_TESTING=OFF -DBUILD_TESTS=OFF" "$cmdlog" "$projlog" || {
        echo "cmake configure failed" > "$status_dir/failed.marker"
        return 0
      }
    fi

    run_and_log "cmake --build '$build' -j$(nproc)" "$cmdlog" "$projlog" || {
      echo "cmake build failed" > "$status_dir/failed.marker"
      return 0
    }

    run_and_log "cp -f '$build/compile_commands.json' '$artifacts/compile_commands.json'" "$cmdlog" "$projlog" || true

    PROJECT="$project_key" O2DIR="$o2dir" MODE="cmake" generate_bc_from_compile_db "$project_key" "$o2dir" "cmake" >> "$projlog" 2>&1 || {
      echo "bc generation from compile_commands failed" > "$status_dir/failed.marker"
      return 0
    }
  else
    local workcopy="$o2dir/work/${project_key}"
    rm -rf "$workcopy"
    run_and_log "cp -a '$source_root' '$workcopy'" "$cmdlog" "$projlog" || {
      echo "work copy failed" > "$status_dir/failed.marker"
      return 0
    }
    run_and_log "chmod -R u+w '$workcopy'" "$cmdlog" "$projlog" || true

    local mkroot="$workcopy"
    if [ "$project" = "redis" ]; then
      mkroot="$workcopy/src"
      run_and_log_allow_fail "make -C '$workcopy' distclean" "$cmdlog" "$projlog" || true
      run_and_log_allow_fail "make -C '$workcopy/deps' -j$(nproc) CC=clang-16 hiredis linenoise lua hdr_histogram fpconv fast_float xxhash" "$cmdlog" "$projlog" || true
      run_and_log_allow_fail "bash -lc 'cd \"$mkroot\" && ./mkreleasehdr.sh'" "$cmdlog" "$projlog" || true
      if [ "$O2G_ONLY" = "1" ]; then
        run_and_log "make -C '$mkroot' -B -n CC=clang-16 MALLOC=libc BUILD_TLS=no OPTIMIZATION='-O2' REDIS_CFLAGS='-g -DNULL=0' > '$logs/make_dryrun.log'" "$cmdlog" "$projlog" || {
          echo "make dry-run failed" > "$status_dir/failed.marker"
          return 0
        }
      else
        run_and_log "make -C '$mkroot' -B -n CC=clang-16 MALLOC=libc BUILD_TLS=no OPTIMIZATION='-O2' REDIS_CFLAGS='-g -DNDEBUG -DNULL=0' > '$logs/make_dryrun.log'" "$cmdlog" "$projlog" || {
          echo "make dry-run failed" > "$status_dir/failed.marker"
          return 0
        }
      fi
    else
      run_and_log_allow_fail "make -C '$mkroot' clean" "$cmdlog" "$projlog" || true
      run_and_log_allow_fail "make -C '$mkroot' -j$(nproc) CC=clang-16 CXX=clang++-16 CFLAGS='-O2 -g' CXXFLAGS='-O2 -g' OPTIMIZATION='-O2'" "$cmdlog" "$projlog" || true
      run_and_log "make -C '$mkroot' -B -n CC=clang-16 CXX=clang++-16 CFLAGS='-O2 -g' CXXFLAGS='-O2 -g' OPTIMIZATION='-O2' > '$logs/make_dryrun.log'" "$cmdlog" "$projlog" || {
        echo "make dry-run failed" > "$status_dir/failed.marker"
        return 0
      }
    fi

    O2DIR="$o2dir" SRCDIR="$mkroot" generate_bc_from_make_dryrun "$o2dir" "$mkroot" >> "$projlog" 2>&1 || {
      echo "bc generation from make dry-run failed" > "$status_dir/failed.marker"
      return 0
    }
  fi

  O2DIR="$o2dir" BCNAME="$bcname" link_whole_program_bc "$o2dir" "$bcname" >> "$logs/llvm_link.log" 2>&1 || {
    echo "llvm-link failed" > "$status_dir/failed.marker"
    return 0
  }

  O2DIR="$o2dir" BCNAME="$bcname" verify_ir "$o2dir" "$bcname" > "$logs/verify.log" 2>&1 || true

  local summary_csv="$logs/summary.csv"
  echo "analysis,exit_code,status,elapsed_sec" > "$summary_csv"
  local start_ts end_ts elapsed ec st
  start_ts=$(date +%s)

  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    "timeout $IFDS_TIMEOUT_SEC phasar-cli -m '$artifacts/$bcname.bc' -D ifds-uninit -P basic -C otf -E __ALL__ --emit-raw-results --emit-text-report --emit-stats --emit-statistics-as-json --out '$runs/ifds-uninit'" >> "$cmdlog"

  set +e
  timeout "$IFDS_TIMEOUT_SEC" phasar-cli \
    -m "$artifacts/$bcname.bc" \
    -D ifds-uninit \
    -P basic \
    -C otf \
    -E __ALL__ \
    --emit-raw-results \
    --emit-text-report \
    --emit-stats \
    --emit-statistics-as-json \
    --out "$runs/ifds-uninit" > "$logs/ifds-uninit.stdout.log" 2> "$logs/ifds-uninit.stderr.log"
  ec=$?
  set -e

  end_ts=$(date +%s)
  elapsed=$((end_ts-start_ts))
  if [ "$ec" -eq 0 ]; then
    st="ok"
  elif [ "$ec" -eq 124 ]; then
    st="timeout"
  elif [ "$ec" -eq 137 ]; then
    st="oom_or_killed"
  else
    st="error"
  fi
  echo "ifds-uninit,$ec,$st,$elapsed" >> "$summary_csv"

  # locate latest run dir
  local latest_run
  latest_run=$(RUNROOT="$runs/ifds-uninit" python3 - <<'PYEOF'
from pathlib import Path
import os
runroot = Path(os.environ['RUNROOT'])
subs=[p for p in runroot.iterdir() if p.is_dir()]
subs.sort(key=lambda p:p.stat().st_mtime, reverse=True)
print(subs[0] if subs else '')
PYEOF
)
  echo "latest_run=$latest_run" >> "$projlog"

  if [ -n "$latest_run" ] && [ -f "$latest_run/psr-report.txt" ]; then
    REPORT="$latest_run/psr-report.txt" SOURCE_ROOT="$source_root" OUT_CSV="$runs/ifds-uninit/target_linecheck.csv" OUT_JSON="$runs/ifds-uninit/target_linecheck.json" \
      linecheck_report "$latest_run/psr-report.txt" "$source_root" "$runs/ifds-uninit/target_linecheck.csv" "$runs/ifds-uninit/target_linecheck.json" >> "$projlog" 2>&1 || true
  fi

  if [ "$ec" -eq 0 ]; then
    echo "success_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" > "$success_marker"
    echo "run_dir=$latest_run" >> "$success_marker"
    echo "exit_code=$ec" >> "$success_marker"
  else
    echo "failed_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" > "$status_dir/failed.marker"
    echo "exit_code=$ec" >> "$status_dir/failed.marker"
    echo "status=$st" >> "$status_dir/failed.marker"
  fi

  PROJECT_KEY="$project_key" O2DIR="$o2dir" project_summary_update "$project_key" "$o2dir" >> "$projlog" 2>&1 || true

  # per-project readme
  PROJECT="$project" PROJECT_KEY="$project_key" SOURCE_ROOT="$source_root" O2DIR="$o2dir" LOG_DIR_NAME="$LOG_DIR_NAME" BCNAME="$bcname" PROFILE_DIR_NAME="$PROFILE_DIR_NAME" python3 - <<'PYEOF'
import csv
from pathlib import Path
import os

project = os.environ['PROJECT']
project_key = os.environ['PROJECT_KEY']
source_root = os.environ['SOURCE_ROOT']
o2dir = Path(os.environ['O2DIR'])
logs = o2dir / 'logs'
runs = o2dir / 'runs' / 'ifds-uninit'
log_dir_name = os.environ['LOG_DIR_NAME']
logs = o2dir / log_dir_name
bcname = os.environ['BCNAME']
profile_dir = os.environ['PROFILE_DIR_NAME']

rows = []
if (logs / 'summary.csv').exists():
  rows = list(csv.DictReader((logs / 'summary.csv').open()))

lines = []
lines.append(f'# {project_key} {profile_dir} - PhASAR ifds-uninit')
lines.append('')
lines.append('## Source and output')
lines.append(f'- Target project dir: `{source_root}`')
lines.append(f'- Output dir: `{o2dir}`')
lines.append('')
lines.append('## Commands and logs')
lines.append(f'- All commands: `{logs / "commands.log"}`')
lines.append(f'- Project process log: `{logs / "project.log"}`')
lines.append(f'- Build stdout/stderr: `{logs / "project.log"}`')
lines.append(f'- IFDS logs: `{logs / "ifds-uninit.stdout.log"}`, `{logs / "ifds-uninit.stderr.log"}`')
lines.append('')
lines.append('## Artifacts')
lines.append(f'- Whole-program bc: `{o2dir / "artifacts" / (bcname + ".bc")}`')
lines.append(f'- Whole-program ll: `{o2dir / "artifacts" / (bcname + ".ll")}`')
lines.append(f'- ifds-uninit runs: `{runs}`')
lines.append(f'- Linecheck CSV/JSON: `{runs / "target_linecheck.csv"}`, `{runs / "target_linecheck.json"}`')
lines.append('')
lines.append('## ifds-uninit status')
if rows:
  r = rows[0]
  lines.append(f"- exit_code: {r['exit_code']}")
  lines.append(f"- status: {r['status']}")
  lines.append(f"- elapsed_sec: {r['elapsed_sec']}")
else:
  lines.append('- no summary')

(o2dir / 'readme.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
PYEOF
}

echo "Starting all-target scan (profile=$PROFILE_DIR_NAME) ifds-uninit"
echo "timeout_sec=$IFDS_TIMEOUT_SEC"

for p in "${PROJECTS[@]}"; do
  key="$(map_project_key "$p")"
  src="$(map_source_root "$p")"
  echo "==== Project: $p ($key) ===="
  if [ ! -d "$src" ]; then
    echo "missing source: $src"
    mkdir -p "$RESULT_ROOT/$key/phasar/$PROFILE_DIR_NAME/status"
    echo "missing_source" > "$RESULT_ROOT/$key/phasar/$PROFILE_DIR_NAME/status/failed.marker"
    continue
  fi
  run_project "$p" "$key" "$src"
done

echo "All projects processed. Cross-project summary: $RESULT_ROOT/$SUMMARY_FILE_NAME"
