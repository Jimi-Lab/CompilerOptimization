# cclyzer++ Scan Final Report

## Metadata
- target: tengine
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/tengine.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/cclyzerpp/LLVM14-O2-g/run_20260427_132038_tengine
- status: reported
- return_code: 0
- elapsed_sec: 184

## Important Interpretation Note
- cclyzer++ is a global pointer-analysis engine. Rows in `extract/candidates.tsv` are high-signal candidate anomalies for manual review, not verified CWE bug reports.
- Promote a row to a paper case only after O0/O2/O2-noinline comparison and source/IR inspection.

## Candidate Counts
| kind | count |
| --- | ---: |
| CallgraphFanout | 1000 |
| PointsToFanout | 1000 |
| PhiMergeHotspot | 1000 |
| MissingDebugLoc | 1000 |
| AliasBucketFanout | 994 |
| TailCallSite | 867 |
| PointerObjectFanout | 21 |

## Top Candidates
| kind | metric | file | line | function | subject | detail |
| --- | ---: | --- | ---: | --- | --- | --- |
| AliasBucketFanout | 3745 | NA | 0 | NA | *stack_alloc@stbi_load[%struct.stbi__context* %6][0].?/8[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 2152 | NA | 0 | NA | *stack_alloc@stbi_load[%struct.stbi__context* %6][0].?/8 | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1895 | NA | 0 | NA | *global_alloc@stbi__stdio_read | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1686 | NA | 0 | NA | *unknown* | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 900 | NA | 0 | NA | *heap_alloc@stbi__parse_png_file[i8* %906][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 900 | NA | 0 | NA | *typed_heap_alloc@stbi__parse_png_file[i16* %906][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 900 | NA | 0 | NA | *typed_heap_alloc@stbi__parse_png_file[i8* %906][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 891 | NA | 0 | NA | *heap_alloc@stbi__parse_png_file[i8* %736][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 891 | NA | 0 | NA | *typed_heap_alloc@stbi__parse_png_file[i16* %736][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 891 | NA | 0 | NA | *typed_heap_alloc@stbi__parse_png_file[i8* %736][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 885 | NA | 0 | NA | *heap_alloc@stbi__create_png_image_raw[i8* %46][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 885 | NA | 0 | NA | *typed_heap_alloc@stbi__create_png_image_raw[i16* %46][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 885 | NA | 0 | NA | *typed_heap_alloc@stbi__create_png_image_raw[i8* %46][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| PointsToFanout | 534 | llvm-link | 0 | stbi__compute_transparency | %121 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 498 | llvm-link | 0 | stbi__compute_transparency | %134 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 489 | llvm-link | 0 | stbi__compute_transparency | %146 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 456 | llvm-link | 0 | stbi__compute_transparency16 | %102 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 453 | llvm-link | 0 | stbi__de_iphone | %132 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 435 | llvm-link | 0 | stbi__compute_transparency16 | %48 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 435 | llvm-link | 0 | stbi__compute_transparency16 | %35 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 435 | llvm-link | 0 | stbi__compute_transparency | %150 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 435 | llvm-link | 0 | stbi__de_iphone | %57 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 420 | llvm-link | 0 | stbi__compute_transparency16 | %115 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 417 | llvm-link | 0 | stbi__compute_transparency16 | %109 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 417 | llvm-link | 0 | stbi__compute_transparency16 | %43 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 417 | llvm-link | 0 | stbi__compute_transparency | %168 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 417 | llvm-link | 0 | stbi__de_iphone | %137 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 417 | llvm-link | 0 | stbi__de_iphone | %92 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 411 | llvm-link | 0 | stbi__compute_transparency16 | %127 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 402 | llvm-link | 0 | stbi__compute_transparency16 | %121 | variable has a broad points-to set; candidate over-approximation / phi merge |

## Largest Relations
| relation | rows |
| --- | ---: |
| subset.operand_points_to | 61158 |
| subset.var_points_to | 53200 |
| variable | 48768 |
| variable_has_type | 48768 |
| variable_in_func_name | 48768 |
| variable_has_name | 48301 |
| instr_bb_entry | 46512 |
| instr_func | 46512 |
| instr_successor | 46343 |
| instr_pos | 42574 |
| constant | 31436 |
| constant_has_type | 31436 |
| constant_has_value | 31436 |
| constant_hashes_to | 31436 |
| constant_in_func_name | 30638 |
| call_instr_arg | 29559 |
| instr_assigns_to | 27654 |
| constant_to_int | 26040 |
| integer_constant | 18267 |
| subset.ptr_points_to | 14383 |

## Command
```bash
timeout -s KILL -k 5 21600 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/tengine/cclyzerpp/LLVM14-O2-g/run_20260427_132038_tengine/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/tengine.bc'"'"''
```
