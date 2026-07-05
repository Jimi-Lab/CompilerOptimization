# Yapall Scan Final Report

## Metadata
- target: lepton
- universe: O2
- compiler_universe: LLVM14-O2-g
- yapall_runner: docker:yapall:llvm14
- signatures: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/signatures.json
- docker_image: yapall:llvm14
- docker_signatures: /opt/yapall/signatures.json
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/yapall/LLVM14-O2-g/run_20260427_yapall_docker_lepton_linked
- status_counts: {'reported': 1}
- issue_counts: {'free_non_heap': 406, 'invalid_call': 170247, 'invalid_load': 254087, 'invalid_memcpy_dst': 51273, 'invalid_memcpy_src': 43924, 'invalid_store': 229997, 'points_to_top': 15057}

## Highest-Score Inputs
| score | input_bc | mode | contexts | invalid_loads | invalid_stores | invalid_calls | memcpy_dst | memcpy_src | free_non_heap | points_to_top | needs_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 764991 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc | subset | 0 | 254087 | 229997 | 170247 | 51273 | 43924 | 406 | 15057 | 0 |

## Issue Hotspots By Input
| input_bc | total | kinds |
| --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc | 764991 | free_non_heap=406, invalid_call=170247, invalid_load=254087, invalid_memcpy_dst=51273, invalid_memcpy_src=43924, invalid_store=229997, points_to_top=15057 |

## Status Matrix
| input_bc | mode | contexts | check | status | return_code | elapsed_sec | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc | subset | 0 | default | reported | 0 | 333 | /home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/yapall/LLVM14-O2-g/run_20260427_yapall_docker_lepton_linked/log/CompilerOptimization_CompilerResult_lepton_LLVM14-O2-g_lepton_artifacts_lepton_O2_g_bc_subset_k0_default.log |

## Notes
- Yapall reports IR-level pointer-analysis imprecision signals, not source-level confirmed vulnerabilities.
- Treat nonzero invalid_* rows as candidate bug reports for manual triage and O0/O2/O2-noinline comparison.
- This runner preserves raw stdout/stderr logs and normalized TSV evidence.
