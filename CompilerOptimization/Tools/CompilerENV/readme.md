# CompilerENV（论文实验编译基座）设计规范

## 1. 目标与边界

### 1.1 目标
`CompilerENV` 只做一件事：  
**稳定、可复现地编译目标项目，并产出适用于多种分析器的标准工件**（LLVM bitcode / IR / binary / compile_commands）。

用于支撑以下工具链（在独立容器中运行）：
- LLVM IR / BC 工具：SVF、Phasar、IKOS、KLEE、SeaHorn、SMACK
- 前端分析链：CodeChecker、clang static analyzer
- 二进制分析：angr（主要依赖 binary，不依赖 BC）

### 1.2 非目标（必须明确）
- 不在 CompilerENV 内安装/运行上述分析器。
- 不在 CompilerENV 内做漏洞判定。
- 不承担工具版本冲突处理（由各工具容器处理）。

---

## 2. 统一技术栈（固定）

- **OS**: Ubuntu 22.04 LTS
- **LLVM/Clang**: 14.x（`clang-14`, `clang++-14`, `llvm-link-14`, `opt-14`, `llvm-dis-14`）
- **构建系统**: cmake + make/ninja（按项目选择）
- **编译数据库**: `compile_commands.json`（强制导出）
- **默认优化**: `-O2`（论文主线）
- **对照优化宇宙**:
  - `O0`: `-O0 -g`
  - `O2`: `-O2 -g`
  - `O2_noinline`: `-O2 -g -fno-inline`

> 说明：若后续需加入 `-flto`、`-fno-omit-frame-pointer`，应在实验记录中单独标注，避免与主结果混淆。

---

## 3. 产物规范（统一输出）

每个目标项目每个优化宇宙都必须产出：

1. **链接后二进制**
   - 如 `bin/*`, `lib*.so`, `lib*.a`
2. **LLVM bitcode**
   - 目标级 `.bc`（文件级）
   - 尽可能提供 whole-program `.bc`（或 core-subset `.bc`）
3. **可读 IR**
   - `.ll`（用于人工核验）
4. **构建数据库**
   - `compile_commands.json`
5. **完整日志**
   - `configure.log`, `build.log`, `bc_generate.log`
6. **元数据**
   - `toolchain_versions.txt`（clang/llvm/cmake/git）
   - `build_flags.txt`
   - `artifact_manifest.tsv`

---

## 4. 目录约定（强约束）

建议统一：
```text
CompilerOptimization/Result/<target>/CompilerENV/
  O0/
    build/
    artifacts/
    logs/
  O2/
    build/
    artifacts/
    logs/
  O2_noinline/
    build/
    artifacts/
    logs/
  manifest/
    toolchain_versions.txt
    env_fingerprint.txt
```

---

## 5. 编译策略（跨工具兼容）

### 5.1 通用 C/C++ 标志
- CFLAGS/CXXFLAGS 建议基础集：
  - `-g -fno-omit-frame-pointer`
  - 优化按宇宙切换：`-O0` / `-O2` / `-O2 -fno-inline`
- 生成 IR/BC：
  - 单文件：`-emit-llvm -c`
  - 全程序：通过 compile database + 链接阶段聚合（或 wllvm 流程）

### 5.2 与分析器兼容注意点
- **SVF/Phasar/IKOS/KLEE/SeaHorn/SMACK**：严格依赖 LLVM 版本一致性（推荐全链 14）。
- **CodeChecker/clangsa**：依赖 compile commands 与 clang 前端，不要求 whole-program BC。
- **angr**：主要消费 ELF/PE binary；可额外保留 `-g` 便于定位映射。
- **C++ RTTI/异常**：不要随意禁用（除非实验明确控制变量）。

---

## 6. 目标项目覆盖（论文样本池）

当前计划样本：
- leveldb, redis, opencv, rethinkdb, grpc, flite, masscan, rapidjson, libco, lepton, zfp

要求：
- 每个项目至少跑通 `O2` 编译与基础产物导出
- 论文主实验项目（优先）：`leveldb`, `redis`, `curl/grpc`（按可复现性与日志质量选）

---

## 7. 可复现性要求（论文级）

1. 镜像需固定 tag，不使用 `latest`
2. 所有脚本可重入（重复执行不污染结果）
3. 每次运行记录：
   - git commit hash（目标项目）
   - container image digest
   - CPU/内存信息
   - 超时策略与失败原因
4. 失败必须落日志，不允许静默失败

---

## 8. 质量门禁（每次实验前检查）

- `clang-14 --version` 与 `llvm-link-14 --version` 一致
- `compile_commands.json` 存在且可解析
- `.bc` 文件可被 `llvm-dis-14` 正常反汇编
- 关键二进制可执行（最小 smoke test）
- 日志包含完整编译命令（便于审稿复核）

---

## 9. 与论文问题的直接对应

本环境是“语义坍塌研究”的**基础设施层**，服务于：
- 在 `O0/O2/O2_noinline` 三宇宙中生成严格可比工件
- 支持后续 IR 分析器复现实验
- 支持人工核查“报告行号/漏洞类型/路径可达性”对应关系
- 为 LLM Agent 修复流程提供统一输入（源码 + IR + 构建元数据）

---

## 10. 最终原则（必须遵守）

- **CompilerENV 只编译，不分析。**
- **版本固定优先于“新版本”。**
- **日志完整优先于“跑得快”。**
- **可复现优先于“偶然跑通”。**