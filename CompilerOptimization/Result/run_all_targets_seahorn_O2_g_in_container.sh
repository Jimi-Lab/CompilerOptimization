#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="/work/PaperExperiment/CompilerOptimization/Target"
RESULT_ROOT="/work/PaperExperiment/CompilerOptimization/Result"
PROFILE_DIR_NAME="seahorn-O2-g"

LLVM_LINK="/usr/bin/llvm-link-14"
LLVM_DIS="/usr/bin/llvm-dis-14"

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
  python3 - <<'PYEOF'
import hashlib
import json
import os
import shlex
import subprocess
from pathlib import Path

o2dir = Path(os.environ['O2DIR'])
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

with list_path.open('w', encoding='utf-8') as f:
    for p in outs:
        f.write(p + '\n')

print('compile_db_entries', len(entries))
print('selected_link_objs', len(selected_obj_names))
print('selected_sources', len(seen))
print('generated_bc', len(outs))
PYEOF
}

generate_bc_from_make_dryrun() {
  python3 - <<'PYEOF'
import hashlib
import os
import re
import shlex
import subprocess
from pathlib import Path

o2dir = Path(os.environ['O2DIR'])
srcdir = Path(os.environ['SRCDIR'])
dryrun = o2dir / 'log' / 'make_dryrun.log'
objdir = o2dir / 'artifacts' / 'bc_objs'
list_path = o2dir / 'artifacts' / 'bc_files.list'

text = dryrun.read_text(encoding='utf-8', errors='ignore').splitlines()
clang_frag_re = re.compile(r'(?:^|;)\s*(?:/usr/bin/)?clang(?:\+\+)?-?14\b[^;]*\s-c\s[^;]*')
link_frag_re = re.compile(r'(?:^|;)\s*(?:/usr/bin/)?clang(?:\+\+)?-?14\b[^;]*\s-o\s+[^;]+')

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

with list_path.open('w', encoding='utf-8') as f:
    for p in outs:
        f.write(p + '\n')

print('dryrun_lines', len(text))
print('selected_obj_count', len(selected_obj_set) if selected_obj_set else 0)
print('selected_sources', len(seen_src))
print('generated_bc', len(outs))
PYEOF
}

link_whole_program_bc() {
  python3 - <<'PYEOF'
import os
import subprocess
from pathlib import Path

o2dir = Path(os.environ['O2DIR'])
bcname = os.environ['BCNAME']
llvm_link = os.environ['LLVM_LINK']
llvm_dis = os.environ['LLVM_DIS']

art = o2dir / 'artifacts'
files = [x.strip() for x in (art / 'bc_files.list').read_text(encoding='utf-8', errors='ignore').splitlines() if x.strip()]
if not files:
    raise SystemExit('no bc files generated')

bc_out = art / f'{bcname}.bc'
ll_out = art / f'{bcname}.ll'

subprocess.run([llvm_link, *files, '-o', str(bc_out)], check=True)
subprocess.run([llvm_dis, str(bc_out), '-o', str(ll_out)], check=True)
print('linked_inputs', len(files))
print('bc_out', bc_out)
print('ll_out', ll_out)
PYEOF
}

verify_ir() {
  python3 - <<'PYEOF'
import os
from pathlib import Path

o2dir = Path(os.environ['O2DIR'])
bcname = os.environ['BCNAME']
ll = o2dir / 'artifacts' / f'{bcname}.ll'
txt = ll.read_text(encoding='utf-8', errors='ignore')
print('phi', txt.count('= phi '))
print('alloca', txt.count('alloca '))
print('debug_meta', txt.count('!DISubprogram') + txt.count('!DILocation') + txt.count('!DIFile'))
PYEOF
}

update_compile_summary() {
  local project_key="$1"
  local o2dir="$2"
  PROJECT_KEY="$project_key" O2DIR="$o2dir" python3 - <<'PYEOF'
import csv
import os
from pathlib import Path

project_key = os.environ['PROJECT_KEY']
o2dir = Path(os.environ['O2DIR'])
summary = Path('/work/PaperExperiment/CompilerOptimization/Result/seahorn_O2_g_compile_status.csv')

status = 'none'
reason = ''
if (o2dir / 'status' / 'success.marker').exists():
    status = 'success'
elif (o2dir / 'status' / 'failed.marker').exists():
    status = 'failed'
    reason = (o2dir / 'status' / 'failed.marker').read_text(encoding='utf-8', errors='ignore').strip().replace('\n', ' | ')

bc = o2dir / 'artifacts' / f'{project_key}_O2_g.bc'
has_bc = '1' if bc.exists() and bc.stat().st_size > 0 else '0'
bc_size = str(bc.stat().st_size) if bc.exists() else '0'

rows = []
if summary.exists():
    with summary.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

rows = [r for r in rows if r.get('project') != project_key]
rows.append({
    'project': project_key,
    'status': status,
    'has_bc': has_bc,
    'bc_size': bc_size,
    'bc_path': str(bc),
    'reason': reason,
})
rows.sort(key=lambda x: x['project'])

with summary.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['project', 'status', 'has_bc', 'bc_size', 'bc_path', 'reason'])
    w.writeheader()
    w.writerows(rows)

