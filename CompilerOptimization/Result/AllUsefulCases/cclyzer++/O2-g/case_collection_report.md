# cclyzer++ O2-g Useful Case 收集报告

## 范围

- tool: `cclyzer++`
- universe: `LLVM14-O2-g`
- 纳入的 targets: `flatbuffers`, `libsndfile`, `tengine`, `zopfli`
- 数据来源: 已有各 run 的 `ValueCases/all_cases.csv`
- 重新分类依据: `CompilerOptimization/Result/AllUsefulCases/useful_cases_matrix_plan.md`
- 参考分析方案: `CompilerOptimization/Tools/cclyzerpp/AnalysisResult/cclyzerpp_native_output_case_analysis_plan.md`

## 优先级统计

| key | count |
| --- | ---: |
| `P2` | 105423 |
| `P0` | 27932 |
| `P1` | 15542 |

## 优先级原因

| key | count |
| --- | ---: |
| `ExternalOrUnresolvedLineZero` | 66489 |
| `ExternalOrUnresolvedNoDebugLoc` | 24410 |
| `NoSourceFileInFact` | 10380 |
| `ExternalOrUnresolvedColumnOutOfRange` | 157 |
| `LineZero` | 27869 |
| `NoDebugLocNeedsIRReview` | 12055 |
| `LineOutOfRange` | 7 |
| `SourceIRMismatchNeedsSemanticReview` | 3487 |
| `ExternalOrUnresolvedSourceIRMismatch` | 3987 |
| `ColumnOutOfRange` | 56 |

## Target 汇总

| target | cases | P0 | P1 | P2 | source regions | top phenomena |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| flatbuffers | 118945 | 16975 | 10134 | 91836 | system_header=82298, project_header=18270, llvm_ir_only=9538, project_source=8839 | Wanted-LineColumnMissing=99304, Wanted-PhiMergeLocationDrift=11452, Wanted-AliasCollapseWithBadLocation=4566, Wanted-CodeMismatch=2050, Wanted-AllocationSiteDrift=1573 |
| libsndfile | 15570 | 7742 | 4511 | 3317 | project_source=11726, llvm_ir_only=3310, project_header=527, system_header=7 | Wanted-LineColumnMissing=10173, Wanted-PhiMergeLocationDrift=3713, Wanted-CodeMismatch=1037, Wanted-AliasCollapseWithBadLocation=326, Wanted-AllocationSiteDrift=321 |
| tengine | 10164 | 411 | 67 | 9686 | third_party_header=8328, llvm_ir_only=1354, project_source=450, project_header=28, system_header=4 | Wanted-LineColumnMissing=7083, Wanted-PhiMergeLocationDrift=2280, Wanted-AliasCollapseWithBadLocation=403, Wanted-CodeMismatch=336, Wanted-AllocationSiteDrift=62 |
| zopfli | 4218 | 2804 | 830 | 584 | project_source=3560, llvm_ir_only=583, project_header=74, system_header=1 | Wanted-LineColumnMissing=3014, Wanted-PhiMergeLocationDrift=624, Wanted-CodeMismatch=276, Wanted-AllocationSiteDrift=155, Wanted-AliasCollapseWithBadLocation=149 |

## 仅项目源码统计

| target | project-source cases | P0 | P1 | P2 |
| --- | ---: | ---: | ---: | ---: |
| flatbuffers | 8839 | 2505 | 6334 | 0 |
| libsndfile | 11726 | 7252 | 4474 | 0 |
| tengine | 450 | 394 | 56 | 0 |
| zopfli | 3560 | 2730 | 830 | 0 |

## 位置有效性

| key | count |
| --- | ---: |
| `line_zero` | 94358 |
| `no_debug_loc` | 36465 |
| `unknown` | 10380 |
| `column_out_of_range` | 213 |
| `line_out_of_range` | 7 |
| `valid` | 7474 |

## P0 最终审核

最终审核日期: `2026-04-29`.

结论: `P0` rows 是客观的 invalid-location 证据，但不能理解为 27,932 个彼此独立的论文 case。它们是 cclyzer++ 原生 facts 映射出来的 relation-level rows。按 `(reported_file, reported_line, reported_column, priority_reason)` 去重后，P0 集合包含 171 个 unique locations。

P0 row 统计:

| reason | rows | unique locations | audit result |
| --- | ---: | ---: | --- |
| `LineZero` | 27869 | 130 | 有效的 invalid-line 证据；应表述为 line missing / no valid source line，不总是 wrong-line mismatch |
| `ColumnOutOfRange` | 56 | 35 | 最强的 location-invalid 证据；reported column 超过实际源码行长度 |
| `LineOutOfRange` | 7 | 6 | 最强的 location-invalid 证据；reported line 超过实际文件总行数 |

已执行的批量检查:

- 每个 P0 `reported_file` 都能在本地找到。
- 每个 `LineZero` P0 row 都满足 `reported_line=0`。
- 每个 `LineOutOfRange` P0 unique location 都已按本地文件总行数检查。
- 每个 `ColumnOutOfRange` P0 unique location 都已按实际本地源码行长度检查。
- 未发现检查失败项。

重要解释约束:

- `LineOutOfRange` 和 `ColumnOutOfRange` 是最干净、最适合直接进入论文的 line/column invalidity cases。
- `LineZero` 作为源码行号在客观上无效，但多数 rows 表示 debug/source-location loss，而不是已经证明 report 错到了另一个非零行。`LineZero` rows 中，27,115 行同时有 `ir_line=0`，318 行 `ir_line` 为空，436 行有非零 recovered `ir_line`。
- 因此，使用 `LineZero` cases 时要谨慎：它们支持 "no valid source line / line attribution collapsed to 0"；只有 recovered `ir_line` 非零的子集，才适合表述为 relation line 与 recovered IR debug line 之间的直接行号不一致。
- 论文应选择有代表性的 unique locations，而不是使用 raw relation-row counts。

## 纳入的 Runs

- `flatbuffers`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/cclyzerpp/LLVM14-O2-g/run_20260427_132609_flatbuffers_flatc_O2_g`
- `libsndfile`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g`
- `tengine`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/cclyzerpp/LLVM14-O2-g/run_20260427_132038_tengine`
- `zopfli`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/cclyzerpp/LLVM14-O2-g/run_20260427_132038_zopfli_O2_g_zopfli_only`

## 说明

- 没有覆盖或修改已有的 cclyzer++ `ValueCases`。
- `P0` 当前只限于 project source/header 中的客观无效位置：`LineZero`、`LineOutOfRange`、`ColumnOutOfRange`，以及明确缺失的项目文件。
- `SourceIRMismatch` 对 project code 归为 `P1`，因为它是 semantic/source-IR consistency candidate，不等同于工具原生 report 中可直接比对文本的 `SourceTextMismatch`。
- `NoDebugLoc` 对 project code 归为 `P1`，对 external/unresolved code 归为 `P2`；除非它同时具备具体的 project line/column invalidity，否则不升为 P0。
- 空 source file、system header、third-party header 和 unknown remap cases 会保留，但除非存在项目本地的客观无效证据，否则降为 `P2`。
- Header rows 会保留并通过 `source_region` 和 `header_context` 标注；仅仅因为位置在 header 中，不作为 P0 原因。
- 完整表保留 system/header/third-party cases 以便审计；论文正文统计 project-source 时应使用 `project_source_only=1`。

## 输出文件

- `tool_cases.csv`
- `tool_runs.csv`
- `native_output_profile.md`
- `collection_manifest.json`
- `scripts/collect_cclyzerpp_o2g_cases.py`
