# Yapall Scan Final Report

## Metadata

- target: zopfli
- universe: O2
- compiler_universe: LLVM14-O2-g
- yapall_bin: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/target/release/yapall
- signatures: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/signatures.json
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/yapall/LLVM14-O2-g/run_20260426_yapall_zopfli_k0
- status_counts: {'reported': 2}
- issue_counts: {'free_non_heap': 4, 'invalid_load': 220, 'invalid_memcpy_src': 4, 'invalid_store': 212}

## Highest-Score Inputs

| score | input_bc                                                                                                               | mode        | contexts | invalid_loads | invalid_stores | invalid_calls | memcpy_dst | memcpy_src | free_non_heap | points_to_top | needs_signature |
| ----- | ---------------------------------------------------------------------------------------------------------------------- | ----------- | -------- | ------------- | -------------- | ------------- | ---------- | ---------- | ------------- | ------------- | --------------- |
| 220   | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc | subset      | 0        | 110           | 106            | 0             | 0          | 2          | 2             | 0             | 0               |
| 220   | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc | unification | 0        | 110           | 106            | 0             | 0          | 2          | 2             | 0             | 0               |

## Issue Hotspots By Input

| input_bc                                                                                                               | total | kinds                                                                      |
| ---------------------------------------------------------------------------------------------------------------------- | ----- | -------------------------------------------------------------------------- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc | 440   | free_non_heap=4, invalid_load=220, invalid_memcpy_src=4, invalid_store=212 |

## Status Matrix

| input_bc                                                                                                               | mode        | contexts | check   | status   | return_code | elapsed_sec | log                                                                                                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------- | ----------- | -------- | ------- | -------- | ----------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc | subset      | 0        | default | reported | 0           | 0           | /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/yapall/LLVM14-O2-g/run_20260426_yapall_zopfli_k0/log/CompilerOptimization_CompilerResult_zopfli_LLVM14-O2-g_artifacts_zopfli_O2_g_zopfli_only_bc_subset_k0_default.log      |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc | unification | 0        | default | reported | 0           | 1           | /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/yapall/LLVM14-O2-g/run_20260426_yapall_zopfli_k0/log/CompilerOptimization_CompilerResult_zopfli_LLVM14-O2-g_artifacts_zopfli_O2_g_zopfli_only_bc_unification_k0_default.log |

## Notes

- Yapall reports IR-level pointer-analysis imprecision signals, not source-level confirmed vulnerabilities.
- Treat nonzero invalid_* rows as candidate bug reports for manual triage and O0/O2/O2-noinline comparison.
- This runner preserves raw stdout/stderr logs and normalized TSV evidence.
