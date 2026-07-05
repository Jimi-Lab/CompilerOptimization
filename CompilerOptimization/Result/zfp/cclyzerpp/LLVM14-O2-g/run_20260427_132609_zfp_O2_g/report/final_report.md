# cclyzer++ Scan Final Report

## Metadata
- target: zfp
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260427_132609_zfp_O2_g
- status: tool failure
- return_code: 139
- elapsed_sec: 21

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
| call_instr_arg | 130419 |
| instr_successor | 101345 |
| instr_bb_entry | 98939 |
| instr_func | 95397 |
| instr_pos | 93187 |
| variable_has_type | 88839 |
| variable_in_func_name | 84936 |
| variable_has_name | 83977 |
| variable | 80989 |
| constant_in_func_name | 72715 |
| constant_has_value | 69877 |
| constant_has_type | 69748 |
| constant_hashes_to | 68530 |
| constant | 67560 |
| call_instr_func_operand | 44183 |
| func_constant_fn_name | 42751 |
| instr_assigns_to | 42276 |
| call_instr | 38945 |
| func_constant | 36095 |
| constant_to_int | 29277 |

## Command
```bash
timeout -s KILL -k 5 21600 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260427_132609_zfp_O2_g/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc'"'"''
```
