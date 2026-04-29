# PaperExperiment 工作区说明

本工作区服务于一篇目标会议为 ASPLOS 的系统安全论文，研究 `clang -O2 -g` 生成的 LLVM bitcode 如何影响 IR 层静态分析与验证工具。

除非某个子目录中存在更具体的 `AGENTS.md`，否则 `/home/jimi/PaperExperiment` 下的所有文件都应遵循这些说明。

## 研究重点

- 核心研究问题是：`clang -O2 -g` 生成的带调试信息的优化 LLVM bitcode，会如何改变 IR 层静态分析工具“能够看见”的程序语义？
- 主要现象是优化诱导的语义坍缩：Inline、Mem2Reg、SROA、GVN、DCE、CFG simplification 等相关优化 pass 可能擦除调用边、合并变量身份、扭曲 DWARF 位置信息、切断 source-sink 路径，或触发路径/状态爆炸。
- 论文方向是系统导向的，而不只是测量导向的：先测量退化，再使用 Neuro-Symbolic/LLM agent 框架恢复优化 IR 中丢失的语义链接。

## 编译宇宙

主实验严格包含三个 bitcode 宇宙：

- `O0`: `clang -O0 -g`
- `O2`: `clang -O2 -g`
- `O2-noinline`: `clang -O2 -g -fno-inline`

重要约束：

- 不要向主实验添加 `-DNDEBUG`。
- 不要把 CMake 的 `RelWithDebInfo` 或任何构建系统 preset 等同于论文中的 O2 宇宙。
- 如果某个 target 必须通过 CMake 或其他构建系统构建，应检查 `compile_commands.json`、构建日志或 bitcode 生成命令，以确认实际使用的编译 flag。
- 现有历史目录中可能包含 `RelWithDebInfo` 等名称；在将其作为论文证据使用前，必须核实 artifact 背后的真实编译 flag。

## 工具范围

主实验只使用 IR/bitcode 层工具，尤其是可直接扫描 `.bc` 的工具：

- `SVF`
- `Phasar`
- `IKOS`
- `KLEE`
- `SeaHorn`
- `SMACK`
- `dg`
- `Clam`
- `cclyzer++`
- `yapall`

除非用户明确改变范围，否则不要把 CodeQL、Joern、Infer、Semgrep、Flawfinder、Cppcheck、OWASP SAST lists、SCA tools，或 source-level/front-end tools 引入主实验矩阵。

## 项目结构

- `CompilerOptimization/Target/` 包含作为分析对象的 target 源码项目。
- `CompilerOptimization/CompilerResult/` 包含已编译的 LLVM/bitcode artifact，并按 target 和优化宇宙划分。
- `CompilerOptimization/Result/` 包含 analyzer run、日志、summary、report、casebook 和实验证据。应将这些内容视为研究 artifact，而不是可随意丢弃的构建输出。
- `CompilerOptimization/Tools/` 包含本地工具源码/构建树和 analyzer 依赖。
- `Paper/`、`paper.md` 和 `experiment.md` 包含论文笔记与方法论。

## 证据标准

对于每一个候选 case，保留最小证据包：

- target、tool、run directory、universe、精确的输入 `.bc`/`.ll`，以及 command line；
- 可用时，记录 raw log 路径和规范化的 CSV/JSON 行；
- status label：reported、verified/no-error、found-error、timeout、too-complex、translation failure、backend failure 或 tool failure；
- O0 vs O2 vs O2-noinline 对比；
- 可用时，记录相关 source snippet 和 IR snippet；
- 可疑根因：inline、Phi-node merge、SROA struct split、CFG simplification、DCE、DWARF location drift、state explosion 或 other。

使用来自日志、CSV summary、`.bc`/`.ll` artifact 和 final report 的证据。只要本地 artifact 存在，就不要依赖记忆。

## Case 标签

解释 finding 时使用一致的标签：

- `TP`：true positive。
- `FP-TypeMismatch`：报告的 bug 类型与代码/IR 位置不匹配。
- `FP-PathInfeasible`：报告路径不可行。
- `FP-LocationDrift`：行号/函数归因漂移，通常由 inline 和 DWARF mapping 引起。
- `FN-O2`：在 O0 中可见，但在 O2 中缺失。
- `Timeout/TooComplex`：分析退化，而不是语义判定。
- `Unknown`：证据不足。

只有当 `O2-noinline` 完全或部分恢复结果时，才优先将现象归因于 inline。

## 编辑规则

- 除非用户明确要求，否则不要删除或覆盖现有实验结果、日志、summary、report、bitcode 或生成 artifact。
- 如果添加新的 run，应写入新的带时间戳目录或命名清晰的目录。
- 保持修改范围狭窄，并保留可复现性。
- 对于脚本，应记录关键命令、镜像名、输入 bitcode 路径、输出目录、返回码和环境检查。
- 除非正在编辑中文笔记或论文正文，否则新的基础设施文件使用 ASCII。

## 验证偏好

- 搜索时优先使用 `rg`/`rg --files`。
- 可用时优先使用现有项目脚本。
- 基于 Docker 的 analyzer run 可能耗时且代价较高；启动大型矩阵 run 前，应确认 target、输入 bitcode、universe、tool 和输出目录。
- 编辑 shell 脚本后，可行时运行 `bash -n <script>`。
- 修改 CSV 或 report 文件时，验证表头和代表性行。

## 沟通

- 当用户用中文提问时，用中文回复，除非用户另有要求。
- 明确说明所检查或修改的 target、tool、run directory 和 compilation universe。
- 如果结果因 timeout、translation failure、backend failure、缺少 Docker image 或依赖不可用而不完整，应直接说明。
