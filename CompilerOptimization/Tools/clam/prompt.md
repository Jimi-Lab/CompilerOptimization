# Clam Docker 深度扫描目标 LLVM bitcode 的执行提示

本提示用于让 Codex 使用本地 Docker 镜像 `seahorn/clam-llvm14:nightly` 对用户指定的程序级 LLVM bitcode (`.bc`) 执行 Clam 深度扫描，并把完整命令、日志、状态、结果和后续筛选线索整理为可复现实验证据。

本工作区实验背景遵循 `/home/jimi/PaperExperiment/AGENTS.md`：主实验只研究 IR/bitcode 层工具，Clam 输入必须是已有的 `clang -O0 -g`、`clang -O2 -g` 或 `clang -O2 -g -fno-inline` bitcode。不要引入 source-level 工具，不要向主实验添加 `-DNDEBUG`，不要把 CMake `RelWithDebInfo` 直接等同于论文的 O2 宇宙。

## 输入输出路径

```bash
# 必填：待扫描的程序级 LLVM bitcode，必须是绝对路径，后缀通常为 .bc 或 .ll。
INPUT_BC_HOST="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc"

# 必填：所有 Clam 输出写入的根目录，必须是绝对路径。
# Codex 会在该目录下创建一个新的 run_<YYYYMMDD_HHMMSS>/ 子目录。
# 不要填写已有重要结果目录作为最终 run 目录；这里应填写本次扫描专用输出根目录。
OUTPUT_ROOT_HOST="/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/clam/LLVM14-O2-g"

# 必填：target 名称，用于报告和 TSV 字段，例如 redis、zlib、cJSON、rapidjson。
TARGET="<target>"

# 必填：编译宇宙，只能填写 O0、O2、O2-noinline 或 unknown。
UNIVERSE="<O2>"
```

推荐输出路径示例：

```bash
OUTPUT_ROOT_HOST="/home/jimi/PaperExperiment/CompilerOptimization/Result/redis/clam/clam-O2-g"
```

## 0. 必须先向用户确认的信息

如果用户没有明确给出待扫描 bitcode 或输出路径，必须先停止并询问：

```text
请同时提供：
1. 待扫描的程序级 LLVM bitcode 绝对路径 INPUT_BC_HOST，例如：
   /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/<target>/LLVM14-O2-g/artifacts/<program>_O2_g.bc
2. Clam 输出根目录 OUTPUT_ROOT_HOST，例如：
   /home/jimi/PaperExperiment/CompilerOptimization/Result/<target>/clam/clam-O2-g
3. TARGET 和 UNIVERSE。
```

如果用户只给出目录，必须在目录中用 `find`/`rg --files` 找出候选 `.bc`/`.ll`，让用户确认具体扫描哪个文件。不要擅自对整个大型目录启动矩阵扫描。

必须从 bitcode 路径或用户说明中记录以下字段：

- `target`: 例如 `redis`、`zlib`、`cJSON`。
- `universe`: `O0`、`O2` 或 `O2-noinline`。如果路径无法判断，标记为 `unknown` 并要求用户确认。
- `input_bc`: 用户指定的绝对路径。
- `output_root`: 用户指定的绝对路径。
- `run_dir`: 在 `output_root` 下新建的 `run_<YYYYMMDD_HHMMSS>` 目录。
- `tool`: 固定为 `Clam`。
- `docker_image`: 固定为 `seahorn/clam-llvm14:nightly`。

路径合法性约束：

- `INPUT_BC_HOST` 必须存在且是普通文件。
- `INPUT_BC_HOST` 必须位于 `/home/jimi/PaperExperiment` 下，否则 Docker 映射模板不适用，必须先请用户确认新的挂载方案。
- `OUTPUT_ROOT_HOST` 必须是绝对路径，且必须位于 `/home/jimi/PaperExperiment` 下。
- Codex 可以创建 `OUTPUT_ROOT_HOST`，但不能删除或覆盖其中已有内容。
- 最终 `RUN_DIR="$OUTPUT_ROOT_HOST/run_<YYYYMMDD_HHMMSS>"` 必须是新目录。如果碰撞，重新生成时间戳或追加后缀。

