# ZFP SMACK O2-g Report

## Input Information
- BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM13-O2-g/artifacts/zfp_O2_g.bc`
- Output dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/smack/smack-O2-g`
- Run dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/smack/smack-O2-g/runs/run_20260410_005715`
- Docker image: `smackers/smack:latest-full`
- main_symbol: `present`
- undefined_symbol_count: `23`

## Scan Matrix
| mode | check | encoding | unroll | verifier | timeout | exit | result | elapsed |
|---|---|---|---:|---|---:|---:|---|---:|
| translate | memory-safety | na | 10 | default | 2100 | 1 | backend failure | 6 |
| verify | assertions | unbounded-integer | 10 | default | 2100 | 1 | backend failure | 6 |
| verify | memory-safety | unbounded-integer | 10 | default | 2100 | 1 | backend failure | 5 |
| verify | integer-overflow | unbounded-integer | 10 | default | 2100 | 1 | backend failure | 5 |
| verify | memory-safety | unbounded-integer | 16 | default | 2100 | 1 | backend failure | 5 |
| verify | assertions | bit-vector | 10 | default | 2100 | 1 | backend failure | 5 |
| verify | memory-safety | bit-vector | 10 | default | 2100 | 1 | backend failure | 5 |
| verify | integer-overflow | bit-vector | 10 | default | 2100 | 1 | backend failure | 5 |
| verify | memory-safety | unbounded-integer | 10 | svcomp | 2100 | 1 | backend failure | 6 |

## Result Overview
- `verified`: 0
- `error`: 0
- `timeout`: 0
- `tool_failure`: 0
- `backend_failure`: 9
- `translation_failure`: 0
- `unknown`: 0

## Bug Candidates
- none

## Non-bug Failures
- `backend failure` check=`memory-safety` encoding=`na` unroll=`10` verifier=`default` -> Traceback (most recent call last):
- `backend failure` check=`assertions` encoding=`unbounded-integer` unroll=`10` verifier=`default` -> Traceback (most recent call last):
- `backend failure` check=`memory-safety` encoding=`unbounded-integer` unroll=`10` verifier=`default` -> Traceback (most recent call last):
- `backend failure` check=`integer-overflow` encoding=`unbounded-integer` unroll=`10` verifier=`default` -> Traceback (most recent call last):
- `backend failure` check=`memory-safety` encoding=`unbounded-integer` unroll=`16` verifier=`default` -> Traceback (most recent call last):
- `backend failure` check=`assertions` encoding=`bit-vector` unroll=`10` verifier=`default` -> Traceback (most recent call last):
- `backend failure` check=`memory-safety` encoding=`bit-vector` unroll=`10` verifier=`default` -> Traceback (most recent call last):
- `backend failure` check=`integer-overflow` encoding=`bit-vector` unroll=`10` verifier=`default` -> Traceback (most recent call last):
- `backend failure` check=`memory-safety` encoding=`unbounded-integer` unroll=`10` verifier=`svcomp` -> Traceback (most recent call last):

## Final Conclusion
- Verdict: `FAIL`
- No strong conclusions; tool/backend/translation issues dominate.
