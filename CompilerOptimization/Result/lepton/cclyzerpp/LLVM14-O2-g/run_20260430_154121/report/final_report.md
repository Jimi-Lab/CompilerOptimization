# cclyzer++ Scan Final Report

## Metadata
- target: lepton
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/cclyzerpp/LLVM14-O2-g/run_20260430_154121
- status: reported
- return_code: 0
- elapsed_sec: 2475

## Important Interpretation Note
- cclyzer++ is a global pointer-analysis engine. Rows in `extract/candidates.tsv` are high-signal candidate anomalies for manual review, not verified CWE bug reports.
- Promote a row to a paper case only after O0/O2/O2-noinline comparison and source/IR inspection.

## Candidate Counts
| kind | count |
| --- | ---: |
| CallgraphFanout | 1000 |
| PointsToFanout | 1000 |
| PointerObjectFanout | 1000 |
| PhiMergeHotspot | 1000 |
| TailCallSite | 1000 |
| MissingDebugLoc | 1000 |
| AliasBucketFanout | 832 |

## Top Candidates
| kind | metric | file | line | function | subject | detail |
| --- | ---: | --- | ---: | --- | --- | --- |
| AliasBucketFanout | 7160 | NA | 0 | NA | *heap_alloc@_ZN8Sirikata11memmgr_initEmmmmb[i8* %12][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7160 | NA | 0 | NA | *heap_alloc@_ZN8Sirikata11memmgr_initEmmmmb[i8* %17][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7160 | NA | 0 | NA | *heap_alloc@_ZN8Sirikata11memmgr_initEmmmmb[i8* %24][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7160 | NA | 0 | NA | *typed_heap_alloc@_ZN8Sirikata11memmgr_initEmmmmb[%"struct.Sirikata::MemMgrState"* %24][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7160 | NA | 0 | NA | *typed_heap_alloc@_ZN8Sirikata11memmgr_initEmmmmb[%"struct.Sirikata::MemMgrState"* %12][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7160 | NA | 0 | NA | *typed_heap_alloc@_ZN8Sirikata11memmgr_initEmmmmb[%"struct.Sirikata::MemMgrState"* %17][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7159 | NA | 0 | NA | *global_alloc@EOI[*][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7159 | NA | 0 | NA | *global_alloc@g_dash[*][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[8][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[16][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[24][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[32][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[40][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[48][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[56][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[64][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[72][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7157 | NA | 0 | NA | *global_alloc@g_dash[80][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7141 | NA | 0 | NA | *global_alloc@.str.18.158[0][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7140 | NA | 0 | NA | *stack_alloc@_Z13run_benchmarkPcPhmii[%"class.std::__cxx11::basic_string"* %22][0].?/2.?/1[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@EOI[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@g_dash[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@.str.18.158[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@.str.18.158[*][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@EOI[0][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@g_dash[0][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@g_dash[96][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@_ZTV24ActualThreadPacketReader[0].?/0[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@_ZTV25VirtualThreadPacketReader[0].?/0[*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 7139 | NA | 0 | NA | *global_alloc@_ZTV19VP8ComponentEncoderI13VPXBoolReaderE[0].?/0[*] | one allocation reaches many variables; candidate alias collapse hotspot |

## Largest Relations
| relation | rows |
| --- | ---: |
| subset.operand_points_to | 1039781 |
| subset.var_points_to | 963961 |
| subset.ptr_points_to | 398639 |
| call_instr_arg | 237016 |
| constant | 167810 |
| constant_has_type | 167810 |
| constant_has_value | 167810 |
| constant_hashes_to | 167810 |
| instr_bb_entry | 163309 |
| instr_func | 163309 |
| instr_successor | 162672 |
| constant_in_func_name | 156962 |
| instr_pos | 155370 |
| variable | 141630 |
| variable_has_type | 141630 |
| variable_in_func_name | 141630 |
| variable_has_name | 137189 |
| constant_to_int | 100209 |
| func_constant | 80046 |
| func_constant_fn_name | 80046 |

## Command
```bash
timeout -s KILL -k 5 43200 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/lepton/cclyzerpp/LLVM14-O2-g/run_20260430_154121/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc'"'"''
```