print(summary)
PYEOF
}

write_project_readme() {
  local project_key="$1"
  local o2dir="$2"
  local source_root="$3"
  local bcname="$4"
  PROJECT_KEY="$project_key" O2DIR="$o2dir" SOURCE_ROOT="$source_root" BCNAME="$bcname" python3 - <<'PYEOF'
import os
from pathlib import Path

project_key = os.environ['PROJECT_KEY']
o2dir = Path(os.environ['O2DIR'])
source_root = os.environ['SOURCE_ROOT']
bcname = os.environ['BCNAME']
logs = o2dir / 'log'

lines = []
lines.append(f'# {project_key} seahorn-O2-g compile status')
lines.append('')
lines.append('## Source and output')
lines.append(f'- Source root: `{source_root}`')
lines.append(f'- Output root: `{o2dir}`')
lines.append('')
lines.append('## Artifacts')
lines.append(f'- Whole-program bc: `{o2dir / "artifacts" / (bcname + ".bc")}`')
lines.append(f'- Whole-program ll: `{o2dir / "artifacts" / (bcname + ".ll")}`')
lines.append(f'- BC input list: `{o2dir / "artifacts" / "bc_files.list"}`')
lines.append('')
lines.append('## Logs')
lines.append(f'- Command log: `{logs / "commands.log"}`')
lines.append(f'- Build/process log: `{logs / "project.log"}`')
lines.append(f'- llvm-link log: `{logs / "llvm_link.log"}`')
lines.append(f'- IR verify log: `{logs / "verify.log"}`')
lines.append(f'- SeaHorn scan plan only: `{logs / "scan.plan.log"}`')
lines.append('')
lines.append('## Notes')
lines.append('- This phase only compiles and links whole-program bitcode with LLVM14 in SeaHorn image.')
lines.append('- No SeaHorn scanning command is executed in this run.')

(o2dir / 'readme.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
PYEOF
}

run_project() {
  local project="$1"
  local project_key="$2"
  local source_root="$3"

  local root="$RESULT_ROOT/$project_key/seahorn/$PROFILE_DIR_NAME"
  local build="$root/build"
  local artifacts="$root/artifacts"
  local logs="$root/log"
  local status_dir="$root/status"
  local success_marker="$status_dir/success.marker"
  local failed_marker="$status_dir/failed.marker"
  local cmdlog="$logs/commands.log"
  local projlog="$logs/project.log"
  local bcname="${project_key}_O2_g"

  mkdir -p "$build" "$artifacts/bc_objs" "$logs" "$status_dir" "$root/work"
  : > "$cmdlog"
  : > "$projlog"

  if [ -f "$success_marker" ]; then
    echo "[SKIP] $project_key already successful" | tee -a "$projlog"
    update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
    return 0
  fi

  echo "project=$project" >> "$projlog"
  echo "project_key=$project_key" >> "$projlog"
  echo "source_root=$source_root" >> "$projlog"
  echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$projlog"

  local mode="unsupported"
  if [ -f "$source_root/CMakeLists.txt" ]; then
    mode="cmake"
  elif [ -f "$source_root/Makefile" ] || [ "$project" = "redis" ]; then
    mode="make"
  fi
  echo "build_mode=$mode" >> "$projlog"

  if [ "$mode" = "unsupported" ]; then
    echo "unsupported build system" > "$failed_marker"
    update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
    write_project_readme "$project_key" "$root" "$source_root" "$bcname"
    return 0
  fi

  rm -f "$failed_marker"

  if [ "$mode" = "cmake" ]; then
    run_and_log "cmake -S '$source_root' -B '$build' -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=clang-14 -DCMAKE_CXX_COMPILER=clang++-14 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_C_FLAGS='-O2 -g' -DCMAKE_CXX_FLAGS='-O2 -g' -DBUILD_TESTING=OFF -DBUILD_TESTS=OFF" "$cmdlog" "$projlog" || {
      echo "cmake configure failed" > "$failed_marker"
      update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
      write_project_readme "$project_key" "$root" "$source_root" "$bcname"
      return 0
    }

    run_and_log "cmake --build '$build' -j$(nproc)" "$cmdlog" "$projlog" || {
      echo "cmake build failed" > "$failed_marker"
      update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
      write_project_readme "$project_key" "$root" "$source_root" "$bcname"
      return 0
    }

    run_and_log "cp -f '$build/compile_commands.json' '$artifacts/compile_commands.json'" "$cmdlog" "$projlog" || true

    O2DIR="$root" generate_bc_from_compile_db >> "$projlog" 2>&1 || {
      echo "bc generation from compile_commands failed" > "$failed_marker"
      update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
      write_project_readme "$project_key" "$root" "$source_root" "$bcname"
      return 0
    }
  else
    local workcopy="$root/work/$project_key"
    rm -rf "$workcopy"
    run_and_log "cp -a '$source_root' '$workcopy'" "$cmdlog" "$projlog" || {
      echo "work copy failed" > "$failed_marker"
      update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
      write_project_readme "$project_key" "$root" "$source_root" "$bcname"
      return 0
    }
    run_and_log "chmod -R u+w '$workcopy'" "$cmdlog" "$projlog" || true

    local mkroot="$workcopy"
    if [ "$project" = "redis" ]; then
      mkroot="$workcopy/src"
      run_and_log_allow_fail "make -C '$workcopy' distclean" "$cmdlog" "$projlog" || true
      run_and_log_allow_fail "make -C '$workcopy/deps' -j$(nproc) CC=clang-14 hiredis linenoise lua hdr_histogram fpconv fast_float xxhash" "$cmdlog" "$projlog" || true
      run_and_log_allow_fail "bash -lc 'cd \"$mkroot\" && ./mkreleasehdr.sh'" "$cmdlog" "$projlog" || true
      run_and_log_allow_fail "make -C '$mkroot' -j$(nproc) CC=clang-14 MALLOC=libc BUILD_TLS=no OPTIMIZATION='-O2' REDIS_CFLAGS='-g -DNULL=0'" "$cmdlog" "$projlog" || true
      run_and_log "make -C '$mkroot' -B -n CC=clang-14 MALLOC=libc BUILD_TLS=no OPTIMIZATION='-O2' REDIS_CFLAGS='-g -DNULL=0' > '$logs/make_dryrun.log'" "$cmdlog" "$projlog" || {
        echo "make dry-run failed" > "$failed_marker"
        update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
        write_project_readme "$project_key" "$root" "$source_root" "$bcname"
        return 0
      }
    else
      run_and_log_allow_fail "make -C '$mkroot' clean" "$cmdlog" "$projlog" || true
      run_and_log_allow_fail "make -C '$mkroot' -j$(nproc) CC=clang-14 CXX=clang++-14 CFLAGS='-O2 -g' CXXFLAGS='-O2 -g' OPTIMIZATION='-O2'" "$cmdlog" "$projlog" || true
      run_and_log "make -C '$mkroot' -B -n CC=clang-14 CXX=clang++-14 CFLAGS='-O2 -g' CXXFLAGS='-O2 -g' OPTIMIZATION='-O2' > '$logs/make_dryrun.log'" "$cmdlog" "$projlog" || {
        echo "make dry-run failed" > "$failed_marker"
        update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
        write_project_readme "$project_key" "$root" "$source_root" "$bcname"
        return 0
      }
    fi

    O2DIR="$root" SRCDIR="$mkroot" generate_bc_from_make_dryrun >> "$projlog" 2>&1 || {
      echo "bc generation from make dry-run failed" > "$failed_marker"
      update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
      write_project_readme "$project_key" "$root" "$source_root" "$bcname"
      return 0
    }
  fi

  O2DIR="$root" BCNAME="$bcname" LLVM_LINK="$LLVM_LINK" LLVM_DIS="$LLVM_DIS" link_whole_program_bc > "$logs/llvm_link.log" 2>&1 || {
    echo "llvm-link failed" > "$failed_marker"
    update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
    write_project_readme "$project_key" "$root" "$source_root" "$bcname"
    return 0
  }

  O2DIR="$root" BCNAME="$bcname" verify_ir > "$logs/verify.log" 2>&1 || true

  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    "sea horn artifacts/${bcname}.bc --solve --step=large --track=reg --cpu 1800 --mem 20000" >> "$cmdlog"
  {
    echo "This phase does not execute SeaHorn scans."
    echo "Planned command for next phase:"
    echo "sea horn artifacts/${bcname}.bc --solve --step=large --track=reg --cpu 1800 --mem 20000"
  } > "$logs/scan.plan.log"

  {
    echo "success_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "bc_path=$artifacts/$bcname.bc"
    echo "ll_path=$artifacts/$bcname.ll"
    echo "mode=compile_only"
    echo "toolchain=llvm14"
  } > "$success_marker"
  rm -f "$failed_marker"

  update_compile_summary "$project_key" "$root" >> "$projlog" 2>&1 || true
  write_project_readme "$project_key" "$root" "$source_root" "$bcname"
}

echo "Starting SeaHorn LLVM14 whole-program compile pass"
echo "Profile: $PROFILE_DIR_NAME"
echo "Policy: compile flags only -O2 -g (no -DNDEBUG, no RelWithDebInfo)"

for p in "${PROJECTS[@]}"; do
  key="$(map_project_key "$p")"
  src="$(map_source_root "$p")"
  echo "==== Project: $p ($key) ===="
  if [ ! -d "$src" ]; then
    out="$RESULT_ROOT/$key/seahorn/$PROFILE_DIR_NAME"
    mkdir -p "$out/status" "$out/log"
    echo "missing_source" > "$out/status/failed.marker"
    echo "missing source: $src" > "$out/log/project.log"
    : > "$out/log/commands.log"
    update_compile_summary "$key" "$out" || true
    continue
  fi
  run_project "$p" "$key" "$src"
done

echo "All projects processed. Summary: $RESULT_ROOT/seahorn_O2_g_compile_status.csv"
