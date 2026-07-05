# Verification: paper-zfp-phasar-12

## Verdict

- label: `exact`
- verified_file: `CompilerOptimization/Target/zfp/src/template/revencode.c`
- verified_line: `26`
- verified_source_text: `w -= z; z -= y;`

## Checks

- [x] Raw artifact line/row matches `input.json`.
- [x] Reported location invalidity is independently confirmed.
- [x] IR instruction and debug metadata are located.
- [x] Recovered line is checked against the source tree.
- [x] If inline is claimed, caller/callee attribution is separated.
- [x] If evidence is insufficient, `unrecoverable` is justified rather than guessed.

## Evidence Notes

- `psr-report.txt` use block 168 starts at raw report line 2925 and reports `Variable(s): z, x, z`, `Line: 26`, source text `w -= z; z -= y;`, function `zfp_encode_block_float_2`, and file `/work/PaperExperiment/CompilerOptimization/Target/zfp/src/template/encode.c`.
- The reported file/line pair is valid but mismatched: `CompilerOptimization/Target/zfp/src/template/encode.c:26` is only `}`, not the reported source text.
- The reported source text exactly exists at `CompilerOptimization/Target/zfp/src/template/revencode.c:26`, inside `rev_fwd_lift_int32`.
- In the local O2-g `.ll`, the corresponding instruction is `%264 = sub i32 %262, %263, !dbg !12191`. `!12191 = !DILocation(line: 26, column: 13, scope: !12177, inlinedAt: !12185)`.
- `!12177` is the DISubprogram `rev_fwd_lift_int32` with file `!5567`, and `!5567` is `Target/zfp/src/template/revencode.c`.
- The reported `encode.c` file is explained by `%264` having multiple `llvm.dbg.value` users. In addition to `revencode.c` variables such as `z` and `x`, `%264` is later used as `metadata !12208`, where `!12208` is local variable `x` in `int2uint_int32`, file `!5606 = Target/zfp/src/template/encode.c`.
- Phasar's `getFilePathFromIR` prefers a `DILocalVariable` file when an instruction is used by debug metadata. Since `getDbgVarIntrinsic()` returns only one metadata user, `%264` can be reported with the file of a later inline/debug variable rather than with the instruction's own `DILocation` file.

## Paper Use

- include_in_main_table: `yes`
- include_as_failure_boundary: `yes`
- caveats: `Only O2-g Phasar IFDS-uninit evidence is present under the local zfp/phasar result tree; no local O0/O2-noinline Phasar zfp run was found for cross-universe comparison. Treat this as a report/source-mapping failure triggered by optimized inline debug metadata, not as evidence for or against a real source-level uninitialized-use bug.`
