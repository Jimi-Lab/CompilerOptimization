#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g"
WORK="$BASE/work/redis-src"
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

if [[ ! -d "$WORK/src" ]]; then
  echo "missing redis work source: $WORK/src" >&2
  exit 1
fi

log_cmd "python3_compile_redis_server_and_deps_to_bc"
python3 - <<'PY' >> "$BCLOG" 2>&1
from pathlib import Path
import subprocess

base = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g')
work = base / 'work' / 'redis-src'
art = base / 'artifacts'
bc_root = art / 'bc_objs_redis_server'
bc_root.mkdir(parents=True, exist_ok=True)

src_dir = work / 'src'
deps_dir = work / 'deps'
vec_dir = work / 'modules' / 'vector-sets'

src_flags = [
    '-pedantic', '-DREDIS_STATIC=', '-Wno-c11-extensions',
    '-std=gnu11', '-Wall', '-W', '-Wno-missing-field-initializers',
    '-Werror=deprecated-declarations', '-Wstrict-prototypes',
    '-O2', '-g', '-DNULL=0',
    '-I../deps/hiredis', '-I../deps/linenoise', '-I../deps/lua/src',
    '-I../deps/hdr_histogram', '-I../deps/fpconv', '-I../deps/fast_float',
    '-I../deps/xxhash', '-DUSE_OPENSSL=1', '-DBUILD_TLS_MODULE=0',
    '-DINCLUDE_VEC_SETS=1'
]

def run(cmd, cwd):
    subprocess.run(cmd, check=True, cwd=cwd)

mk = (src_dir / 'Makefile').read_text(encoding='utf-8', errors='ignore').splitlines()
server_objs = []
vec_objs = []
for ln in mk:
    if ln.startswith('REDIS_SERVER_OBJ='):
        server_objs = [x for x in ln.split('=', 1)[1].split() if x.endswith('.o')]
    if ln.startswith('REDIS_VEC_SETS_OBJ='):
        vec_objs = [x for x in ln.split('=', 1)[1].split() if x.endswith('.o')]

if not server_objs:
    raise SystemExit('Failed to parse REDIS_SERVER_OBJ from src/Makefile')

compiled = []

for obj in server_objs + vec_objs:
    stem = obj[:-2]
    cand_src = src_dir / f'{stem}.c'
    cwd = src_dir
    if not cand_src.exists():
        cand_src = vec_dir / f'{stem}.c'
        cwd = vec_dir
    if not cand_src.exists():
        print('skip_missing_source', obj)
        continue
    out_bc = bc_root / 'src' / f'{stem}.bc'
    out_bc.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['clang-14', *src_flags, '-emit-llvm', '-c', str(cand_src), '-o', str(out_bc)]
    run(cmd, cwd=cwd)
    compiled.append(out_bc)

hiredis_dir = deps_dir / 'hiredis'
hiredis_members = subprocess.run(['ar', 't', str(hiredis_dir / 'libhiredis.a')], check=True, capture_output=True, text=True).stdout.splitlines()
for mem in hiredis_members:
    if not mem.endswith('.o'):
        continue
    src = hiredis_dir / (Path(mem).stem + '.c')
    if not src.exists():
        continue
    out_bc = bc_root / 'deps_hiredis' / (Path(mem).stem + '.bc')
    out_bc.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        'clang-14', '-std=c99', '-Wall', '-Wextra', '-Wstrict-prototypes',
        '-Wwrite-strings', '-Wno-missing-field-initializers', '-O2', '-g',
        '-fPIC', '-emit-llvm', '-c', str(src), '-o', str(out_bc)
    ]
    run(cmd, cwd=hiredis_dir)
    compiled.append(out_bc)

lua_dir = deps_dir / 'lua' / 'src'
lua_members = subprocess.run(['ar', 't', str(lua_dir / 'liblua.a')], check=True, capture_output=True, text=True).stdout.splitlines()
for mem in lua_members:
    if not mem.endswith('.o'):
        continue
    src = lua_dir / (Path(mem).stem + '.c')
    if not src.exists():
        continue
    out_bc = bc_root / 'deps_lua' / (Path(mem).stem + '.bc')
    out_bc.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        'clang-14', '-Wall', '-DLUA_ANSI', '-DENABLE_CJSON_GLOBAL', '-DREDIS_STATIC=',
        '-DLUA_USE_MKSTEMP', '-O2', '-g', '-emit-llvm', '-c', str(src), '-o', str(out_bc)
    ]
    run(cmd, cwd=lua_dir)
    compiled.append(out_bc)

