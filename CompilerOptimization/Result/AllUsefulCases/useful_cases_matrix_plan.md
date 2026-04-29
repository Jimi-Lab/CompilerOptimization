# O2-g Useful Cases 矩阵收集计划

## 1. 范围

本目录用于收集和汇总已经完成的 `clang -O2 -g` / `LLVM14-O2-g` bitcode 分析结果中的 useful cases。

重要边界：

- 顶层矩阵只负责收集、整理和汇总。
- 顶层矩阵不负责对所有工具的原始输出做深度解析。
- 每个工具必须先在自己的目录下生成高精度的标准化 case 集合：

```text
CompilerOptimization/Result/AllUsefulCases/phasar/
CompilerOptimization/Result/AllUsefulCases/seahorn/
CompilerOptimization/Result/AllUsefulCases/smack/
CompilerOptimization/Result/AllUsefulCases/dg/
CompilerOptimization/Result/AllUsefulCases/ikos/
CompilerOptimization/Result/AllUsefulCases/cclyzer++/
CompilerOptimization/Result/AllUsefulCases/yapall/
```

顶层矩阵只读取这些工具级标准化文件，再生成跨工具汇总表。这样做是必要的，因为每个 analyzer 对位置、warning、fact、mode 和 failure 的表达方式都不一样。如果用一个全局 parser 粗暴处理所有工具，会遗漏大量真正有价值的 cases，也容易误判。

本轮只纳入 `O2-g` / `LLVM14-O2-g` 结果。`O0`、`O2-noinline`、`RelWithDebInfo`、source-level tools 和 SCA tools 不进入本矩阵，除非之后明确扩展范围。

工具集合严格限定为：

```text
phasar, seahorn, smack, dg, ikos, cclyzer++, yapall
```

## 2. 已经确定的用户口径

以下口径已经由当前任务确定，脚本和后续分析不能另行猜测：

1. 用户会按工具指定要分析哪些已经产生结果的 repo / run。
   收集过程不应自动从全部历史目录里决定最终 target 集合。

2. 工具集合严格等于：
   `phasar`、`seahorn`、`smack`、`dg`、`ikos`、`cclyzer++`、`yapall`。

3. `P0/P1/P2` 是论文证据优先级，不是工具报告 bug 的严重等级。

4. 扫描结果目录由用户指定。
   discovery 脚本可以辅助检查候选目录，但最终纳入必须来自用户指定 run list，或来自已经检查过的 manifest。

5. 头文件位置必须谨慎处理。
   工具 report 到 header 并不自动说明它错了。它可能来自 inline/template code、macro expansion 或库代码。必须通过 `source_region`、`project_source_only`、`header_context`、`location_validity` 等字段单独分类。

6. 人工验证放到后续阶段。
   因此 P0 必须限制为已经具有高置信度、可以直接进入论文证据的 cases，而且这种置信度必须来自客观证据。

## 3. 输出布局

顶层输出：

```text
CompilerOptimization/Result/AllUsefulCases/useful_cases_matrix.csv
CompilerOptimization/Result/AllUsefulCases/useful_cases_inventory.csv
CompilerOptimization/Result/AllUsefulCases/tool_native_output_profile.csv
CompilerOptimization/Result/AllUsefulCases/run_selection_manifest.csv
CompilerOptimization/Result/AllUsefulCases/final_matrix_report.md
```

工具级输出：

```text
CompilerOptimization/Result/AllUsefulCases/<tool>/tool_cases.csv
CompilerOptimization/Result/AllUsefulCases/<tool>/tool_runs.csv
CompilerOptimization/Result/AllUsefulCases/<tool>/native_output_profile.md
CompilerOptimization/Result/AllUsefulCases/<tool>/case_collection_report.md
CompilerOptimization/Result/AllUsefulCases/<tool>/evidence/
```

建议的顶层脚本：

```text
CompilerOptimization/Result/AllUsefulCases/scripts/merge_tool_cases_matrix.py
```

建议的工具级脚本：

```text
CompilerOptimization/Result/AllUsefulCases/<tool>/scripts/collect_<tool>_cases.py
```

顶层脚本不应该深入解析每一种 analyzer 原始格式。它只应该合并各工具目录中已经生成的标准化 `tool_cases.csv`。

## 4. 整体工作流

1. 对每个工具，由用户指定需要分析的具体结果目录。

2. 工具专用 collector 读取该工具的原生输出，并写出：
   - `<tool>/tool_cases.csv`
   - `<tool>/tool_runs.csv`
   - `<tool>/native_output_profile.md`
   - `<tool>/case_collection_report.md`

