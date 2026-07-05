# Yapall Scan Final Report

## Metadata
- target: masscan
- universe: O2
- compiler_universe: LLVM14-O2-g
- yapall_runner: docker:yapall:llvm14
- signatures: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/signatures.json
- docker_image: yapall:llvm14
- docker_signatures: /opt/yapall/signatures.json
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/yapall/LLVM14-O2-g/run_20260506_yapall_docker_masscan_linked_rescan
- status_counts: {'reported': 1}
- issue_counts: {'free_non_heap': 665, 'invalid_call': 20600, 'invalid_load': 89035, 'invalid_memcpy_dst': 32391, 'invalid_memcpy_src': 8669, 'invalid_store': 198072, 'points_to_top': 11017}

## Highest-Score Inputs
| score | input_bc | mode | contexts | invalid_loads | invalid_stores | invalid_calls | memcpy_dst | memcpy_src | free_non_heap | points_to_top | needs_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 360449 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc | subset | 0 | 89035 | 198072 | 20600 | 32391 | 8669 | 665 | 11017 | 0 |

## Issue Hotspots By Input
| input_bc | total | kinds |
| --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc | 360449 | free_non_heap=665, invalid_call=20600, invalid_load=89035, invalid_memcpy_dst=32391, invalid_memcpy_src=8669, invalid_store=198072, points_to_top=11017 |

## Status Matrix
| input_bc | mode | contexts | check | status | return_code | elapsed_sec | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc | subset | 0 | default | reported | 0 | 101 | /home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/yapall/LLVM14-O2-g/run_20260506_yapall_docker_masscan_linked_rescan/log/CompilerOptimization_CompilerResult_masscan_LLVM14-O2-g_artifacts_masscan_O2_g_bc_subset_k0_default.log |

## Notes
- Yapall reports IR-level pointer-analysis imprecision signals, not source-level confirmed vulnerabilities.
- Treat nonzero invalid_* rows as candidate bug reports for manual triage and O0/O2/O2-noinline comparison.
- This runner preserves raw stdout/stderr logs and normalized TSV evidence.
