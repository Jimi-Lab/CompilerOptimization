#!/usr/bin/env bash
set -euo pipefail

BASE="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g"
SRC="/home/jimi/PaperExperiment/CompilerOptimization/Target/redis"
WORK="$BASE/work/redis-src"
ART="$BASE/artifacts"
LOG="$BASE/log"
STATUS="$BASE/status"

mkdir -p "$BASE" "$ART" "$LOG" "$STATUS" "$BASE/work"

CMDLOG="$LOG/commands.log"
BUILDLOG="$LOG/build.log"

: > "$CMDLOG"
: > "$BUILDLOG"

log_cmd() {
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$CMDLOG"
}

run_log() {
  log_cmd "$*"
  "$@" >> "$BUILDLOG" 2>&1
}

echo "project=redis" >> "$BUILDLOG"
echo "source=$SRC" >> "$BUILDLOG"
echo "start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$BUILDLOG"
echo "policy=README Build Redis from source + clang-14 -O2 -g in seahorn llvm14 container" >> "$BUILDLOG"

# README dependency installation step (done in container per run, option 2)
run_log apt-get update
run_log apt-get install -y --no-install-recommends \
  ca-certificates wget dpkg-dev gcc g++ libc6-dev libssl-dev make git python3 \
  python3-pip python3-venv python3-dev unzip rsync clang automake autoconf \
  gcc-10 g++-10 libtool libblocksruntime-dev pkg-config

# README step for Ubuntu flows requires CMake 3.31.6.
run_log pip3 install cmake==3.31.6
run_log ln -sf /usr/local/bin/cmake /usr/bin/cmake
run_log cmake --version

run_log rm -rf "$WORK"
run_log mkdir -p "$WORK"
run_log rsync -a --delete "$SRC/" "$WORK/"
run_log chmod +x "$WORK/src/mkreleasehdr.sh"
log_cmd chmod_optional_jemalloc_configure
chmod +x "$WORK/deps/jemalloc/configure" >> "$BUILDLOG" 2>&1 || true

# clang-14 strictness fix for atomic function pointer initializer in redis src.
log_cmd patch_threads_mngr_for_clang14
python3 - <<'PY' >> "$BUILDLOG" 2>&1
from pathlib import Path
p = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src/src/threads_mngr.c')
txt = p.read_text(encoding='utf-8')
old = 'static redisAtomic run_on_thread_cb g_callback = NULL;'
new = 'static redisAtomic run_on_thread_cb g_callback = (run_on_thread_cb)0;'
if old in txt:
    txt = txt.replace(old, new, 1)
    p.write_text(txt, encoding='utf-8')
    print('patched_threads_mngr_initializer=1')
else:
    print('patched_threads_mngr_initializer=0')
PY

run_log bash -lc "cd '$WORK' && make distclean"

# Build from source following README flags, plus required clang -O2 -g.
log_cmd "attempt_full_build_with_modules"
set +e
bash -lc "cd '$WORK' && export BUILD_TLS=yes BUILD_WITH_MODULES=yes INSTALL_RUST_TOOLCHAIN=yes DISABLE_WERRORS=yes && make -j \"\$(nproc)\" all CC=clang-14 CXX=clang++-14 OPT='-O2' DEBUG='-g' REDIS_CFLAGS='-DNULL=0' MALLOC=libc V=1" >> "$BUILDLOG" 2>&1
FULL_RC=$?
set -e

if [[ "$FULL_RC" -ne 0 ]]; then
  echo "full_build_with_modules_exit=$FULL_RC" >> "$BUILDLOG"
  echo "fallback=build_core_redis_only (BUILD_WITH_MODULES not set)" >> "$BUILDLOG"
  run_log bash -lc "cd '$WORK' && make distclean"
  run_log bash -lc "cd '$WORK' && export BUILD_TLS=yes DISABLE_WERRORS=yes && make -j \"\$(nproc)\" all CC=clang-14 CXX=clang++-14 OPT='-O2' DEBUG='-g' REDIS_CFLAGS='-DNULL=0' MALLOC=libc V=1"
fi

log_cmd copy_main_binaries
cp -f "$WORK/src/redis-server" "$ART/redis-server_O2_g" >> "$BUILDLOG" 2>&1
cp -f "$WORK/src/redis-cli" "$ART/redis-cli_O2_g" >> "$BUILDLOG" 2>&1
cp -f "$WORK/src/redis-benchmark" "$ART/redis-benchmark_O2_g" >> "$BUILDLOG" 2>&1
cp -f "$WORK/src/redis-check-rdb" "$ART/redis-check-rdb_O2_g" >> "$BUILDLOG" 2>&1
cp -f "$WORK/src/redis-check-aof" "$ART/redis-check-aof_O2_g" >> "$BUILDLOG" 2>&1
cp -f "$WORK/src/redis-sentinel" "$ART/redis-sentinel_O2_g" >> "$BUILDLOG" 2>&1

if [[ -f "$WORK/src/redis-tls.so" ]]; then
  cp -f "$WORK/src/redis-tls.so" "$ART/redis-tls_O2_g.so" >> "$BUILDLOG" 2>&1
fi

log_cmd verify_compiler_flags_from_verbose_log
python3 - <<'PY' > "$ART/compile_flag_check.txt"
from pathlib import Path

log = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/log/build.log').read_text(encoding='utf-8', errors='ignore')
lines = [ln.strip() for ln in log.splitlines() if 'clang-14' in ln]
core_lines = [ln for ln in lines if '/work/redis-src/src/' in ln]
with_o2 = sum(1 for ln in lines if ' -O2' in ln)
with_g = sum(1 for ln in lines if ' -g' in ln)
with_o3 = sum(1 for ln in lines if ' -O3' in ln)
core_with_o2 = sum(1 for ln in core_lines if ' -O2' in ln)
core_with_g = sum(1 for ln in core_lines if ' -g' in ln)
core_with_o3 = sum(1 for ln in core_lines if ' -O3' in ln)

print(f'clang14_command_lines={len(lines)}')
print(f'command_lines_with_O2={with_o2}')
print(f'command_lines_with_g={with_g}')
print(f'command_lines_with_O3={with_o3}')
print(f'core_redis_clang14_lines={len(core_lines)}')
print(f'core_redis_lines_with_O2={core_with_o2}')
print(f'core_redis_lines_with_g={core_with_g}')
print(f'core_redis_lines_with_O3={core_with_o3}')
PY

log_cmd write_artifact_manifest
python3 - <<'PY' > "$ART/build_outputs.list"
from pathlib import Path
art = Path('/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/artifacts')
for p in sorted(art.glob('*')):
    if p.is_file():
        print(str(p))
PY

{
  echo "work_dir=$WORK"
  echo "artifacts=$ART"
  echo "build_log=$BUILDLOG"
  echo "commands_log=$CMDLOG"
  echo "flag_check=$ART/compile_flag_check.txt"
  echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} > "$STATUS/success.marker"

rm -f "$STATUS/failed.marker"
echo "done_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$BUILDLOG"

# Keep host workspace writable after container root build.
if [[ -n "${HOST_UID:-}" && -n "${HOST_GID:-}" ]]; then
  chown -R "${HOST_UID}:${HOST_GID}" "$BASE" >/dev/null 2>&1 || true
fi
