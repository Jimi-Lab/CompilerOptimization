# cclyzer++ Scan Final Report

## Metadata
- target: zopfli
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/cclyzerpp/LLVM14-O2-g/run_20260427_132038_zopfli_O2_g_zopfli_only
- status: reported
- return_code: 0
- elapsed_sec: 59

## Important Interpretation Note
- cclyzer++ is a global pointer-analysis engine. Rows in `extract/candidates.tsv` are high-signal candidate anomalies for manual review, not verified CWE bug reports.
- Promote a row to a paper case only after O0/O2/O2-noinline comparison and source/IR inspection.

## Candidate Counts
| kind | count |
| --- | ---: |
| CallgraphFanout | 1000 |
| MissingDebugLoc | 1000 |
| PhiMergeHotspot | 945 |
| PointsToFanout | 875 |
| AliasBucketFanout | 643 |
| TailCallSite | 303 |
| PointerObjectFanout | 160 |

## Top Candidates
| kind | metric | file | line | function | subject | detail |
| --- | ---: | --- | ---: | --- | --- | --- |
| PointerObjectFanout | 217 | NA | 0 | NA | *stack_alloc@main[i8** %3] | memory object has a broad points-to set |
| PointerObjectFanout | 217 | NA | 0 | NA | *stack_alloc@main[i8** %3][0] | memory object has a broad points-to set |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %1131 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %1122 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %1116 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %1066 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %1043 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %1033 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %1001 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %982 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %976 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %950 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %940 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %931 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %925 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %887 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %868 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %862 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %817 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %808 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %770 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %723 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %827 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %761 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %1091 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %877 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %714 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %733 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %802 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 216 | llvm-link | 0 | EncodeTree | %780 | variable has a broad points-to set; candidate over-approximation / phi merge |

## Largest Relations
| relation | rows |
| --- | ---: |
| subset.operand_points_to | 63964 |
| subset.var_points_to | 59525 |
| variable | 14124 |
| variable_has_type | 14124 |
| variable_in_func_name | 14124 |
| variable_has_name | 13753 |
| instr_bb_entry | 13672 |
| instr_func | 13672 |
| instr_successor | 13620 |
| instr_pos | 12715 |
| call_instr_arg | 10741 |
| constant | 9306 |
| constant_has_type | 9306 |
| constant_has_value | 9306 |
| constant_hashes_to | 9306 |
| constant_in_func_name | 9191 |
| instr_assigns_to | 7913 |
| constant_to_int | 5844 |
| integer_constant | 4626 |
| call_instr | 3713 |

## Command
```bash
timeout -s KILL -k 5 21600 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/zopfli/cclyzerpp/LLVM14-O2-g/run_20260427_132038_zopfli_O2_g_zopfli_only/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc'"'"''
```
