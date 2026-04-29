# DG O2-g Case Collection Report

## Scope

- tool: `dg`
- universe: `O2-g` / `LLVM14-O2-g`
- selected runs: `8`
- run list: `/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/dg/result.txt`
- output directory: `/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/dg/O2-g`

## Collection Rules

- `summary/line_hits.csv` is treated as DG's normalized native `--c-lines` reported cases.
- Rows with multiple `source_files` are expanded to one standardized case per source candidate.
- `summary/warnings.csv` is collected as native stderr diagnostic evidence; warnings with parseable `!dbg !N` and a resolvable `!DILocation` are mapped back to source using the run's `work/*.ll`.
- `summary/failures.csv` is collected as run/mode-level P2 degradation evidence.
- P0 is reserved for objective invalid source locations according to the matrix plan.
- Valid ordinary DG line hits are kept as P2 unless a warning/debug-location mismatch or another objective invalidity is present.

## Priority Counts

| key | count |
| --- | ---: |
| `P2` | 1817863 |
| `P1` | 618 |
| `P0` | 295 |

## Priority Reasons

| key | count |
| --- | ---: |
| `ValidDgLineHit` | 1799483 |
| `ToolWarningOnly` | 9544 |
| `ExternalOrUnresolvedSource` | 8780 |
| `ToolWarningWithDebugLocNeedsReview` | 618 |
| `LineZero` | 159 |
| `ColumnOutOfRange` | 131 |
| `ToolFailureOnly` | 22 |
| `RunTimeoutOnly` | 19 |
| `UnsupportedModeFailure` | 15 |
| `SourceLinePreprocessorOnly` | 5 |

## Case Kinds

| key | count |
| --- | ---: |
| `DGLineHit` | 1799483 |
| `RunOrLocationWeakEvidence` | 18324 |
| `ToolWarningDebugLocCandidate` | 618 |
| `LocationInvalid` | 295 |
| `RunDegradation` | 56 |

## Target Summary

| target | line-hit rows | expanded line-hit cases | warnings | failures | P0 | P1 | P2 | invalid locations | source regions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| flatbuffers | 24759 | 36825 | 2310 | 9 | 65 | 0 | 39079 | column_out_of_range=47, line_zero=13, no_debug_loc=2296, preprocessor_only=5, unknown=9, valid=36774 | llvm_ir_only=2305, project_header=5086, project_source=27323, system_header=4233, unknown=197 |
| lepton | 72696 | 85876 | 376 | 8 | 124 | 152 | 85984 | column_out_of_range=84, line_zero=40, no_debug_loc=94, unknown=106, valid=85936 | llvm_ir_only=200, project_header=12466, project_source=69344, system_header=4035, unknown=215 |
| libsndfile | 124113 | 176625 | 252 | 6 | 10 | 14 | 176859 | line_zero=10, no_debug_loc=182, unknown=62, valid=176629 | llvm_ir_only=244, project_header=1348, project_source=175225, system_header=56, unknown=10 |
| masscan | 118098 | 162234 | 1004 | 11 | 7 | 266 | 162976 | line_zero=7, no_debug_loc=584, unknown=165, valid=162493 | llvm_ir_only=749, project_header=847, project_source=161627, system_header=19, unknown=7 |
| redis | 772574 | 1266179 | 2112 | 10 | 55 | 122 | 1268124 | line_zero=55, no_debug_loc=1518, unknown=440, valid=1266288 | llvm_ir_only=1958, project_header=5160, project_source=1118445, system_header=164, third_party_header=11740, third_party_source=130811, unknown=23 |
| tengine | 41579 | 41923 | 2432 | 7 | 9 | 64 | 44289 | line_zero=9, no_debug_loc=2320, unknown=39, valid=41994 | llvm_ir_only=2359, project_header=4778, project_source=4930, system_header=31, third_party_header=32255, unknown=9 |
| zfp | 14831 | 18084 | 1624 | 3 | 12 | 0 | 19699 | line_zero=12, no_debug_loc=1624, unknown=3, valid=18072 | llvm_ir_only=1627, project_header=943, project_source=17129, unknown=12 |
| zopfli | 18933 | 20738 | 126 | 2 | 13 | 0 | 20853 | line_zero=13, no_debug_loc=84, unknown=44, valid=20725 | llvm_ir_only=128, project_header=243, project_source=20469, system_header=13, unknown=13 |

## Location Validity

| key | count |
| --- | ---: |
| `valid` | 1808911 |
| `no_debug_loc` | 8702 |
| `unknown` | 868 |
| `line_zero` | 159 |
| `column_out_of_range` | 131 |
| `preprocessor_only` | 5 |

## Source Regions

| key | count |
| --- | ---: |
| `project_source` | 1594492 |
| `third_party_source` | 130811 |
| `third_party_header` | 43995 |
| `project_header` | 30871 |
| `llvm_ir_only` | 9570 |
| `system_header` | 8551 |
| `unknown` | 486 |

## Warning Families

| key | count |
| --- | ---: |
| `unsupported_shufflevector` | 6370 |
| `unhandled_ir` | 2934 |
| `nonzero_memset` | 870 |
| `inttoptr_constant` | 36 |
| `native_warning` | 26 |

## Output Files

- `tool_cases.csv`: standardized DG case inventory.
- `tool_runs.csv`: selected run manifest.
- `native_output_profile.md`: DG native output interpretation.
- `collection_manifest.json`: machine-readable stats and run selection.
