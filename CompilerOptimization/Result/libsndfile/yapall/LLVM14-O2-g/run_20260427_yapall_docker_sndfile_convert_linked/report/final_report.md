# Yapall Scan Final Report

## Metadata
- target: libsndfile
- universe: O2
- compiler_universe: LLVM14-O2-g
- yapall_runner: docker:yapall:llvm14
- signatures: /home/jimi/PaperExperiment/CompilerOptimization/Tools/yapall/yapall/signatures.json
- docker_image: yapall:llvm14
- docker_signatures: /opt/yapall/signatures.json
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked
- status_counts: {'reported': 1}
- issue_counts: {'free_non_heap': 1068, 'invalid_call': 115830, 'invalid_load': 329600, 'invalid_memcpy_dst': 67712, 'invalid_memcpy_src': 21845, 'invalid_store': 699068, 'points_to_top': 12184}

## Highest-Score Inputs
| score | input_bc | mode | contexts | invalid_loads | invalid_stores | invalid_calls | memcpy_dst | memcpy_src | free_non_heap | points_to_top | needs_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1247307 | /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc | subset | 0 | 329600 | 699068 | 115830 | 67712 | 21845 | 1068 | 12184 | 0 |

## Issue Hotspots By Input
| input_bc | total | kinds |
| --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc | 1247307 | free_non_heap=1068, invalid_call=115830, invalid_load=329600, invalid_memcpy_dst=67712, invalid_memcpy_src=21845, invalid_store=699068, points_to_top=12184 |

## Status Matrix
| input_bc | mode | contexts | check | status | return_code | elapsed_sec | log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc | subset | 0 | default | reported | 0 | 360 | /home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/log/CompilerOptimization_CompilerResult_libsndfile_LLVM14-O2-g_artifacts_libsndfile_sndfile_convert_O2_g_bc_subset_k0_default.log |

## Notes
- Yapall reports IR-level pointer-analysis imprecision signals, not source-level confirmed vulnerabilities.
- Treat nonzero invalid_* rows as candidate bug reports for manual triage and O0/O2/O2-noinline comparison.
- This runner preserves raw stdout/stderr logs and normalized TSV evidence.