3. 顶层 merger 读取七个工具级 `tool_cases.csv`。

4. 顶层矩阵按 `target x tool` 聚合 P0/P1/P2 计数。

5. 最终报告解释：
   - 纳入了哪些结果目录；
   - 哪些 mode 成功、部分成功或失败；
   - 找到了多少 P0/P1/P2 cases；
   - 哪些工具能直接输出源码位置；
   - 哪些工具需要 IR/debug metadata 重映射；
   - 哪些 cases 已经可以直接用于论文，哪些进入后续人工验证队列。

## 5. 修订后的 P0/P1/P2 优先级方案

优先级方案必须可实现、可审计。它不能承诺脚本无法可靠完成的自动语义判断。

### 5.1 P0：可直接用于论文的高置信证据

P0 只保留这样的 cases：工具报告的源码位置客观无效，或明显不可信，并且有足够证据可以直接进入论文。

一个 case 进入 P0，必须同时满足以下基础条件：

- 来自用户指定的 `O2-g` 结果目录。
- 有 raw analyzer artifact 路径、run directory、command 或 run manifest，以及可用时的输入 `.bc` / `.ll` 路径。
- analyzer 报告了具体位置，或者工具级 collector 能从 fact / IR / debug metadata 中恢复出具体位置。
- 优先级原因是机器可检查的，或者从很小的 evidence snippet 中一眼可见。

P0 示例：

- `LineOutOfRange`：工具报告的 source line 大于该文件总行数。
- `LineZero`：工具报告到某个 source file 的第 0 行。C/C++ 源码行号正常应为 1-based，因此 `line=0` 不是有效源码行；若某工具明确用 `0` 表示 unknown/no-location，也应记录为无有效源码行。
- `ColumnOutOfRange`：工具报告的 column 超过该行长度，无法指向真实 token。
- `MissingSourceFile`：工具报告的 source file 在预期 source root 或已知 remap root 下找不到，而该 run 的其他 source mapping 是有效的。
- `NoDebugLocButReportedSource`：工具报告或暗示了源码位置，但锚定的 IR instruction 没有 debug location。
- `SourceLineEmptyOrNonCode`：报告位置指向空行、纯注释行或纯预处理行，但 warning 声称那里发生了 load/free/use/assertion 等可执行操作。
- `SourceTextMismatch`：工具原生 report 同时给出 source line 和 source text，但按 source-root/build-root/container-root/debug-remap-root 解析到的实际源码行文本与 report 中的 source text 不一致。这是客观 source-location mismatch，应归为 P0，而不是需要语义判断的 P1。
- `WrongFileByDebugRemap`：工具/fact anchor 通过 LLVM debug metadata 映射到一个 source file，但工具报告的是另一个 project file，且 mismatch 可以直接展示。
- 已有工具专用 `ValueCases` 用 raw row、IR snippet 和 source snippet 证明了上述某一类问题。

`MissingSourceFile` 的判定必须收紧：如果 report 的文件不在当前 repo 中，但它其实可能是 system header、第三方库、build 目录生成文件、旧编译路径、容器内路径或 debug remap 前路径，那么不能立刻算 P0。必须先尝试 source-root、build-root、container-root 和 debug-remap-root 解析；只有仍然找不到合理对应文件，才可以判为 `MissingSourceFile` / P0。

与头文件相关的 P0 只能在存在客观无效证据时成立：

- header file 不存在；
- 行号越界；
- 列号越界；
- report 给出的 source text 与解析到的 header 实际行文本不一致；
- 位置指向 declaration/comment/preprocessor line，但 report 声称那里发生了具体运行时操作；
- inline/template expansion 证据指向另一个具体 executable site，而报告的 header 位置可以证明只是 attribution artifact。

仅仅因为位置在 header 中，不能把它判为 P0。

### 5.2 P1：强候选，但需要语义检查

P1 用于这样的 cases：工具报告的 source line/column 在源码中确实存在，但 report 看起来语义上不对或可疑，需要进一步读源码/IR 后才能升级为论文级证据。

P1 示例：

- 工具报告 UAF / double free / double use，但报告的源码行中肉眼看不到对应操作。
- 该行存在且包含代码，但 warning kind 和局部源码操作不匹配。
- 报告位置在看似合理的 header/template/macro 位置，但不检查 inline stack 或 macro expansion 还不能判断 attribution 是否正确。
- report 有有效 source line，但 IR anchor 指向不同函数或不同 source context。
- 工具在优化后的 merged IR value 上报告问题，多个 source variables 可能已经坍缩。
- case 来自 cclyzer++ / yapall / SeaHorn / SMACK / DG / Phasar / IKOS，且有 raw evidence，但还需要人工判断它到底是 debug-location drift、semantic mismatch、false positive，还是 analyzer 的正常行为。

