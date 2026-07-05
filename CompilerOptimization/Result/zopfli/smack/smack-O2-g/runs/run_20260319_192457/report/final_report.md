# Zopfli SMACK O2-g Report

## Environment
- Image: `smackers/smack:latest-full`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260319_192457`
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zopfli`
- Tool versions:
  - `Ubuntu clang version 13.0.1-2ubuntu2.2`
  - `Ubuntu LLVM version 13.0.1`
  - `Ubuntu LLVM version 13.0.1`
  - `SMACK version 2.8.0`
  - `/home/user/.dotnet/tools/corral`
  - `/home/user/.dotnet/tools/boogie`
  - `/usr/bin/z3`

## Compile Compliance
- Build pipeline rewrites Makefile `-O3` to `-O2 -g` in run work copy before compile.
- Object-level BC generation explicitly uses `clang-13 -O2 -g -emit-llvm -c`.
- No `-DNDEBUG` and no `RelWithDebInfo` are used in this run.

## Artifacts
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260319_192457/artifacts/zopfli_O2_g.bc`
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260319_192457/artifacts/zopfli_O2_g.ll`
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260319_192457/artifacts/bc_files.list`
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260319_192457/artifacts/smack.init.bc`
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260319_192457/artifacts/smack.final.ll`
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260319_192457/artifacts/smack.bpl`

## Scan Matrix Status
| mode | check | enc | unroll | verifier | exit | result | elapsed |
|---|---|---|---:|---|---:|---|---:|
| translate | memory-safety | na | 8 | default | 0 | unknown | 2 |
| verify | assertions | unbounded-integer | 8 | default | 0 | verified | 54 |
| verify | assertions | unbounded-integer | 8 | svcomp | 0 | verified | 14 |
| verify | assertions | unbounded-integer | 16 | default | 0 | verified | 53 |
| verify | assertions | unbounded-integer | 16 | svcomp | 0 | verified | 13 |
| verify | assertions | bit-vector | 8 | default | 1 | error | 4 |
| verify | assertions | bit-vector | 8 | svcomp | 1 | error | 4 |
| verify | assertions | bit-vector | 16 | default | 1 | error | 4 |
| verify | assertions | bit-vector | 16 | svcomp | 1 | error | 4 |
| verify | memory-safety | unbounded-integer | 8 | default | 2 | error | 1048 |
| verify | memory-safety | unbounded-integer | 8 | svcomp | 126 | error | 1882 |
| verify | memory-safety | unbounded-integer | 16 | default | 2 | error | 997 |
| verify | memory-safety | unbounded-integer | 16 | svcomp | 126 | error | 1882 |
| verify | memory-safety | bit-vector | 8 | default | 1 | error | 5 |
| verify | memory-safety | bit-vector | 8 | svcomp | 1 | error | 5 |
| verify | memory-safety | bit-vector | 16 | default | 1 | error | 5 |
| verify | memory-safety | bit-vector | 16 | svcomp | 1 | error | 5 |
| verify | integer-overflow | unbounded-integer | 8 | default | 0 | verified | 54 |
| verify | integer-overflow | unbounded-integer | 8 | svcomp | 0 | verified | 14 |
| verify | integer-overflow | unbounded-integer | 16 | default | 0 | verified | 53 |
| verify | integer-overflow | unbounded-integer | 16 | svcomp | 0 | verified | 14 |
| verify | integer-overflow | bit-vector | 8 | default | 1 | error | 4 |
| verify | integer-overflow | bit-vector | 8 | svcomp | 1 | error | 4 |
| verify | integer-overflow | bit-vector | 16 | default | 1 | error | 4 |
| verify | integer-overflow | bit-vector | 16 | svcomp | 1 | error | 4 |

## Failure Categories
- SMACK found an error: invalid pointer dereference.
- Timed out during normal inlining.
- Traceback (most recent call last):

## Next Steps
- Increase `--time-limit` or split checks if heavy combinations timeout.
- If verifier backend errors appear, use `smackers/smack:latest-full` and verify `corral/boogie/z3` in PATH.
- Re-run the same matrix on additional projects after confirming stable backend behavior.
