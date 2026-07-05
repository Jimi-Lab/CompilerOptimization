# Yapall Scan Final Report

## Metadata
- target: flatbuffers
- universe: O2
- compiler_universe: LLVM14-O2-g
- yapall_bin: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/target/release/yapall
- signatures: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/signatures.json
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0
- status_counts: {'verified/no-error': 10}
- issue_counts: {}

## Highest-Score Inputs
| score | input_bc | mode | contexts | invalid_loads | invalid_stores | invalid_calls | memcpy_dst | memcpy_src | free_non_heap | points_to_top | needs_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_001.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_002.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_003.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_004.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_005.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_006.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_007.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_008.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_009.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_010.bc | subset | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Issue Hotspots By Input
| input_bc | total | kinds |
| --- | --- | --- |

## Status Matrix
| input_bc | mode | contexts | check | status | return_code | elapsed_sec | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_001.bc | subset | 0 | default | verified/no-error | 0 | 0 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_001_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_002.bc | subset | 0 | default | verified/no-error | 0 | 0 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_002_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_003.bc | subset | 0 | default | verified/no-error | 0 | 3 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_003_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_004.bc | subset | 0 | default | verified/no-error | 0 | 0 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_004_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_005.bc | subset | 0 | default | verified/no-error | 0 | 1 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_005_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_006.bc | subset | 0 | default | verified/no-error | 0 | 0 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_006_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_007.bc | subset | 0 | default | verified/no-error | 0 | 0 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_007_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_008.bc | subset | 0 | default | verified/no-error | 0 | 3 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_008_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_009.bc | subset | 0 | default | verified/no-error | 0 | 2 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_009_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/bc_objs_flatc/flatc_obj_010.bc | subset | 0 | default | verified/no-error | 0 | 1 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_objs10_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_bc_objs_flatc_flatc_obj_010_bc_subset_k0_default.log |

## Notes
- Yapall reports IR-level pointer-analysis imprecision signals, not source-level confirmed vulnerabilities.
- Treat nonzero invalid_* rows as candidate bug reports for manual triage and O0/O2/O2-noinline comparison.
- This runner preserves raw stdout/stderr logs and normalized TSV evidence.