P1 必须保留足够证据，方便后续人工升级：

- raw artifact path；
- message / fact row；
- source snippet；
- 可用时的 IR snippet；
- suspected mismatch reason；
- location 属于 project source、project header、third-party header、system header、generated source 还是 unknown。

### 5.3 P2：弱证据、间接证据或 run-level 证据

P2 可以用于覆盖率统计和附录级论证，但它本身不能直接作为论文正文 case。

P2 示例：

- timeout、too-complex、translation failure、backend failure、import failure、unsupported IR 或 mode failure，但没有具体 source/IR case。
- 工具输出只有 summary count 或 status，没有具体 row/log line。
- 位置有效，目前看不出 mismatch，但经过更深的工具专用分析后可能仍有价值。
- 工具产生了 partial results，但成功 mode 还没有提供 case-level evidence。
- system-header 或 library-header 位置没有客观无效证据，且尚未完成语义分析。
- 为了展示多工具一致性或重复行为而保留的 duplicates。

### 5.4 不进入 useful cases 的内容

以下内容不进入 useful cases：

- 非 `O2-g` 结果。
- source-level / front-end 工具输出。
- 只有 build log、没有 analyzer 输出。
- 没有 run directory 和 raw evidence 的孤立数字。
- 位置有效，且当前没有 mismatch、degradation 或论文相关现象的结果。
- 重复 case，除非这个重复本身用于支撑跨工具或跨 mode 结论。

## 6. 工具级标准化 case schema

每个工具级 collector 都应该输出 `tool_cases.csv`，schema 如下：

```csv
case_uid,target,tool,priority,priority_reason,case_kind,status_label,run_dir,run_id,mode,input_bc,input_ll,raw_artifact,raw_row_or_line,reported_file,reported_line,reported_column,location_validity,source_region,project_source_only,header_context,ir_function,ir_instruction,ir_line,ir_snippet,source_snippet,message,root_cause_hint,confidence,needs_manual_review,manual_verdict,evidence_files,notes
```

字段说明：

- `priority`：只能是 `P0`、`P1`、`P2`。
- `priority_reason`：简短的机器可读原因，例如 `LineOutOfRange`、`ColumnOutOfRange`、`SourceTextMismatch`、`WarningKindSourceMismatch`、`RunTimeoutOnly`。
- `case_kind`：标准化现象类型，例如 `LocationInvalid`、`LocationDrift`、`WarningKindMismatch`、`IRSourceMismatch`、`RunDegradation`、`NoDebugLoc`、`AliasCollapseCandidate`。
- `status_label`：analyzer 状态，例如 `reported`、`found-error`、`verified/no-error`、`timeout`、`too-complex`、`translation failure`、`backend failure`、`tool failure`。
- `location_validity`：`valid`、`line_zero`、`line_out_of_range`、`column_out_of_range`、`missing_file`、`empty_or_comment_line`、`preprocessor_only`、`no_debug_loc`、`unknown`。
- `source_region`：`project_source`、`project_header`、`third_party_source`、`third_party_header`、`system_header`、`generated_source`、`llvm_ir_only`、`unknown`。
- `project_source_only`：只有当位置属于 target 自己的源码，而不是 system 或 third-party code 时才为 `1`。
- `header_context`：`not_header`、`project_header`、`third_party_header`、`system_header`、`unknown`。
- `needs_manual_review`：P0 通常应为 `0`；P1 通常应为 `1`；P2 取决于具体原因。

## 7. 工具级标准化 run schema

每个工具级 collector 都应该输出 `tool_runs.csv`：

```csv
target,tool,selected,run_dir,run_id,universe,input_bc,input_ll,mode,status,success_modes,failed_modes,timeout_modes,raw_artifacts,reason,excluded_reason,notes
```

用户指定的 run directory 必须记录在这里。如果辅助 discovery 找到了额外 runs，在用户确认前应标记为 `selected=0`。

## 8. 矩阵 CSV schema

顶层 `useful_cases_matrix.csv`：

```csv
target,phasar,seahorn,smack,dg,ikos,cclyzerpp,yapall,total_P0,total_P1,total_P2,notes
```

每个工具单元格格式：

```text
P0=<n>;P1=<n>;P2=<n>;status=<ok|partial|timeout|failure|missing|no_case>;runs=<k>;modes=<summary>
```

示例：

