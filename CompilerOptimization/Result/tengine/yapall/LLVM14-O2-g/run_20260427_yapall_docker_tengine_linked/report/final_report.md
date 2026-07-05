# Yapall Scan Final Report

## Metadata
- target: tengine
- universe: O2
- compiler_universe: LLVM14-O2-g
- yapall_runner: docker:yapall:llvm14
- signatures: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/signatures.json
- docker_image: yapall:llvm14
- docker_signatures: /opt/yapall/signatures.json
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/yapall/LLVM14-O2-g/run_20260427_yapall_docker_tengine_linked
- status_counts: {'reported': 1}
- issue_counts: {'free_non_heap': 9, 'invalid_call': 6578, 'invalid_load': 2602, 'invalid_memcpy_dst': 62, 'invalid_memcpy_src': 132, 'invalid_store': 428, 'points_to_top': 22}

## Highest-Score Inputs
| score | input_bc | mode | contexts | invalid_loads | invalid_stores | invalid_calls | memcpy_dst | memcpy_src | free_non_heap | points_to_top | needs_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9833 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/tengine.bc | subset | 0 | 2602 | 428 | 6578 | 62 | 132 | 9 | 22 | 0 |

## Issue Hotspots By Input
| input_bc | total | kinds |
| --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/tengine.bc | 9833 | free_non_heap=9, invalid_call=6578, invalid_load=2602, invalid_memcpy_dst=62, invalid_memcpy_src=132, invalid_store=428, points_to_top=22 |

## Status Matrix
| input_bc | mode | contexts | check | status | return_code | elapsed_sec | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/tengine.bc | subset | 0 | default | reported | 0 | 2 | /home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/yapall/LLVM14-O2-g/run_20260427_yapall_docker_tengine_linked/log/CompilerOptimization_CompilerResult_tengine_LLVM14-O2-g_artifacts_tengine_bc_subset_k0_default.log |

## Notes
- Yapall reports IR-level pointer-analysis imprecision signals, not source-level confirmed vulnerabilities.
- Treat nonzero invalid_* rows as candidate bug reports for manual triage and O0/O2/O2-noinline comparison.
- This runner preserves raw stdout/stderr logs and normalized TSV evidence.
