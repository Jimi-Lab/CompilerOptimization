# Curl 7.68.0 在 IKOS Docker 中的 O2 编译与 Bitcode 扫描记录

## 1. 目标

在 **IKOS 容器环境** 内完成以下流程：

1. 使用 `clang-14` + `-O2` 正常配置和编译 `curl`；
2. 利用 `ikos-scan` 拦截编译，生成 executable 级别的 `curl.bc`；
3. 执行 `ikos` 对生成的 bitcode 文件进行全部项、basic 优化、进程间 (inter-procedural) 的静态分析扫描；
4. 获得分析数据库 `curl.db`。

---

## 2. 路径约定

- 源码目录（宿主机）: `/home/jimi/PaperExperiment/CompilerOptimization/Target/Curl/7.68.0/curl-curl-7_68_0`
- 输出根目录（宿主机）: `/home/jimi/PaperExperiment/CompilerOptimization/Result/curl/ikos/O2_scan_with_ikos_scan`

容器内对应映射为：
- 源码：`/work/src`
- 输出：`/work/out`

---

## 3. 执行细节与步骤

与 `leveldb` 的 `cmake` 体系不同，`curl` 是基于 `autotools` (`configure` 和 `make`)。若直接用 `ikos-scan ./configure` 可能会导致某些依赖 C 编译器底层机制的检测用例非预期报错（例如检测 `sizeof(size_t)` 和 `struct timeval`）。为了成功完成 `ikos-scan`，我们采用了**分步介入策略**。

### 3.1 预处理：修补 `ikos-scan` 提取脚本

确保系统安装 `file` 以识别可执行文件，并修改 `ikos-scan` 的 Python 脚本中的 `extract_bitcode`，让其通过 `llvm-objcopy --dump-section` 强制获取链接后的 `.bc` 路径。

### 3.2 Configure 流程 (纯 Clang)

配置 `curl` 时使用原生的 `clang-14` 以保证所有特征测试宏如期建立，强行带入 `-O2` 参数：

```bash
cd /work/src
./configure \
  CC=clang-14 \
  CXX=clang++-14 \
  CFLAGS="-O2 -g" \
  CXXFLAGS="-O2 -g" \
  --disable-shared --enable-static \
  --without-ssl --without-libssh2 --without-brotli --without-zstd \
  --disable-ldap --disable-ldaps --disable-threaded-resolver
```

### 3.3 构建与提纯 Bitcode (`ikos-scan`)

正式调用 `ikos-scan` 劫持 `make` 过程。使用 `yes n` 抑制默认分析，以便稍后自行增加完整分析选项：

```bash
yes n | ikos-scan make -j4
# 拷贝所有生成的目标文件
find /work/src/src -name "curl" -type f -executable -exec cp {} /work/out/build/ \;
find /work/src -name "*.bc" -exec cp {} /work/out/build/ \;
```
*备注：此时在 `/work/out/build` 下已成功产生了重达 `4.6MB` 的单文件全程序 Bitcode (`curl.bc`)*。

### 3.4 全量参数深层扫描

执行 IKOS 分析，开启所有安全属性检查，设定为 `-opt=basic` 并采取 `inter-procedural` 分析模型：

```bash
cd /work/out/build
ikos --opt=basic --proc=inter -a=boa,dbz,nullity,prover,upa,uva,sio,uio,shc,poa,pcmp,sound,fca,dca,dfa curl.bc -o curl.db
```

---

## 4. 输出产物

1. `/build/curl.bc`: 带有 `-O2` 优化语义的 `curl` LLVM IR 全局 Bitcode。
2. `/build/curl.db`: IKOS 静态分析产生的结果 SQLite 数据库（可通过 `ikos-report` 或 `ikos-view` 查阅漏洞预警）。
3. `/logs/configure.log`: `autotools` 的环境变量与特性检测日志。
4. `/logs/ikos_scan_build.log`: `ikos-scan` 的编译拦截及 Bitcode 链接记录。
5. `/logs/ikos_analyze.log`: `ikos` 主引擎深度分析的控制台输出日志。

