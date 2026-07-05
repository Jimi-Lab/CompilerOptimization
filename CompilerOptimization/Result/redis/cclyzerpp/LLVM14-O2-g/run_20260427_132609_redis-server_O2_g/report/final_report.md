# cclyzer++ Scan Final Report

## Metadata
- target: redis
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/artifacts/redis-server_O2_g.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/redis/cclyzerpp/LLVM14-O2-g/run_20260427_132609_redis-server_O2_g
- status: tool failure
- return_code: 139
- elapsed_sec: 263

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
| constant | 220347 |
| constant_has_value | 218479 |
| constant_hashes_to | 218225 |
| constant_has_type | 217918 |
| variable | 156847 |
| variable_has_name | 155882 |
| variable_in_func_name | 154507 |
| variable_has_type | 151892 |
| instr_bb_entry | 139707 |
| instr_successor | 138939 |
| instr_func | 135448 |
| instr_pos | 130010 |
| constant_in_func_name | 127801 |
| call_instr_arg | 114026 |
| constant_to_int | 101750 |
| integer_constant | 87821 |
| instr_assigns_to | 75215 |
| call_instr_func_operand | 42051 |
| func_constant_fn_name | 40808 |
| func_constant | 38060 |

## Command
```bash
timeout -s KILL -k 5 21600 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/redis/cclyzerpp/LLVM14-O2-g/run_20260427_132609_redis-server_O2_g/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/artifacts/redis-server_O2_g.bc'"'"''
```
