# Redis LLVM14-O2-g 编译与 BC 生成记录

## 目标
- 源码路径：`/home/jimi/PaperExperiment/CompilerOptimization/Target/redis`
- 结果路径：`/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g`
- 编译环境：`seahorn/seahorn-llvm14:fixed`
- 约束：`clang-14`，`-O2 -g`

## 主机侧执行命令（Docker 启动命令）
```bash
docker run --rm --user 0:0 \
  -e HOST_UID="$(id -u)" -e HOST_GID="$(id -g)" \
  -v "/home/jimi/PaperExperiment:/home/jimi/PaperExperiment" \
  -w "/home/jimi/PaperExperiment" \
  --entrypoint /bin/bash seahorn/seahorn-llvm14:fixed -lc \
  "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/rebuild_redis_official_in_seahorn_llvm14_o2g.sh"
```

```bash
docker run --rm --user 0:0 \
  -v "/home/jimi/PaperExperiment:/home/jimi/PaperExperiment" \
  -w "/home/jimi/PaperExperiment" \
  --entrypoint /bin/bash seahorn/seahorn-llvm14:fixed -lc \
  "apt-get update >/dev/null && apt-get install -y --no-install-recommends libssl-dev >/dev/null && /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/build_scan_bc_redis_server_o2g.sh"
```

## Redis 编译过程（容器内实际命令）
来源：`log/commands.log`

1. 依赖安装（README Build from source 对齐）
```bash
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates wget dpkg-dev gcc g++ libc6-dev libssl-dev make git python3 \
  python3-pip python3-venv python3-dev unzip rsync clang automake autoconf \
  gcc-10 g++-10 libtool libblocksruntime-dev pkg-config
pip3 install cmake==3.31.6
ln -sf /usr/local/bin/cmake /usr/bin/cmake
cmake --version
```

2. 工作目录准备与补丁
```bash
rm -rf /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src
mkdir -p /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src
rsync -a --delete /home/jimi/PaperExperiment/CompilerOptimization/Target/redis/ /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src/
chmod +x /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src/src/mkreleasehdr.sh
```

3. 首次构建（带 modules，失败后回退）
```bash
bash -lc "cd '/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src' && make distclean"
bash -lc "cd '/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src' && export BUILD_TLS=yes BUILD_WITH_MODULES=yes INSTALL_RUST_TOOLCHAIN=yes DISABLE_WERRORS=yes && make -j \"$(nproc)\" all CC=clang-14 CXX=clang++-14 OPT='-O2' DEBUG='-g' REDIS_CFLAGS='-DNULL=0' MALLOC=libc V=1"
```

4. 回退构建（核心 Redis，成功）
```bash
bash -lc "cd '/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src' && make distclean"
bash -lc "cd '/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/work/redis-src' && export BUILD_TLS=yes DISABLE_WERRORS=yes && make -j \"$(nproc)\" all CC=clang-14 CXX=clang++-14 OPT='-O2' DEBUG='-g' REDIS_CFLAGS='-DNULL=0' MALLOC=libc V=1"
```

5. 成功产物复制
```bash
cp -f "$WORK/src/redis-server" "$ART/redis-server_O2_g"
cp -f "$WORK/src/redis-cli" "$ART/redis-cli_O2_g"
cp -f "$WORK/src/redis-benchmark" "$ART/redis-benchmark_O2_g"
cp -f "$WORK/src/redis-check-rdb" "$ART/redis-check-rdb_O2_g"
cp -f "$WORK/src/redis-check-aof" "$ART/redis-check-aof_O2_g"
cp -f "$WORK/src/redis-sentinel" "$ART/redis-sentinel_O2_g"
```

## BC 生成过程（可直接投喂静态分析）
来源：`log/bc_commands.log`

```bash
python3_compile_redis_server_and_deps_to_bc
llvm-link_redis_server_bc
llvm-dis_redis_server_bc
llvm-nm_main_check
```

脚本：`build_scan_bc_redis_server_o2g.sh`

- 从 `src/Makefile` 解析 `REDIS_SERVER_OBJ` / `REDIS_VEC_SETS_OBJ`
- 用 `clang-14 -O2 -g -emit-llvm -c` 逐个重编译为 `.bc`
- 同步重编译依赖并链接进最终 BC：`hiredis/lua/hdr_histogram/fpconv/fast_float/xxhash`
- `llvm-link-14` 合并为单文件：`redis-server_O2_g.bc`

## 最终结果
- 可执行文件：
  - `artifacts/redis-server_O2_g`
  - `artifacts/redis-cli_O2_g`
  - `artifacts/redis-benchmark_O2_g`
  - `artifacts/redis-check-rdb_O2_g`
  - `artifacts/redis-check-aof_O2_g`
  - `artifacts/redis-sentinel_O2_g`
- 静态分析 BC：
  - `artifacts/redis-server_O2_g.bc`
  - `artifacts/redis-server_O2_g.ll`
  - `artifacts/bc_files_redis_server.list`

## 校验与状态文件
- 构建成功标记：`status/success.marker`
- BC 成功标记：`status/bc_success.marker`
- 编译参数统计：`artifacts/compile_flag_check.txt`
  - `core_redis_lines_with_O2=238`
  - `core_redis_lines_with_g=238`
  - `core_redis_lines_with_O3=0`
- `main` 校验（BC）：`status/bc_success.marker` 中 `main_symbol=present`

## 日志文件
- Redis 编译全日志：`log/build.log`
- Redis 编译命令时间线：`log/commands.log`
- BC 生成日志：`log/bc_build.log`
- BC 链接日志：`log/bc_link.log`
- BC 命令时间线：`log/bc_commands.log`

## 说明
- `BUILD_WITH_MODULES=yes` 的完整模块构建在 clang-14 下出现模块侧编译问题，脚本自动回退到核心 Redis 构建并成功产出核心二进制。
- 模块失败摘要见：`artifacts/module_build_failure_summary.txt`
