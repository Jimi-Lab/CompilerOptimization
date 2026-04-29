#!/usr/bin/env bash
set -euo pipefail

# 用法：
#   TARGET_DIR=/work/leveldb \
#   OUT_ROOT=/work/CompilerOptimization/Result/leveldb/CompilerENV \
#   bash build_matrix.sh

TARGET_DIR="${TARGET_DIR:-/work/leveldb}"
OUT_ROOT="${OUT_ROOT:-/work/CompilerOptimization/Result/leveldb/CompilerENV}"

CLANG_C="${CC:-clang-14}"
CLANG_CXX="${CXX:-clang++-14}"
LLVM_LINK="${LLVM_LINK:-llvm-link-14}"
LLVM_DIS="${LLVM_DIS:-llvm-dis-14}"

mkdir -p "${OUT_ROOT}/manifest"

log() { echo "[$(date '+%F %T')] $*"; }

write_toolchain_meta() {
  {
    echo "date: $(date -Is)"
    echo "target_dir: ${TARGET_DIR}"
    echo "clang: $(${CLANG_C} --version | head -n1)"
    echo "clang++: $(${CLANG_CXX} --version | head -n1)"
    echo "llvm-link: $(${LLVM_LINK} --version | head -n1)"
    echo "cmake: $(cmake --version | head -n1)"
    echo "git: $(git --version)"
    if [ -d "${TARGET_DIR}/.git" ]; then
      echo "target_commit: $(git -C "${TARGET_DIR}" rev-parse HEAD || true)"
    fi
  } > "${OUT_ROOT}/manifest/toolchain_versions.txt"
}

build_one() {
  local U="$1"          # O0 / O2 / O2_noinline
  local OPT_FLAGS="$2"  # "-O0 -g" etc.

  local UROOT="${OUT_ROOT}/${U}"
  local BDIR="${UROOT}/build"
  local ADIR="${UROOT}/artifacts"
  local LDIR="${UROOT}/logs"
  mkdir -p "${BDIR}" "${ADIR}" "${LDIR}"

  log "=== [${U}] configure ==="
  cmake -S "${TARGET_DIR}" -B "${BDIR}" -G "Ninja" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DLEVELDB_BUILD_TESTS=OFF \
    -DLEVELDB_BUILD_BENCHMARKS=OFF \
    -DCMAKE_C_COMPILER="${CLANG_C}" \
    -DCMAKE_CXX_COMPILER="${CLANG_CXX}" \
    -DCMAKE_C_FLAGS="${OPT_FLAGS} -fno-omit-frame-pointer" \
    -DCMAKE_CXX_FLAGS="${OPT_FLAGS} -fno-omit-frame-pointer" \
    > "${LDIR}/configure.log" 2>&1

  log "=== [${U}] build ==="
  cmake --build "${BDIR}" -j"$(nproc)" > "${LDIR}/build.log" 2>&1

  cp "${BDIR}/compile_commands.json" "${ADIR}/compile_commands.json"

  # 收集二进制/库
  find "${BDIR}" -type f \( -perm -111 -o -name "*.a" -o -name "*.so*" \) \
    | sort > "${ADIR}/binaries_and_libs.list"

  log "=== [${U}] generate TU bitcode from compile_commands ==="
  mkdir -p "${ADIR}/bc_objs"

  python3 - "${ADIR}/compile_commands.json" "${ADIR}/bc_objs" "${LDIR}/bc_generate.log" "${OPT_FLAGS}" "${CLANG_C}" "${CLANG_CXX}" <<'PY'
import json, os, sys, shlex, subprocess, hashlib

ccdb, outdir, logfile, opt_flags, clang_c, clang_cxx = sys.argv[1:]
opt_flags = shlex.split(opt_flags)

def run(cmd):
    with open(logfile, "a") as f:
        f.write("$ " + " ".join(shlex.quote(x) for x in cmd) + "\n")
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with open(logfile, "a") as f:
        f.write(p.stdout + "\n")
    return p.returncode

with open(ccdb) as f:
    db = json.load(f)

seen = set()
bc_files = []

for e in db:
    src = os.path.abspath(e["file"])
    if src in seen:
        continue
    seen.add(src)

    args = e.get("arguments")
    if not args:
        args = shlex.split(e["command"])

    # 选 C / C++
    ext = os.path.splitext(src)[1].lower()
    compiler = clang_c if ext in [".c"] else clang_cxx

    cleaned = []
    skip_next = False
    for i, a in enumerate(args):
        if i == 0:
            continue
        if skip_next:
            skip_next = False
            continue
        if a in ["-c", "-S", "-E"]:
            continue
        if a == "-o":
            skip_next = True
            continue
        if a.startswith("-o"):
            continue
        if a.startswith("-M"):  # 依赖生成选项
            continue
        cleaned.append(a)

    h = hashlib.sha1(src.encode()).hexdigest()[:16]
    out_bc = os.path.join(outdir, f"{h}.bc")

    cmd = [compiler] + cleaned + opt_flags + ["-emit-llvm", "-c", src, "-o", out_bc]
    rc = run(cmd)
    if rc == 0 and os.path.exists(out_bc):
        bc_files.append(out_bc)

list_path = os.path.join(os.path.dirname(outdir), "bc_files.list")
with open(list_path, "w") as f:
    for x in sorted(set(bc_files)):
        f.write(x + "\n")

print(f"generated_bc={len(set(bc_files))}")
PY

  if [[ -s "${ADIR}/bc_files.list" ]]; then
    log "=== [${U}] link whole-program bc ==="
    "${LLVM_LINK}" $(cat "${ADIR}/bc_files.list") -o "${ADIR}/leveldb_${U}.bc" \
      > "${LDIR}/llvm_link.log" 2>&1 || true

    if [[ -f "${ADIR}/leveldb_${U}.bc" ]]; then
      "${LLVM_DIS}" "${ADIR}/leveldb_${U}.bc" -o "${ADIR}/leveldb_${U}.ll" \
        > "${LDIR}/llvm_dis.log" 2>&1 || true
    fi
  fi

  # 清单
  {
    echo -e "path\tsize_bytes"
    find "${ADIR}" -type f | sort | while read -r f; do
      echo -e "${f}\t$(stat -c%s "${f}")"
    done
  } > "${ADIR}/artifact_manifest.tsv"

  echo "${OPT_FLAGS}" > "${ADIR}/build_flags.txt"
  log "=== [${U}] done ==="
}

write_toolchain_meta
build_one "O0" "-O0 -g"
build_one "O2" "-O2 -g"
build_one "O2_noinline" "-O2 -g -fno-inline"

log "ALL DONE. OUT_ROOT=${OUT_ROOT}"