## 1. 已核实的 Clam/Docker 事实

以下内容来自本地源码和实际 Docker 探针，不要凭记忆改写：

- Clam 源码路径：`/home/jimi/PaperExperiment/CompilerOptimization/Tools/clam/clam-src/clam`
- Docker 镜像：`seahorn/clam-llvm14:nightly`
- 镜像内可执行文件：
  - `/clam/build/run/bin/clam`
  - `/clam/build/run/bin/clam.py`
  - `/clam/build/run/bin/clam-pp`
  - `/clam/build/run/bin/seaopt`
- 当前环境中直接运行 `clam.py` 会在 `os.setpgrp()` 处触发 `PermissionError`；因此主流程使用底层二进制 `clam`，不要依赖 `clam.py`。
- `clam --help` 显示底层二进制支持 `--crab-check`、`--crab-null-check`、`--crab-uaf-check`、`--crab-bounds-check`、`--crab-track`、`--crab-heap-analysis`、`--crab-inter`、`--crab-dom`、`--crab-check-verbose`、`--ocrab`、`--ojson`、`--oll` 等参数。
- 镜像中的 Crab 配置包含 `HAVE_APRON TRUE`，但未启用 `HAVE_LDD`、`HAVE_PPLITE`、`HAVE_ELINA`。因此：
  - 可使用：`int`、`zones`、`soct`、`oct`、`pk`、`w-int`、`ric` 等。
  - 不建议作为主矩阵使用：`boxes`、`pk-pplite`。
- 该镜像生成 JSON 时可能打印 `Warning: too old version of boost. It needs >= 1.80 for json support`，并产生空 JSON。主证据必须以 raw log 为准，JSON 只作为可选产物记录。
- Clam 报告位置来自 LLVM instruction 的 `DebugLoc`。源码中 `CfgBuilderUtils.cc` 直接取 `dloc.getLine()`、`dloc.getCol()`、`getFilename()`；没有针对 `DILocation::getInlinedAt()` 做 inline call stack 恢复。这正适合筛选 `FP-LocationDrift` / 行号漂移 case。

## 2. 输出目录规范

所有 Clam run 必须写入用户显式指定的 `OUTPUT_ROOT_HOST` 下的新时间戳目录，不能覆盖已有结果。

目录模板：

```text
<OUTPUT_ROOT_HOST>/run_<YYYYMMDD_HHMMSS>/
```

其中 `OUTPUT_ROOT_HOST` 必须由用户显式填写。推荐 `run_label`：

- `clam-O0-g`
- `clam-O2-g`
- `clam-O2-g-noinline`
- 如果 universe 未知：`clam-unknown`

每次 run 创建以下子目录：

```text
artifacts/
log/
status/
report/
commands/
extract/
```

必须生成这些文件：

```text
commands/commands.log          # 每条实际运行命令，含时间、checker、domain、返回码
status/run_status.tsv          # 每个配置的状态汇总
extract/warnings.tsv           # 从 raw log 抽取的 warning/error/check summary
report/final_report.md         # 本次扫描的总报告
```

每个 checker/domain 单独保存：

```text
log/<checker>_<domain>.log
status/<checker>_<domain>.status
artifacts/<checker>_<domain>.ll
artifacts/<checker>_<domain>.crabir
artifacts/<checker>_<domain>.json
```

即使 `.json` 为空，也保留文件并在 report 中说明 Boost 版本限制导致 JSON 不可靠。

## 3. 运行前检查

在启动扫描前必须执行并记录：

```bash
date -Is
test -f "$INPUT_BC"
ls -lh "$INPUT_BC"
docker image ls seahorn/clam-llvm14
docker run --rm --entrypoint /bin/bash seahorn/clam-llvm14:nightly -lc 'command -v clam && clam --version'
```

