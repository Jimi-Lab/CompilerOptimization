# Verification: paper-zfp-phasar-11

## Verdict

- label: `exact`
- verified_file: `CompilerOptimization/Target/zfp/include/zfp/bitstream.inl`
- verified_line: `244`
- verified_source_text: `if (++s->bits == wsize) {`

## Checks

- [x] Raw artifact line/row matches `input.json`.
- [x] Reported location invalidity is independently confirmed.
- [x] IR instruction and debug metadata are located.
- [x] Recovered line is checked against the source tree.
- [x] If inline is claimed, caller/callee attribution is separated.
- [x] If evidence is insufficient, `unrecoverable` is justified rather than guessed.

## Evidence Notes

- `psr-report.txt` use block 32 starts at raw report line 472 and reports `Variable(s): s, s`, `Line: 244`, source text `if (++s->bits == wsize) {`, function `encode_ints_uint32.29`, and file `/work/PaperExperiment/CompilerOptimization/Target/zfp/src/template/encode.c`.
- The reported file/line pair is valid but mismatched: `CompilerOptimization/Target/zfp/src/template/encode.c:244` is `if (size <= 64)`, not the reported source text.
- The reported source text exactly exists at `CompilerOptimization/Target/zfp/include/zfp/bitstream.inl:244`, inside the inline helper `stream_write_bit`.
- In the local O2-g `.ll`, the corresponding instruction in `encode_ints_uint32.29` is `%256 = add i64 %250, 1, !dbg !7903`. `!7903 = !DILocation(line: 244, column: 7, scope: !7766, inlinedAt: !7899)`.
- `!7766` is a lexical block in `stream_write_bit`, whose DISubprogram `!7755` and file `!119` are `Target/zfp/include/zfp/bitstream.inl`; this is the source location of the executable statement.
- The inline chain is `bitstream.inl:244` inlined at `encode.c:198` (`stream_write_bit(&s, !!x)`), which is in turn inlined at `encode.c:252` into `encode_ints_uint32.29`.
- The reported file `encode.c` is explained by the following `llvm.dbg.value`: `%256` is recorded as a fragment of local variable `s` (`!7836`), and `!7836` is declared in `encode_few_ints_prec_uint32` at `Target/zfp/src/template/encode.c:183`. Phasar's `getFilePathFromIR` prefers this `DILocalVariable` file when an instruction is used by debug metadata.

## Paper Use

- include_in_main_table: `yes`
- include_as_failure_boundary: `yes`
- caveats: `Only O2-g Phasar IFDS-uninit evidence is present under the local zfp/phasar result tree; no local O0/O2-noinline Phasar zfp run was found for cross-universe comparison. Treat this as a report/source-mapping failure triggered by optimized inline debug metadata, not as evidence for or against a real source-level uninitialized-use bug.`
