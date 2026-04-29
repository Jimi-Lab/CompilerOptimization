# 构建 `ikos:3.5-llvm14-o2g` 的修复记录

## 背景

本次 patch 明确只面向 IKOS 3.5 官方支持的 LLVM 14 系列环境：

- 基础镜像固定为 `ikos:3.5-llvm14`
- 容器内使用 `clang-14` / `llvm-14` / `llvm-config-14`
- 待分析输入应为 `clang-14` 生成的 LLVM 14 bitcode

原始 `ikos:3.5-llvm14` 在分析优化后的 `-O2 -g` bitcode 时会在 LLVM-to-AR 阶段失败：

```text
unsupported llvm cmp instruction with predicate: eq [2]
```

原因是优化后的 IR 中包含 `<8 x i8>` 向量比较。手动用 LLVM `opt -scalarizer` 预处理后，向量比较可以被消除，但 IKOS 继续在 LLVM `freeze` 指令处失败：

```text
unsupported llvm instruction freeze [2]
```

## 修复内容

修改文件：

```text
CompilerOptimization/Tools/ikos/ikos/frontend/llvm/src/ikos_pp.cpp
CompilerOptimization/Tools/ikos/ikos/frontend/llvm/src/import/function.cpp
CompilerOptimization/Tools/ikos/ikos/frontend/llvm/src/import/function.hpp
```

核心改动：

- 在 `ikos-pp` 的 none/basic/aggressive 预处理链路中加入 LLVM `Scalarizer`，把优化 IR 中的向量操作标量化。
- 在 LLVM importer 中新增 `FreezeInst` 翻译，把 `freeze x` 作为 `result := x` 处理，避免 IKOS 前端因未知指令退出。

这些改动都建立在 LLVM 14 工具链上，不引入 LLVM 13 或其他 LLVM 主版本。

## 构建镜像

构建脚本：

```bash
CompilerOptimization/Tools/ikos/build_ikos_o2g_image.sh ikos:3.5-llvm14-o2g
```

默认基础镜像是：

```text
ikos:3.5-llvm14
```

脚本中已经固定只使用这个 LLVM 14 基础镜像，不再接受其他 LLVM 主版本作为 base image。

## 验证命令

```bash
BC_PATH=/path/to/your/llvm14_O2_g.bc

timeout -s KILL -k 10 600 \
docker run --rm --user 1000:1000 \
  -v /home/jimi/PaperExperiment:/work \
  -w /work \
  --entrypoint /bin/bash \
  ikos:3.5-llvm14-o2g \
  -lc "ikos --display-summary=no --progress=no \
    --report-file /tmp/cjson_o2g_ikos_patched.csv \
    -f=csv --status-filter=\"*\" \
    ${BC_PATH}"
```

推荐输入：

- `clang-14 -O2 -g -emit-llvm` 生成的 `.bc`
- 与容器内 LLVM 14 工具链保持同主版本

不建议输入：

- `clang-13` 或其他非 LLVM 14 主版本生成的 `.bc`
- 需要跨主版本兼容假设的 bitcode
