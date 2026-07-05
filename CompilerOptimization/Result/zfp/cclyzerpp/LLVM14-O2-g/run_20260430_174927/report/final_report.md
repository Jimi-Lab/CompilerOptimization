# cclyzer++ Scan Final Report

## Metadata
- target: zfp
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc
- docker_image: paperexperiment/cclyzerpp-dev:llvm14-dbgdeclare-nullguard
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927
- status: reported
- return_code: 0
- elapsed_sec: 289

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
| MissingDebugLoc | 1000 |
| TailCallSite | 602 |
| PointerObjectFanout | 4 |

## Top Candidates
| kind | metric | file | line | function | subject | detail |
| --- | ---: | --- | ---: | --- | --- | --- |
| AliasBucketFanout | 2628 | NA | 0 | NA | *heap_alloc@main[i8* %443][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 2628 | NA | 0 | NA | *typed_heap_alloc@main[i64* %443][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 2627 | NA | 0 | NA | *heap_alloc@main[i8* %558][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 2627 | NA | 0 | NA | *typed_heap_alloc@main[i64* %558][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *heap_alloc@main[i8* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *heap_alloc@main[i8* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[double* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[float* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[i32* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[i64* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[double* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[float* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[i32* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[i64* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[i8* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[<2 x float>* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[<2 x double>* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[<4 x float>* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[<2 x i32>* %412][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[i8* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[<2 x float>* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[<2 x double>* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[<4 x float>* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1828 | NA | 0 | NA | *typed_heap_alloc@main[<2 x i32>* %652][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1626 | NA | 0 | NA | *heap_alloc@main[i8* %558][16] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1626 | NA | 0 | NA | *heap_alloc@main[i8* %558][24] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1626 | NA | 0 | NA | *heap_alloc@main[i8* %558][32] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1626 | NA | 0 | NA | *heap_alloc@main[i8* %558][40] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1626 | NA | 0 | NA | *heap_alloc@main[i8* %558][48] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1626 | NA | 0 | NA | *heap_alloc@main[i8* %558][56] | one allocation reaches many variables; candidate alias collapse hotspot |

## Largest Relations
| relation | rows |
| --- | ---: |
| subset.operand_points_to | 575290 |
| subset.var_points_to | 530565 |
| call_instr_arg | 132935 |
| instr_bb_entry | 103672 |
| instr_func | 103672 |
| instr_successor | 103392 |
| instr_pos | 96722 |
| variable | 92886 |
| variable_has_type | 92886 |
| variable_in_func_name | 92886 |
| variable_has_name | 91431 |
| constant | 73936 |
| constant_has_type | 73936 |
| constant_has_value | 73936 |
| constant_hashes_to | 73936 |
| constant_in_func_name | 73703 |
| instr_assigns_to | 47715 |
| func_constant | 44643 |
| func_constant_fn_name | 44643 |
| call_instr | 44581 |

## Command
```bash
timeout -s KILL -k 5 43200 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash paperexperiment/cclyzerpp-dev:llvm14-dbgdeclare-nullguard -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc'"'"''
```