如果输入是 `.bc`，建议额外检查 LLVM 14 是否能读：

```bash
docker run --rm \
  -v /home/jimi/PaperExperiment:/work \
  -w /work \
  --entrypoint /bin/bash \
  seahorn/clam-llvm14:nightly -lc '
llvm-dis-14 "$INPUT_IN_CONTAINER" -o /tmp/clam_input_check.ll &&
llvm-nm-14 "$INPUT_IN_CONTAINER" | sed -n "1,40p"
'
```

注意：`INPUT_IN_CONTAINER` 是把宿主机 `/home/jimi/PaperExperiment/...` 映射到容器 `/work/...` 后的路径。通常转换规则是：

```text
宿主机: /home/jimi/PaperExperiment/CompilerOptimization/...
容器内: /work/CompilerOptimization/...
```

如果 `llvm-dis-14` 失败，状态标记为 `translation failure` 或 `tool failure`，不要继续跑矩阵。

## 4. 主扫描矩阵

Clam 一次只能启用一种主要 checker，因此要分开跑。主矩阵：

```text
checkers:
  null    -> --crab-null-check
  uaf     -> --crab-uaf-check --crab-dom-param=region.deallocation=true
  bounds  -> --crab-bounds-check

domains:
  zones   # 默认关系域，主配置
  soct    # split octagon，较强
  oct     # Apron octagon，镜像支持
  pk      # Apron polyhedra，最重，可能慢
  int     # intervals，粗糙但可能产生更多 warning
  w-int   # wrapped intervals
  ric     # intervals + congruences
```

默认深度参数：

```text
--crab-track=mem
--crab-heap-analysis=cs-sea-dsa
--sea-dsa-type-aware=true
--sea-dsa-devirt
--crab-inter
--crab-inter-recursive
--crab-inter-exact-summary-reuse
--crab-widening-delay=2
--crab-narrowing-iterations=3
--crab-widening-jump-set=20
--crab-check-verbose=2
--crab-print-invariants=none
--crab-stats
--crab-enable-warnings=true
```

说明：

- `--crab-track=mem` 启用内存对象跟踪，是 null/uaf/bounds 更有意义的配置。
- `--crab-heap-analysis=cs-sea-dsa` 使用 context-sensitive SeaDsa。
- `--sea-dsa-type-aware=true` 启用 type-aware SeaDsa。
- `--sea-dsa-devirt` 让 SeaDsa 构建更完整 call graph，适合含 indirect calls 的程序。
- `--crab-inter` 启用 summary-based inter-procedural analysis。
- `--crab-check-verbose=2` 打印 error + warning checks；这是大量 report bugs 的主设置。若需要 safe checks，可单独补跑 `--crab-check-verbose=3`，但日志会显著膨胀。
- 不要在主实验里加 `--inline` 或 `clam-pp --clam-inline-all`，否则会混入 Clam 自己的 inline，污染 `clang -O2 -g` inline 归因。

## 5. 单个配置的 Docker 命令模板

以下模板必须落盘到 `commands/commands.log`，并将 stdout/stderr 全量保存到 `log/<checker>_<domain>.log`。

```bash
docker run --rm \
  -v /home/jimi/PaperExperiment:/work \
  -w /work \
  --entrypoint /bin/bash \
  seahorn/clam-llvm14:nightly -lc '
set -o pipefail
clam "<INPUT_IN_CONTAINER>" \
  --crab-check \
  <CHECKER_OPTION> \
  --crab-track=mem \
  --crab-heap-analysis=cs-sea-dsa \
  --sea-dsa-type-aware=true \
  --sea-dsa-devirt \
  --crab-inter \
  --crab-inter-recursive \
  --crab-inter-exact-summary-reuse \
  --crab-dom=<DOMAIN> \
  --crab-widening-delay=2 \
  --crab-narrowing-iterations=3 \
  --crab-widening-jump-set=20 \
  --crab-check-verbose=2 \
  --crab-print-invariants=none \
  --crab-stats \
  --crab-enable-warnings=true \
  --oll="<OUT_LL_IN_CONTAINER>" \
  --ocrab="<OUT_CRABIR_IN_CONTAINER>" \
  --ojson="<OUT_JSON_IN_CONTAINER>"
'
```