hdr_dir = deps_dir / 'hdr_histogram'
hdr_src = hdr_dir / 'hdr_histogram.c'
out_bc = bc_root / 'deps_hdr' / 'hdr_histogram.bc'
out_bc.parent.mkdir(parents=True, exist_ok=True)
run([
    'clang-14', '-std=c99', '-Wall', '-O2', '-g', '-DHDR_MALLOC_INCLUDE="hdr_redis_malloc.h"',
    '-emit-llvm', '-c', str(hdr_src), '-o', str(out_bc)
], cwd=hdr_dir)
compiled.append(out_bc)

fp_dir = deps_dir / 'fpconv'
fp_src = fp_dir / 'fpconv_dtoa.c'
out_bc = bc_root / 'deps_fpconv' / 'fpconv_dtoa.bc'
out_bc.parent.mkdir(parents=True, exist_ok=True)
run(['clang-14', '-Wall', '-O2', '-g', '-emit-llvm', '-c', str(fp_src), '-o', str(out_bc)], cwd=fp_dir)
compiled.append(out_bc)

ff_dir = deps_dir / 'fast_float'
ff_src = ff_dir / 'fast_float_strtod.cpp'
out_bc = bc_root / 'deps_fast_float' / 'fast_float_strtod.bc'
out_bc.parent.mkdir(parents=True, exist_ok=True)
run(['clang++-14', '-Wall', '-O2', '-g', '-std=c++11', '-DFASTFLOAT_ALLOWS_LEADING_PLUS', '-emit-llvm', '-c', str(ff_src), '-o', str(out_bc)], cwd=ff_dir)
compiled.append(out_bc)

xx_dir = deps_dir / 'xxhash'
xx_src = xx_dir / 'xxhash.c'
out_bc = bc_root / 'deps_xxhash' / 'xxhash.bc'
out_bc.parent.mkdir(parents=True, exist_ok=True)
run(['clang-14', '-fPIC', '-O2', '-g', '-emit-llvm', '-c', str(xx_src), '-o', str(out_bc)], cwd=xx_dir)
compiled.append(out_bc)

lst = art / 'bc_files_redis_server.list'
lst.write_text(''.join(str(p) + '\n' for p in compiled), encoding='utf-8')
print('compiled_bc_files', len(compiled))
print('bc_list', lst)
PY

log_cmd "llvm-link_redis_server_bc"
llvm-link-14 $(python3 - <<'PY'
from pathlib import Path
for line in Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/artifacts/bc_files_redis_server.list').read_text(encoding='utf-8').splitlines():
    if line.strip():
        print(line.strip())
PY
) -o "$ART/redis-server_O2_g.bc" >> "$LNKLOG" 2>&1

log_cmd "llvm-dis_redis_server_bc"
llvm-dis-14 "$ART/redis-server_O2_g.bc" -o "$ART/redis-server_O2_g.ll" >> "$LNKLOG" 2>&1

log_cmd "llvm-nm_main_check"
llvm-nm-14 "$ART/redis-server_O2_g.bc" > "$LOG/llvm_nm_redis_server_bc.log" 2>&1

MAIN_STATUS="$(python3 - <<'PY'
from pathlib import Path
txt = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/log/llvm_nm_redis_server_bc.log').read_text(encoding='utf-8', errors='replace')
print('present' if any(line.rstrip().endswith(' T main') for line in txt.splitlines()) else 'missing')
PY
)"

{
  echo "redis_server_bc=$ART/redis-server_O2_g.bc"
  echo "redis_server_ll=$ART/redis-server_O2_g.ll"
  echo "bc_list=$ART/bc_files_redis_server.list"
  echo "main_symbol=$MAIN_STATUS"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/bc_success.marker"
