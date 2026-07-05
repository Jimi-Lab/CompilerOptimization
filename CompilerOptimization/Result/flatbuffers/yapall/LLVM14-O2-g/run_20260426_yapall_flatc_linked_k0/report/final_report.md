# Yapall Scan Final Report

## Metadata
- target: flatbuffers
- universe: O2
- compiler_universe: LLVM14-O2-g
- yapall_bin: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/target/release/yapall
- signatures: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/signatures.json
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_linked_k0
- status_counts: {'timeout': 1}
- issue_counts: {}

## Highest-Score Inputs
| score | input_bc | mode | contexts | invalid_loads | invalid_stores | invalid_calls | memcpy_dst | memcpy_src | free_non_heap | points_to_top | needs_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Issue Hotspots By Input
| input_bc | total | kinds |
| --- | --- | --- |

## Status Matrix
| input_bc | mode | contexts | check | status | return_code | elapsed_sec | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc | subset | 0 | default | timeout | 137 | 120 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/yapall/LLVM14-O2-g/run_20260426_yapall_flatc_linked_k0/log/CompilerOptimization_CompilerResult_flatbuffers_LLVM14-O2-g_artifacts_flatbuffers_flatc_O2_g_bc_subset_k0_default.log |

## Notes
- Yapall reports IR-level pointer-analysis imprecision signals, not source-level confirmed vulnerabilities.
- Treat nonzero invalid_* rows as candidate bug reports for manual triage and O0/O2/O2-noinline comparison.
- This runner preserves raw stdout/stderr logs and normalized TSV evidence.
