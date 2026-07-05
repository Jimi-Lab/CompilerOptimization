# cclyzer++ Scan Final Report

## Metadata
- target: lepton
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/cclyzerpp/LLVM14-O2-g/run_20260430_114650_lepton_O2_g
- status: timeout
- return_code: 137
- elapsed_sec: 10

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
| constant_hashes_to | 29439 |
| constant | 28104 |
| constant_has_value | 27044 |
| constant_has_type | 26137 |
| call_instr_arg | 25436 |
| instr_successor | 17497 |
| instr_pos | 17429 |
| instr_func | 16276 |
| constant_in_func_name | 15724 |
| variable | 14834 |
| variable_has_name | 14819 |
| constant_to_int | 14419 |
| instr_bb_entry | 14337 |
| variable_in_func_name | 12522 |
| variable_has_type | 12207 |
| integer_constant | 11944 |
| call_instr_func_operand | 7530 |
| call_instr | 7258 |
| func_constant | 6157 |
| func_constant_fn_name | 5828 |

## Command
```bash
timeout -s KILL -k 5 21600 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/lepton/cclyzerpp/LLVM14-O2-g/run_20260430_114650_lepton_O2_g/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc'"'"''
```