```text
P0=3;P1=14;P2=2;status=partial;runs=1;modes=ok:subset,timeout:full
P0=0;P1=0;P2=0;status=missing;runs=0;modes=
```

顶层 `useful_cases_inventory.csv` 是所有被选中的工具级 `tool_cases.csv` 的拼接结果，必要时可以追加顶层字段。

## 9. 各工具原生输出收集职责

### 9.1 cclyzer++

工具级目录：

```text
CompilerOptimization/Result/AllUsefulCases/cclyzer++/
```

预期原生输入：

```text
CompilerOptimization/Result/<target>/cclyzerpp/LLVM14-O2-g/<run>/ValueCases/all_cases.csv
relation/*.csv.gz
input .bc
input .ll
```

职责：

- 有现成 `ValueCases/all_cases.csv` 时优先使用。
- 保留 relation rows、IR snippets、source snippets 和 debug mapping evidence。
- 使用本文修订后的优先级方案重新分类，而不是盲目信任旧策略下的 P0/P1/P2。
- P0 主要应该是客观 invalid-location 或已经证明的 source/IR mismatch cases。

### 9.2 yapall

工具级目录：

```text
CompilerOptimization/Result/AllUsefulCases/yapall/
```

预期原生输入：

```text
CompilerOptimization/Result/<target>/yapall/LLVM14-O2-g/<run>/ValueCases/*_yapall_value_cases.csv
report/final_report.md
commands/commands.log
```

职责：

- 有 ValueCases 时优先使用。
- 区分“有足够 source/IR evidence 的 case”和“只是 analyzer raw warning 的 issue”。
- `tool_output_insufficient` 或 low-confidence rows 默认归为 P2，除非存在客观 invalid location。
- 即使部分 mode 失败，也要保留成功 mode 产生的 useful cases。

### 9.3 SeaHorn

工具级目录：

```text
CompilerOptimization/Result/AllUsefulCases/seahorn/
```

预期原生输入：

```text
summary/all_cases.csv
summary/smc_cases.csv
summary/failure_inventory.csv
summary/horn_status.csv
report/final_report.md
log/exit_codes.csv
```

职责：

- 提取原生输出中直接给出的 source file / line / column warnings。
- 校验 report file / line / column 是否能对应到 source roots。
- 只有当位置客观无效，或 source/IR mismatch 已经有直接证据时，才进入 P0。
- 语义 warning mismatch，例如 warning kind 与可见源码操作不匹配，先进入 P1，等待后续人工验证。
- 只有 timeout / failure、没有具体 case 的 mode 进入 P2。

### 9.4 SMACK

工具级目录：

```text
CompilerOptimization/Result/AllUsefulCases/smack/
```

预期原生输入：

```text
summary/smack_status.csv
summary/failure_inventory.csv
summary/approximation_warnings.csv
report/final_report.md
report/all_reported_errors.md
log/exit_codes.csv
```

职责：

- 提取具体 verifier errors 和 report 的 source locations。
- translation / backend failures 只有在包含具体 useful source/IR case 时才升级；否则归为 P2。
- approximation warnings 视其是否能绑定到 source/IR，归为 P1 或 P2。
- 不要因为 verifier 报 error 就自动升为 P0；P0 必须有客观位置无效或直接 mismatch 证据。

### 9.5 DG

工具级目录：

```text
CompilerOptimization/Result/AllUsefulCases/dg/
```

预期原生输入：

```text
high_precision_*/report.md
summary/steps.csv
summary/failures.csv
summary/line_hits.csv
summary/warnings.csv
commands.log
```

职责：

- 按 mode 收集 line hits 和 warnings。
- 保留 mode-level status，因为 DG 可能某些 mode 失败、另一些 mode 产生有用输出。
- line hits 通常先归为 P1，除非存在客观 invalid-location 证据。
- unsupported / timeout / failure-only evidence 归为 P2。

### 9.6 Phasar

工具级目录：

```text
CompilerOptimization/Result/AllUsefulCases/phasar/
```

预期原生输入：

```text
log/summary.csv
runs/ifds-uninit/target_linecheck.csv
log/ifds-uninit.stdout.log
log/ifds-uninit.stderr.log
log/commands.log
```

职责：

- 如果存在具体 source locations，使用 `target_linecheck.csv` 或 parser-specific rows。
- `ok` 但没有具体 finding 时标为 `no_case`，不是 P2。
- timeout / failure 且没有 source case 时归为 P2。
- `phasar_O2_RelWithDebInfo` 不得直接纳入，除非 command 能证明其真实输入是 `clang -O2 -g` bitcode。

### 9.7 IKOS

工具级目录：

