# cclyzer++ Scan Final Report

## Metadata
- target: masscan
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/cclyzerpp/LLVM14-O2-g/run_20260430_120006
- status: reported
- return_code: 0
- elapsed_sec: 2983

## Important Interpretation Note
- cclyzer++ is a global pointer-analysis engine. Rows in `extract/candidates.tsv` are high-signal candidate anomalies for manual review, not verified CWE bug reports.
- Promote a row to a paper case only after O0/O2/O2-noinline comparison and source/IR inspection.

## Candidate Counts
| kind | count |
| --- | ---: |
| CallgraphFanout | 1000 |
| PointsToFanout | 1000 |
| AliasBucketFanout | 1000 |
| PointerObjectFanout | 1000 |
| PhiMergeHotspot | 1000 |
| TailCallSite | 1000 |
| MissingDebugLoc | 1000 |

## Top Candidates
| kind | metric | file | line | function | subject | detail |
| --- | ---: | --- | ---: | --- | --- | --- |
| AliasBucketFanout | 1343 | NA | 0 | NA | *typed_heap_alloc@MALLOC[%struct.TCP_Control_Block* %4][0].?/0.?/0.?/0 | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1343 | NA | 0 | NA | *typed_heap_alloc@MALLOC[%struct.TCP_Control_Block* %4][0].?/0.?/0.?/0.?/0 | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1332 | NA | 0 | NA | *typed_heap_alloc@MALLOC[%struct.TCP_Control_Block* %4][0].?/0.?/0 | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1232 | NA | 0 | NA | *typed_heap_alloc@MALLOC[%struct.TCP_Control_Block* %4][0].?/0 | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1227 | NA | 0 | NA | *typed_heap_alloc@MALLOC[%struct.BannerOutput* %4][0].?/0 | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *heap_alloc@CALLOC[i8* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[i32* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[i64* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.ResetFilter* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.DedupEntry_IPv4* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.__pfring** %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.Adapter* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.Masscan** %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.rte_ring** %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.ServiceProbeMatch** %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.Banner1* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.pcap** %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.stack_t* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.Output* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.DedupTable* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.NmapServiceProbeList* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[i8** %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.PayloadsUDP* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.Range* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.BannerOutput* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[%struct.BannerOutput** %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1125 | NA | 0 | NA | *typed_heap_alloc@CALLOC[i8* %14] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1102 | NA | 0 | NA | *heap_alloc@REALLOCARRAY[i8* %16] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1102 | NA | 0 | NA | *typed_heap_alloc@REALLOCARRAY[i32* %16] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1102 | NA | 0 | NA | *typed_heap_alloc@REALLOCARRAY[i64* %16] | one allocation reaches many variables; candidate alias collapse hotspot |

## Largest Relations
| relation | rows |
| --- | ---: |
| subset.ptr_points_to | 1665782 |
| subset.operand_points_to | 434666 |
| subset.var_points_to | 405367 |
| variable | 85491 |
| variable_has_type | 85491 |
| variable_in_func_name | 85491 |
| variable_has_name | 84103 |
| constant | 83509 |
| constant_has_type | 83509 |
| constant_has_value | 83509 |
| constant_hashes_to | 83509 |
| instr_bb_entry | 80358 |
| instr_func | 80358 |
| instr_successor | 79738 |
| instr_pos | 74557 |
| constant_in_func_name | 73415 |
| call_instr_arg | 72213 |
| constant_to_int | 53257 |
| subset_lift.alloc_may_alias_ctx | 51423 |
| subset_lift.alloc_contains_ctx | 46211 |

## Command
```bash
timeout -s KILL -k 5 43200 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/masscan/cclyzerpp/LLVM14-O2-g/run_20260430_120006/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc'"'"''
```
