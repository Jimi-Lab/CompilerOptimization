# libsndfile / zfp P0 Case Study Plan

本目录用于做论文中的 targeted case study：只研究 `libsndfile` 和 `zfp` 两个 repo 的 P0 cases，目标是评估 LLM/agent 是否能从优化 IR、debug metadata、source tree 和 analyzer 原生证据中恢复正确源码行号。

主输入清单：

- `libsndfile_zfp_p0_candidate_inventory.csv`
- `selected_20_p0_case_studies.csv`
- `selected_20_p0_case_studies.md`
- `CASE_STUDY_PROTOCOL.md`
- `llm_recovery_prompt_template.md`

该 CSV 从以下标准化结果抽取，并按 `(repo, tool, reported_file, reported_line, reported_column, priority_reason)` 去重：

- `AllUsefulCases/phasar/O2-g/tool_cases.csv`
- `AllUsefulCases/seahorn/O2-g/tool_cases.csv`
- `AllUsefulCases/dg/O2-g/tool_cases.csv`
- `AllUsefulCases/cclyzer++/O2-g/tool_cases.csv`
- `AllUsefulCases/yapall/O2-g/tool_cases.csv`

## Current 20-Case Study Set

`selected_20_p0_case_studies.csv` 是当前论文 case study 的固定选择：

- `libsndfile`: phasar 2, seahorn 2, dg 2, cclyzer++ 2, yapall 2.
- `zfp`: phasar 2, seahorn 2, dg 2, cclyzer++ 2, yapall 2.
- 总计 20 个 P0 case。

选择原则是每个 repo/tool 平均 2 个 case。若某个 repo/tool 的 unique P0 location 不足 2 个，第二个 case 标为 `repeat-location-variant`，只能作为同一失效模式的补充证据，不能在论文中写成新的 unique location。

正式研究每个 case 前，先阅读 `CASE_STUDY_PROTOCOL.md`。该守则定义了 evidence package、LLM recovery 输入输出、人工验证标签，以及各工具的专门证据要求。

每个 selected case 已建立固定工作目录：

```text
CasesStudy/<tool>/<repo>/<study_case_id>/
```

目录内包含 `input.json`、`case.md`、`llm_output.md` 和 `verification.md`。这些文件只引用原始 artifact，不复制或覆盖 analyzer run。

## Current Candidate Counts

| repo | tool | unique P0 locations |
| --- | --- | ---: |
| libsndfile | phasar | 2 |
| libsndfile | seahorn | 4 |
| libsndfile | dg | 1 |
| libsndfile | cclyzer++ | 83 |
| libsndfile | yapall | 96 |
| zfp | phasar | 10 |
| zfp | seahorn | 1 |
| zfp | dg | 1 |
| zfp | cclyzer++ | 42 |
| zfp | yapall | 4 |

## Case Selection Strategy

不要直接按 raw P0 rows 选论文案例。cclyzer++ / yapall 的 `LineZero` rows 会大量重复同一 source location，论文中应使用 unique locations 和代表性 case。

本轮固定为 20 个 case：每个 repo/tool 2 个。选择时遵循以下优先级：

1. 优先选择 `ColumnOutOfRange`、`LineOutOfRange`、`SourceTextMismatch`。
   这些是最干净的 objective invalid-location 证据，恢复目标明确。
2. 其次选择 `LineZero` 且有足够 IR anchor 的 case。
   这类 case 适合展示 source-location loss，即 analyzer/fact 映射到 project file 但 line=0。
3. 对 unique location 不足 2 个的 repo/tool，第二个 raw row 标记为 `repeat-location-variant`。
   这类 case 只用于补充同一失效模式，不能计作新的 unique source-location case。
4. dg 的 P0 多数可能是 file/line 完全缺失。
   在当前 20-case set 中保留为 negative/control case，用来检查 LLM 是否能在证据不足时拒绝猜测。

## Evidence Package Per Case

每个 selected case 使用固定目录：

```text
CasesStudy/<tool>/<repo>/<study_case_id>/
```

每个目录至少保存：

- `case.md`: 人工整理后的 case narrative。
- `input.json`: 给 LLM/agent 的结构化输入。
- `llm_output.md`: LLM 输出的候选恢复行号和理由。
- `verification.md`: 人工核查结果。

`input.json` 应包含：

- repo、tool、case_uid、priority_reason。
- run_dir、input_bc、input_ll。
- raw_artifact、raw_row_or_line。
- reported_file、reported_line、reported_column。
- ir_function、ir_instruction、ir_line、ir_snippet。
- source_snippet 和 source_context。
- evidence_files 中的 row/source/IR snippets。
- 本地 source root。

## LLM Recovery Task

LLM 的任务不是判断 analyzer 是否真的发现漏洞，而是：

1. 解释为什么当前 reported location 是无效的。
2. 从 IR snippet、debug metadata、function name、raw relation/warning、source tree 中恢复最可能的真实 source line。
3. 输出候选行号、源码片段、置信度和证据链。
4. 如果无法恢复，明确输出 `unrecoverable`，并说明缺少什么证据。

推荐输出 schema：

```json
{
  "recovered_file": "...",
  "recovered_line": 0,
  "recovered_column": 0,
  "source_text": "...",
  "confidence": "high|medium|low|unrecoverable",
  "evidence": [
    "IR instruction ...",
    "function/scope ...",
    "nearby source text ..."
  ],
  "failure_reason": ""
}
```

## Manual Verification

每个 LLM 输出都要人工核查：

- `exact`: 文件和行号都正确。
- `nearby`: 文件正确，行号在同一语句/多行表达式范围内。
- `function-only`: 只恢复到正确函数，未恢复到具体行。
- `wrong`: 文件或语义不匹配。
- `unrecoverable`: 证据不足，合理拒绝恢复。

论文正文建议报告：

- case 原始无效位置，例如 `line=0` 或 `column out of range`。
- LLM 恢复前后对比。
- 为什么仅靠 analyzer 原输出无法得出正确 source location。
- LLM 使用哪些 IR/source/debug 证据恢复了行号。

## Recommended First Pass

先从以下类型开始：

- libsndfile/phasar: `SourceTextMismatch` 或 `LineOutOfRange`。
- libsndfile/cclyzer++: `ColumnOutOfRange`，如果存在；否则选 `LineZero` 且 `ir_snippet` 清楚的 case。
- libsndfile/yapall: 选 `LineZero` 但有具体 `ir_function` / `ir_instruction` 的 case。
- zfp/phasar: `SourceTextMismatch` 或 `LineOutOfRange`。
- zfp/cclyzer++: `ColumnOutOfRange` 或高重复的 `LineZero` unique location。
- zfp/yapall: 4 个 unique `LineZero` 全部可以检查。

完成第一轮后，再从每个工具补 1 个失败恢复 case，形成正反对照。