```text
CompilerOptimization/Result/AllUsefulCases/ikos/
```

预期原生输入需要先根据用户指定的结果目录做 discovery。

职责：

- 先在 `ikos/native_output_profile.md` 中记录实际 IKOS 输出 schema。
- 可用时提取 alarm rows，包括 check kind、status 和 source location。
- 使用同一套客观 P0 规则。
- import / translation / timeout-only evidence 归为 P2。

## 10. Header 和 source region 策略

工具 report 到 header 的位置必须保留，但不能过度解读。

分类规则：

- `project_source`：target 自己的 `.c`、`.cc`、`.cpp` 等源码文件。
- `project_header`：target 自己的 `.h`、`.hpp`、`.hh` 等头文件。
- `third_party_source/header`：target tree 内 vendored dependency。
- `system_header`：compiler / libc / libstdc++ / system include path。
- `generated_source`：生成文件或 build-tree source。
- `llvm_ir_only`：工具只报告 `.ll` 或 IR 位置。
- `unknown`：无法可靠分类。

论文主表应优先使用 `project_source_only=1` 的统计。附录或辅助表可以单独报告 header / system cases。

Header case 升级规则：

- header location 行列有效但语义不清楚：P1。
- header location 有客观无效证据：P0。
- system/STL header location 没有明确 mismatch：P2，或排除在 project-source 主统计之外。

## 11. 验证规则

对每个工具级 collector：

- 检查 `tool_cases.csv` 表头完全匹配标准 schema。
- 检查每个 P0 row 都有：
  - raw artifact；
  - run directory；
  - priority reason；
  - concrete evidence snippet 或 objective location-validity failure。
- 对每个 reported source file，检查它存在；若不存在，则必须标记 `location_validity=missing_file`。
- 对每个 reported line，检查是否为 `0`；若为 `0`，必须标记 `location_validity=line_zero`，并优先作为 P0 候选处理。
- 对存在的文件，检查 reported line 不超过文件总行数。
- 可行时，检查 reported column 不超过对应行长度。
- 检查所有纳入 run 都属于 O2-g 口径。

对顶层 merger：

- 从工具级 `tool_cases.csv` 按 `target,tool` 统计 P0/P1/P2。
- 确保矩阵 totals 与 inventory groupby totals 一致。
- 不要静默纳入用户指定 manifest 之外的 tools 或 targets。
- 从 `tool_runs.csv` 保留 partial-success mode status。

## 12. 当前已知工具目录

以下工具目录已经存在：

```text
CompilerOptimization/Result/AllUsefulCases/cclyzer++/
CompilerOptimization/Result/AllUsefulCases/dg/
CompilerOptimization/Result/AllUsefulCases/ikos/
CompilerOptimization/Result/AllUsefulCases/phasar/
CompilerOptimization/Result/AllUsefulCases/seahorn/
CompilerOptimization/Result/AllUsefulCases/smack/
CompilerOptimization/Result/AllUsefulCases/yapall/
```

之前检查时已知存在的成熟 case 来源包括：

- `cclyzer++`：若干 target 已有 `ValueCases/all_cases.csv`，例如 zopfli、tengine、flatbuffers、libsndfile。
- `yapall`：若干 O2-g run 已有 `ValueCases/*_yapall_value_cases.csv`。
- `SeaHorn`：多个 target 已有 `summary/all_cases.csv`。
- `SMACK`、`DG`、`Phasar` 和 `IKOS` 需要先完成工具专用 collector 或 schema discovery，再进入顶层矩阵。

这些不是最终纳入决定。最终纳入以用户指定的结果目录为准。

## 13. 用户下一步需要提供的内容

下一步需要用户按工具提供 run list。

对每个工具，请提供以下任一种形式：

- 精确 result directory 列表；或
- 一个 manifest 文件，字段为：

```csv
target,tool,run_dir,input_bc,input_ll,notes
```

一旦某个工具的 run list 确定，就先在该工具自己的 `AllUsefulCases/<tool>/` 目录内收集 cases。只有在工具级 cases 生成完成之后，才重新生成顶层矩阵。

## 14. 风险与控制

- 本计划刻意避免使用全局 parser，因为那会丢失大量工具特有 cases。
- P0 被刻意收窄，以保证 P0 是 paper-ready、高置信证据。
- P1 是语义可疑 report 的主要队列，后续需要人工或更深入 IR/source 验证。
- P2 用来保存 run degradation 和弱证据，避免夸大结论。
- header 和 system-library cases 会被保留并显式标注 source-region，但不能污染 project-source 主表。
- 不得删除或覆盖已有实验 artifacts。
