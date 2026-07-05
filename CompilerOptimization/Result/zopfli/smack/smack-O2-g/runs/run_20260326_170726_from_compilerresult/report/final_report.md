# Zopfli SMACK O2-g Report (CompilerResult BC)

## Environment

- Image: `smackers/smack:latest-full`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260326_170726_from_compilerresult`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/artifacts/zopfli_O2_g.bc`
- Tool versions:
  - `Ubuntu clang version 13.0.1-2ubuntu2.2`
  - `Ubuntu LLVM version 13.0.1`
  - `Ubuntu LLVM version 13.0.1`
  - `SMACK version 2.8.0`
  - `/home/user/.dotnet/tools/corral`
  - `/home/user/.dotnet/tools/boogie`
  - `/usr/bin/z3`

## Input BC Validation

- main_symbol: `present`
- undefined_symbol_count: `21`

## Artifacts

- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260326_170726_from_compilerresult/artifacts/smack.init.bc`
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260326_170726_from_compilerresult/artifacts/smack.final.ll`
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260326_170726_from_compilerresult/artifacts/smack.bpl`
- `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2-g/runs/run_20260326_170726_from_compilerresult/artifacts/undefined_symbols.txt`

## 8-Case Scan Matrix

| mode      | check            | enc               | unroll | verifier | exit | result   | elapsed |
| --------- | ---------------- | ----------------- | -----: | -------- | ---: | -------- | ------: |
| translate | memory-safety    | na                |      8 | default  |    0 | unknown  |       2 |
| verify    | assertions       | unbounded-integer |      8 | default  |    0 | verified |      66 |
| verify    | memory-safety    | unbounded-integer |      8 | default  |    2 | error    |    1067 |
| verify    | integer-overflow | unbounded-integer |      8 | default  |    0 | verified |      57 |
| verify    | memory-safety    | unbounded-integer |     16 | default  |    2 | error    |    1070 |
| verify    | assertions       | bit-vector        |      8 | default  |    1 | error    |       5 |
| verify    | memory-safety    | bit-vector        |      8 | default  |    1 | error    |       6 |
| verify    | integer-overflow | bit-vector        |      8 | default  |    1 | error    |       5 |
| verify    | memory-safety    | unbounded-integer |      8 | svcomp   |  126 | error    |    1882 |

## Failure Categories

- SMACK found an error: invalid pointer dereference.
- Timed out during normal inlining.
- Traceback (most recent call last):
- no-key-message

## Interpretation Notes

- This template scans a prebuilt CompilerResult BC instead of rebuilding inside Result.
- `verified` only means safe within the given unroll bound.
- `bit-vector` runs are more precise but more failure-prone in the backend.
