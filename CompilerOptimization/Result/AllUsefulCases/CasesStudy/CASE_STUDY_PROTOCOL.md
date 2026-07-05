# P0 Case Study Protocol

本文档是 `libsndfile` / `zfp` 的 20 个 P0 case study 守则。目标不是泛泛分析工具输出，而是为论文中的 LLM line recovery 实验保留可复查、可比较、可写入正文的证据链。

## Scope

- 只研究 `O2-g` universe，即 `clang -O2 -g` 生成的 LLVM bitcode/IR。
- 只研究 `libsndfile` 和 `zfp`。
- 只研究 P0 cases。
- 工具范围固定为 `phasar`、`seahorn`、`dg`、`cclyzer++`、`yapall`。
- 每个 repo/tool 选 2 个 case，总计 20 个：`2 repos * 5 tools * 2 cases`。
- `selection_type=unique-location` 可作为独立 source-location case；`selection_type=repeat-location-variant` 只能作为同一失效模式的第二条 evidence，不应在论文中声称为新的 unique location。

## Research Question

每个 case 只回答一个核心问题：

在 `clang -O2 -g` 的优化 IR 中，analyzer 给出的 P0 source location 是否发生丢失或漂移？如果发生，LLM/agent 能否利用 IR instruction、debug metadata、函数语境、source tree 和 raw analyzer output 恢复更可信的源码行号？

不要把 case study 写成“这个程序有没有真实漏洞”。除非另有证据，本目录中的 case label 应聚焦于 location recovery：

- `exact`: LLM 恢复到正确文件和正确行。
- `nearby`: 文件正确，行号落在同一语句或同一多行表达式范围内。
- `function-only`: 只能恢复到正确函数。
- `wrong`: 文件或语义位置错误。
- `unrecoverable`: 证据不足，合理拒绝恢复。

## Case Selection Rules

优先级从高到低：

1. `ColumnOutOfRange`、`LineOutOfRange`、`SourceTextMismatch`。
   这些是最清楚的 objective invalid-location / drift 证据。
2. `LineZero` 且有明确 `ir_function`、`ir_instruction`、`ir_snippet`。
   适合展示 source location loss。
3. `LineZero` 但缺少 source file/function。
   只能作为 negative/control case，用来说明原始输出证据不足时 LLM 应拒绝猜测。

不要选择以下 case 作为主成功案例：

- `reported_file` 缺失且没有 IR function/source candidate。
- 只有 summary count，没有 raw log 或 raw row。
- 无法确认输入 bitcode 或 run directory。
- 同一 repo/tool 中重复同一 location，但未标记为 `repeat-location-variant`。

## Evidence Package Layout

每个 case 使用固定目录：

```text
CasesStudy/<tool>/<repo>/<study_case_id>/
```

每个 case 至少包含：

- `case.md`: 人工 case narrative。
- `input.json`: 给 LLM/agent 的结构化输入。
- `llm_output.md`: LLM 原始输出或 JSON 输出。
- `verification.md`: 人工验证记录。

不得覆盖原始 analyzer run、log、summary、bitcode 或 `.ll` artifact。case 目录只保存引用、摘录和人工判断。

## Required Fields

每个 `case.md` 必须写清：

- `study_case_id`
- repo、tool、universe
- run directory
- input `.bc` 和 `.ll`
- raw artifact path
- raw row or raw log line
- reported file/line/column
- location validity: `line_zero`、`line_out_of_range`、`column_out_of_range`、`source_text_mismatch` 等
- IR function
- IR instruction
- source snippet
- suspected root cause: `inline`、`Phi-node merge`、`SROA struct split`、`CFG simplification`、`DCE`、`DWARF location drift`、`state explosion`、`other`
- LLM recovery result
- manual verification label

## Study Workflow

对每个 case 按以下顺序做，不跳步：

1. **Freeze the record**
   从 `selected_20_p0_case_studies.csv` 拷贝该 case 的完整 metadata 到 `input.json`。确认 `run_dir`、`input_bc`、`input_ll`、`raw_artifact` 存在。

2. **Validate the reported location**
   检查 `reported_file:reported_line:reported_column` 是否真实存在，并记录无效原因。`line=0`、超过文件总行数、超过该行长度、source text 与 analyzer 报告文本不一致，都要明确写入。