`<CHECKER_OPTION>` 取值：

```text
null:
  --crab-null-check

uaf:
  --crab-uaf-check --crab-dom-param=region.deallocation=true

bounds:
  --crab-bounds-check
```

建议用外层 `timeout` 控制每个配置，避免大型 bitcode 卡死。默认先用 1800 秒；`pk` 可放宽到 3600 秒。

```bash
timeout -s KILL -k 10 1800 docker run ...
```

如果 timeout 发生，状态标记为 `timeout`，保留已有日志，不要删除中间产物。

## 6. 推荐批量执行伪代码

Codex 实际执行时应把下面逻辑转换成 shell 脚本或逐条命令。不要用会覆盖已有 run 的固定目录。

```bash
# 这些变量必须来自用户显式填写的代码块，不得自动猜测。
INPUT_BC_HOST="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/<target>/<universe>/artifacts/<program>.bc"
OUTPUT_ROOT_HOST="/home/jimi/PaperExperiment/CompilerOptimization/Result/<target>/clam/<run_label>"
TARGET="<target>"
UNIVERSE="<O0|O2|O2-noinline|unknown>"

test -f "$INPUT_BC_HOST"
case "$INPUT_BC_HOST" in /home/jimi/PaperExperiment/*) ;; *) echo "INPUT_BC_HOST outside workspace"; exit 2 ;; esac
case "$OUTPUT_ROOT_HOST" in /home/jimi/PaperExperiment/*) ;; *) echo "OUTPUT_ROOT_HOST outside workspace"; exit 2 ;; esac

RUN_TS="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${OUTPUT_ROOT_HOST}/run_${RUN_TS}"

mkdir -p "$RUN_DIR"/{artifacts,log,status,report,commands,extract}

INPUT_BC_CONT="${INPUT_BC_HOST#/home/jimi/PaperExperiment/}"
INPUT_BC_CONT="/work/${INPUT_BC_CONT}"

for CHECKER in null uaf bounds; do
  for DOMAIN in zones soct oct pk int w-int ric; do
    # build CHECKER_OPTION
    # build output file paths under RUN_DIR
    # run docker command with timeout
    # append command, start time, end time, return code to commands/commands.log
    # write one line to status/run_status.tsv
  done
done
```

`status/run_status.tsv` 表头必须是：

```text
target	universe	checker	domain	status	return_code	input_bc	log_path	ll_path	crabir_path	json_path	start_time	end_time	elapsed_sec
```

状态标签只能使用：

```text
reported
verified/no-error
found-error
timeout
too-complex
translation failure
backend failure
tool failure
```

判定建议：

- 日志含 `Number of total warning checks` 且 warning 数大于 0：`reported`
- 日志含 `Number of total error checks` 且 error 数大于 0：`found-error`
- 日志含完整 `ANALYSIS RESULTS` 且 warning/error 都为 0：`verified/no-error`
- 命令被外层 timeout 杀死：`timeout`
- Clam 前端/LLVM 读入失败、bitcode 不兼容：`translation failure`
- Clam/Crab 崩溃、segfault、assertion failure：`tool failure`
- solver/domain 内部失败或后端不可用：`backend failure`

## 7. 从日志抽取 warning

Clam verbose warning 形态通常如下：

```text
--- WARNING -----------------
loc(file=sds.h line=108 col=35) id=179
Property : assert(_24 > NULL_REF)   /* loc(file=sds.h line=108 col=35) id=179 */
Invariant: ...
-----------------------------
```

必须从所有 `log/*.log` 中抽取到 `extract/warnings.tsv`。表头：

```text
target	universe	checker	domain	kind	file	line	col	id	property	log_path
```

抽取规则：

