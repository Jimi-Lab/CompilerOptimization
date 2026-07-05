# cclyzer++ Scan Final Report

## Metadata
- target: libsndfile
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g
- status: reported
- return_code: 0
- elapsed_sec: 467

## Important Interpretation Note
- cclyzer++ is a global pointer-analysis engine. Rows in `extract/candidates.tsv` are high-signal candidate anomalies for manual review, not verified CWE bug reports.
- Promote a row to a paper case only after O0/O2/O2-noinline comparison and source/IR inspection.

## Candidate Counts
| kind | count |
| --- | ---: |
| CallgraphFanout | 1000 |
| PointsToFanout | 1000 |
| AliasBucketFanout | 1000 |
| PhiMergeHotspot | 1000 |
| TailCallSite | 1000 |
| MissingDebugLoc | 1000 |
| PointerObjectFanout | 180 |

## Top Candidates
| kind | metric | file | line | function | subject | detail |
| --- | ---: | --- | ---: | --- | --- | --- |
| PointsToFanout | 1187 | llvm-link | 0 | psf_log_printf | %1 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 1187 | llvm-link | 0 | psf_log_printf | %16 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %107 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %101 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %89 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %86 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %67 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %53 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %65 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %43 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %47 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %17 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 592 | llvm-link | 0 | psf_log_printf | %126 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 561 | llvm-link | 0 | sf_strerror | %64 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 561 | llvm-link | 0 | main | %252 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 561 | llvm-link | 0 | main | %176 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 557 | llvm-link | 0 | psf_open_file | %446 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 555 | llvm-link | 0 | psf_open_file | %444 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 555 | llvm-link | 0 | sf_strerror | %62 | variable has a broad points-to set; candidate over-approximation / phi merge |
| AliasBucketFanout | 357 | NA | 0 | NA | *typed_heap_alloc@alac_init[%struct.ALAC_PRIVATE* %12][0].?/13[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 357 | NA | 0 | NA | *typed_heap_alloc@wavlike_msadpcm_init[%struct.ALAC_PRIVATE* %36][0].?/13[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 357 | NA | 0 | NA | *typed_heap_alloc@ima_reader_init[%struct.ALAC_PRIVATE* %19][0].?/13[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 357 | NA | 0 | NA | *typed_heap_alloc@ima_writer_init[%struct.ALAC_PRIVATE* %34][0].?/13[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| PointsToFanout | 320 | llvm-link | 0 | wavlike_read_fmt_chunk | %44 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 318 | llvm-link | 0 | wavlike_read_fmt_chunk | %36 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 292 | llvm-link | 0 | psf_binheader_writef | %1 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 292 | llvm-link | 0 | psf_binheader_writef | %25 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 280 | llvm-link | 0 | psf_binheader_readf | %1 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 280 | llvm-link | 0 | psf_binheader_readf | %42 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointerObjectFanout | 210 | NA | 0 | NA | *heap_alloc@ima_reader_init[i8* %19] | memory object has a broad points-to set |

## Largest Relations
| relation | rows |
| --- | ---: |
| variable | 109388 |
| variable_has_type | 109388 |
| variable_in_func_name | 109388 |
| variable_has_name | 107755 |
| subset.operand_points_to | 105258 |
| instr_bb_entry | 102234 |
| instr_func | 102234 |
| instr_successor | 101521 |
| instr_pos | 95734 |
| constant | 86971 |
| constant_has_type | 86971 |
| constant_has_value | 86971 |
| constant_hashes_to | 86971 |
| subset.var_points_to | 84793 |
| constant_in_func_name | 81661 |
| call_instr_arg | 80616 |
| instr_assigns_to | 61012 |
| constant_to_int | 60265 |
| integer_constant | 46742 |
| subset.ptr_points_to | 29144 |

## Command
```bash
timeout -s KILL -k 5 21600 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc'"'"''
```
