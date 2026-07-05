# Yapall Scan Final Report

## Metadata
- target: zfp
- universe: O2
- compiler_universe: LLVM14-O2-g
- yapall_bin: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/target/release/yapall
- signatures: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/signatures.json
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0
- status_counts: {'reported': 2}
- issue_counts: {'free_non_heap': 2, 'invalid_load': 300, 'invalid_memcpy_dst': 32, 'invalid_memcpy_src': 32, 'invalid_store': 266, 'points_to_top': 2}

## Highest-Score Inputs
| score | input_bc | mode | contexts | invalid_loads | invalid_stores | invalid_calls | memcpy_dst | memcpy_src | free_non_heap | points_to_top | needs_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 317 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc | subset | 0 | 150 | 133 | 0 | 16 | 16 | 1 | 1 | 0 |
| 317 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc | unification | 0 | 150 | 133 | 0 | 16 | 16 | 1 | 1 | 0 |

## Issue Hotspots By Input
| input_bc | total | kinds |
| --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc | 634 | free_non_heap=2, invalid_load=300, invalid_memcpy_dst=32, invalid_memcpy_src=32, invalid_store=266, points_to_top=2 |

## Status Matrix
| input_bc | mode | contexts | check | status | return_code | elapsed_sec | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc | subset | 0 | default | reported | 0 | 2 | /home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/log/CompilerOptimization_CompilerResult_zfp_LLVM14-O2-g_artifacts_zfp_O2_g_bc_subset_k0_default.log |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc | unification | 0 | default | reported | 0 | 2 | /home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/log/CompilerOptimization_CompilerResult_zfp_LLVM14-O2-g_artifacts_zfp_O2_g_bc_unification_k0_default.log |

## Notes
- Yapall reports IR-level pointer-analysis imprecision signals, not source-level confirmed vulnerabilities.
- Treat nonzero invalid_* rows as candidate bug reports for manual triage and O0/O2/O2-noinline comparison.
- This runner preserves raw stdout/stderr logs and normalized TSV evidence.