3. **Anchor the IR evidence**
   在 `.ll` 中定位 `ir_function` 和 `ir_instruction`。记录相关 `!dbg` metadata、`inlinedAt`、`DISubprogram`、`DILocation`。如果 instruction 无 `!dbg`，记录为 `NoDebugLoc`。

4. **Recover source candidates**
   使用 IR function name、debug metadata、raw report 的 reported_source、source tree 搜索候选源码行。候选必须是可执行语句，优先于空行、注释、宏展开残影和纯声明。

5. **Run LLM recovery**
   使用 `llm_recovery_prompt_template.md`。LLM 只能输出恢复位置和证据链，不能扩展为漏洞判断。

6. **Manual verification**
   人工检查 LLM 输出是否与 source/IR/raw artifact 一致，并给出 `exact`、`nearby`、`function-only`、`wrong` 或 `unrecoverable`。

7. **Write paper note**
   用 5-8 句话写出论文可用叙述：原始输出如何错、优化 IR 中哪个证据仍可用、LLM 如何恢复、人工验证结果是什么。

## Tool-Specific Evidence Rules

### phasar

- 必查 `psr-report.txt` 中的 raw finding。
- 必记录 `!psr.id`、IR instruction、reported variable 和 `reported_source`。
- `SourceTextMismatch` 不等于 source bug；它表示 Phasar raw finding 的 source attribution 与 resolved source line 不一致。

### seahorn

- 必查 `summary/all_cases.csv` 与对应 `log/sea.*.stderr.log`。
- `LineZero` 通常来自 instrumentation 或 Crab/Clam warning 的 location loss。
- 如果 only `line=0` 但有 IR snippet，可尝试恢复；如果没有 function/source anchor，应标 `unrecoverable`。

### dg

- 必查 `summary/line_hits.csv` 和 `log/*.lines.stdout.log`。
- dg 的 `0:0 -> ...` 类输出常缺少 source file。此类 case 默认是 negative/control，LLM 不应凭空猜文件。
- 只有当 `.ll` 或 log 能提供明确 function/source hint 时，才允许尝试 line recovery。

### cclyzer++

- 必查 `ValueCases/all_cases.csv`、对应 `ValueCases/snippets/*.row.txt`、`*.ir.txt`、`*.source.txt`。
- 如果 `ColumnOutOfRange`，需记录该源码行实际长度和 reported column。
- 对 `phi_instr`、`subset.var_points_to`、`subset.callgraph.callgraph_edge` 分开分析，不要混成一种现象。

### yapall

- 必查 analyzer native log、`commands/commands.log`、`status/run_status.tsv` 和 `ValueCases/summary.md`。
- `site_resolution=resolved_exact_operand_instruction` 的 case 优先作为成功恢复案例。
- 标记 `InlineAttributionDrift` 时，必须区分 caller location 和 callee/inlined function location。

## Paper Reporting Rules

论文中每个 case 的表格建议列：

| field | meaning |
| --- | --- |
| case id | `paper-<repo>-<tool>-NN` |
| tool/repo | analyzer and target |
| invalid report | 原始 file:line:column 及无效原因 |
| IR anchor | function + instruction |
| suspected cause | inline / SROA / Phi / DWARF drift / other |
| LLM recovered | recovered file:line |
| verification | exact / nearby / function-only / wrong / unrecoverable |

正文中不要夸大：

- `repeat-location-variant` 只能说是 repeat evidence。
- `unrecoverable` 是有效结果，说明 evidence boundary。
- `nearby` 不应统计成 `exact`。
- 如果没有 `O0` 或 `O2-noinline` 对比，不要把根因唯一归因于 inline；只能说 inline candidate 或 DWARF/inlining attribution candidate。

## Stop Conditions

遇到以下情况应停止该 case 的恢复并记录 `unrecoverable`：

- raw artifact 不存在。
- input `.ll` 不存在且无法从已有 artifact 找到 instruction。
- reported source file 不存在，且 raw log/IR 不提供替代 source hint。
- LLM 输出无法被 source/IR 证据支持。
- 多个候选行号证据强度相同，无法合理排序。