- `kind`: `WARNING` 或 `ERROR`
- `file,line,col,id`: 来自 `loc(file=... line=... col=...) id=...`
- `property`: 来自下一行 `Property : ...`
- `log_path`: 原始日志路径

如果日志只包含 summary 而没有逐条 `loc(...)`，也要在 `extract/warnings.tsv` 里写一条 summary 行，并在 `report/final_report.md` 说明 `--crab-check-verbose` 输出不足或工具提前失败。

## 8. 结果报告必须包含的内容

扫描结束后，必须写 `report/final_report.md`。报告至少包含：

```markdown
# Clam Scan Final Report

## Metadata
- target:
- universe:
- input_bc:
- docker_image:
- run_dir:
- start_time:
- end_time:

## Environment Checks
- docker image:
- clam path/version:
- llvm-dis/llvm-nm check:

## Command Matrix
| checker | domain | status | return_code | warning | error | safe | log |

## High-Volume Warning Hotspots
| file | line | checker | domain | warning_count | example_property |

## Candidate Location-Drift Leads
| file | line | checker | domain | reason |

## Notes
- JSON reliability:
- timeout/tool failure/backend failure:
- important Clam limitations:

## Reproducibility
- commands log:
- raw logs:
- status TSV:
- warnings TSV:
```

候选 `FP-LocationDrift` 线索优先筛选：

- warning 落在 `.h`、`inline` helper、宏定义附近，但实际业务调用点可能在 `.c/.cc`。
- `line=0 col=0`。
- 同一头文件行在多个函数/多个 domain/checker 中重复爆炸。
- `Property` 指向 null/uaf/bounds，但源码该行只是 helper、结构体字段访问、宏展开、普通 accessor。
- O2 有大量 warning，O0 同配置没有或明显更少。
- 若后续 `O2-noinline` 完全或部分恢复，才优先归因 inline。

## 9. 对比 O0/O2/O2-noinline 的要求

如果用户提供多个 universe 的 bitcode，必须用完全相同的 checker/domain 矩阵分别扫描，并额外生成差分报告：

```text
report/diff_O0_vs_O2.md
report/diff_O2_vs_O2_noinline.md
extract/diff_warnings.tsv
```

差分字段：

```text
target	checker	domain	file	line	col	property	O0_status	O2_status	O2_noinline_status	label
```

标签建议：

- `FP-LocationDrift`: O2 报告位置明显漂移，源码上下文与属性不匹配。
- `FN-O2`: O0 中有可解释告警/路径，O2 消失。
- `Timeout/TooComplex`: O2 或某 domain 超时/状态爆炸。
- `Unknown`: 证据不足。

## 10. 明确不要做的事

- 不要删除或覆盖既有实验结果、日志、summary、report、bitcode。
- 不要在主实验扫描中加入 Clam wrapper 的 `--inline`。
- 不要让 `clam.py` 对已有 `.bc` 再跑 `-O2` 优化；当前主流程直接使用底层 `clam`。
- 不要把 JSON 当主证据；当前镜像 Boost 版本可能导致 JSON 空文件。
- 不要把单个 Clam warning 直接写成优化导致。必须通过 O0/O2/O2-noinline 对比或源码/IR 证据确认。
- 不要把 `CodeQL`、`Joern`、`Infer`、`Semgrep`、`Cppcheck` 等 source-level/front-end 工具引入主实验矩阵。

## 11. 给用户的最终回复格式

执行完成后，用中文简短说明：

- 检查/扫描的 target、universe、input bitcode。
- Clam Docker image 和 run directory。
- 总共跑了多少个 checker/domain 配置，多少成功、多少 timeout/tool failure。
- warning/error/safe 的总体规模。
- `report/final_report.md`、`extract/warnings.tsv`、`commands/commands.log`、`status/run_status.tsv` 路径。
- 如果发现明显 location drift 热点，列出前 3-5 个文件行号。

如果运行不完整，必须明确说明原因：timeout、translation failure、backend failure、tool failure、Docker image 缺失或 bitcode/LLVM 版本不兼容。
