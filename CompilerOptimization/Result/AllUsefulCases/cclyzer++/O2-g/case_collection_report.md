# cclyzer++ O2-g Useful Case 收集报告

## 范围

- tool: `cclyzer++`
- universe: `LLVM14-O2-g`
- 纳入的 targets: `flatbuffers`, `libsndfile`, `tengine`, `zopfli`, `lepton`, `masscan`, `zfp`
- 数据来源: 每个 run 的原生 `relations/*.csv.gz`，经 `CompilerOptimization/Tools/cclyzerpp/analyze_native_value_cases.py` 生成 `ValueCases/all_cases.csv` 后统一标准化
- 明确未使用: `extract/candidates.tsv`、`extract/relation_counts.tsv` 等不完整 extract 摘要
- 重新分类依据: `CompilerOptimization/Result/AllUsefulCases/useful_cases_matrix_plan.md`
- 参考分析方案: `CompilerOptimization/Tools/cclyzerpp/AnalysisResult/cclyzerpp_native_output_case_analysis_plan.md`

## 优先级统计

| key | count |
| --- | ---: |
| `P2` | 136370 |
| `P0` | 127974 |
| `P1` | 25649 |

## 优先级原因

| key | count |
| --- | ---: |
| `ExternalOrUnresolvedLineZero` | 83900 |
| `ExternalOrUnresolvedNoDebugLoc` | 26522 |
| `NoSourceFileInFact` | 21316 |
| `ExternalOrUnresolvedColumnOutOfRange` | 261 |
| `LineZero` | 127901 |
| `NoDebugLocNeedsIRReview` | 18307 |
| `LineOutOfRange` | 7 |
| `SourceIRMismatchNeedsSemanticReview` | 7342 |
| `ExternalOrUnresolvedSourceIRMismatch` | 4371 |
| `ColumnOutOfRange` | 66 |

## Target 汇总

| target | cases | P0 | P1 | P2 | source regions | top phenomena |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| flatbuffers | 118945 | 16975 | 10134 | 91836 | system_header=82298, project_header=18270, llvm_ir_only=9538, project_source=8839 | Wanted-LineColumnMissing=99304, Wanted-PhiMergeLocationDrift=11452, Wanted-AliasCollapseWithBadLocation=4566, Wanted-CodeMismatch=2050, Wanted-AllocationSiteDrift=1573 |
| lepton | 66894 | 40025 | 3766 | 23103 | project_header=31698, system_header=18843, project_source=12093, llvm_ir_only=4260 | Wanted-LineColumnMissing=59521, Wanted-PhiMergeLocationDrift=3643, Wanted-AliasCollapseWithBadLocation=1683, Wanted-CodeMismatch=1497, Wanted-AllocationSiteDrift=550 |
| libsndfile | 15570 | 7742 | 4511 | 3317 | project_source=11726, llvm_ir_only=3310, project_header=527, system_header=7 | Wanted-LineColumnMissing=10173, Wanted-PhiMergeLocationDrift=3713, Wanted-CodeMismatch=1037, Wanted-AliasCollapseWithBadLocation=326, Wanted-AllocationSiteDrift=321 |
| masscan | 21686 | 13375 | 4835 | 3476 | project_source=17989, llvm_ir_only=3472, project_header=221, system_header=4 | Wanted-LineColumnMissing=15696, Wanted-PhiMergeLocationDrift=3086, Wanted-CodeMismatch=1554, Wanted-AliasCollapseWithBadLocation=868, Wanted-AllocationSiteDrift=482 |
| tengine | 10164 | 411 | 67 | 9686 | third_party_header=8328, llvm_ir_only=1354, project_source=450, project_header=28, system_header=4 | Wanted-LineColumnMissing=7083, Wanted-PhiMergeLocationDrift=2280, Wanted-AliasCollapseWithBadLocation=403, Wanted-CodeMismatch=336, Wanted-AllocationSiteDrift=62 |
| zfp | 52516 | 46642 | 1506 | 4368 | project_source=48148, llvm_ir_only=4368 | Wanted-LineColumnMissing=45148, Wanted-PhiMergeLocationDrift=5205, Wanted-AliasCollapseWithBadLocation=1425, Wanted-CodeMismatch=530, Wanted-AllocationSiteDrift=208 |
| zopfli | 4218 | 2804 | 830 | 584 | project_source=3560, llvm_ir_only=583, project_header=74, system_header=1 | Wanted-LineColumnMissing=3014, Wanted-PhiMergeLocationDrift=624, Wanted-CodeMismatch=276, Wanted-AllocationSiteDrift=155, Wanted-AliasCollapseWithBadLocation=149 |

## 仅项目源码统计

| target | project-source cases | P0 | P1 | P2 |
| --- | ---: | ---: | ---: | ---: |
| flatbuffers | 8839 | 2505 | 6334 | 0 |
| lepton | 12093 | 9423 | 2670 | 0 |
| libsndfile | 11726 | 7252 | 4474 | 0 |
| masscan | 17989 | 13186 | 4803 | 0 |
| tengine | 450 | 394 | 56 | 0 |
| zfp | 48148 | 46642 | 1506 | 0 |
| zopfli | 3560 | 2730 | 830 | 0 |

## 位置有效性

| key | count |
| --- | ---: |
| `line_zero` | 211801 |
| `no_debug_loc` | 44829 |
| `unknown` | 21316 |
| `column_out_of_range` | 327 |
| `line_out_of_range` | 7 |
| `valid` | 11713 |

## P0 最终审核

- P0 rows: `127974`
- P0 unique locations: `381`
- P0 unique files: `333`
- 详细审核文件: `p0_final_audit.md`
- unique location 明细: `p0_unique_locations.csv`

## 纳入的 Runs

- `flatbuffers`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/cclyzerpp/LLVM14-O2-g/run_20260427_132609_flatbuffers_flatc_O2_g`
- `libsndfile`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g`
- `tengine`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/cclyzerpp/LLVM14-O2-g/run_20260427_132038_tengine`
- `zopfli`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/cclyzerpp/LLVM14-O2-g/run_20260427_132038_zopfli_O2_g_zopfli_only`
- `lepton`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/cclyzerpp/LLVM14-O2-g/run_20260430_154121`
- `masscan`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/cclyzerpp/LLVM14-O2-g/run_20260430_120006`
- `zfp`: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927`

## 说明

- 没有删除或修改 cclyzer++ 原始 `relations/`、`log/`、`status/`、`commands/` artifact。
- 新增 lepton/masscan/zfp 的 `ValueCases/` 是从原生 `relations/` 重建的分析输出；总表没有读取 `extract/`。
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
