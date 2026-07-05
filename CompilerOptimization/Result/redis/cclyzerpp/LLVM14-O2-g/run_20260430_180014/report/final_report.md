# cclyzer++ Scan Final Report

## Metadata
- target: redis
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/artifacts/redis-server_O2_g.bc
- docker_image: paperexperiment/cclyzerpp-dev:llvm14-dbgdeclare-nullguard
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/redis/cclyzerpp/LLVM14-O2-g/run_20260430_180014
- status: timeout
- return_code: -9
- elapsed_sec: 43200

## Important Interpretation Note
- cclyzer++ is a global pointer-analysis engine. Rows in `extract/candidates.tsv` are high-signal candidate anomalies for manual review, not verified CWE bug reports.
- Promote a row to a paper case only after O0/O2/O2-noinline comparison and source/IR inspection.

## Candidate Counts
| kind | count |
| --- | ---: |

## Top Candidates
| kind | metric | file | line | function | subject | detail |
| --- | ---: | --- | ---: | --- | --- | --- |

## Largest Relations
| relation | rows |
| --- | ---: |
| constant | 484510 |
| constant_has_type | 484510 |
| constant_has_value | 484510 |
| constant_hashes_to | 484510 |
| variable | 478251 |
| variable_has_type | 478251 |
| variable_in_func_name | 478251 |
| variable_has_name | 471358 |
| instr_bb_entry | 431947 |
| instr_func | 431947 |
| instr_successor | 426971 |
| instr_pos | 406904 |
| constant_in_func_name | 396227 |
| call_instr_arg | 362049 |
| constant_to_int | 275889 |
| instr_assigns_to | 237340 |
| integer_constant | 226632 |
| func_constant | 136333 |
| func_constant_fn_name | 136333 |
| call_instr | 135021 |

## Command
```bash
timeout -s KILL -k 5 43200 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash paperexperiment/cclyzerpp-dev:llvm14-dbgdeclare-nullguard -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/redis/cclyzerpp/LLVM14-O2-g/run_20260430_180014/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/artifacts/redis-server_O2_g.bc'"'"''
```
