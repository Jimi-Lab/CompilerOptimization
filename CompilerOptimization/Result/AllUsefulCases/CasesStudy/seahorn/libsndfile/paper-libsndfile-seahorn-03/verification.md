# Verification: paper-libsndfile-seahorn-03

## Verdict

- label: `nearby`  <!-- exact | nearby | function-only | wrong | unrecoverable -->
- case_tag: `FP-LocationDrift`
- verified_file: `Target/libsndfile/src/GSM610/short_term.c`
- verified_line: `308`
- verified_source_text: `{   va [i]  = v [i] ;`

## Checks

- [x] Raw artifact line/row matches `input.json`.
- [x] Reported location invalidity is independently confirmed.
- [x] IR instruction and debug metadata are located.
- [x] Recovered line is checked against the source tree.
- [x] If inline is claimed, caller/callee attribution is separated.
- [x] If evidence is insufficient, `unrecoverable` is justified rather than guessed.

## Evidence Notes

- Raw SeaHorn row: `all_cases.csv` row 313, step 06 `smc_instrument`, reports `Target/libsndfile/src/GSM610/short_term.c:0:0`.
- Input bitcode universe: `LLVM14-O2-g`, command evidence records `clang-14 -O2 -g -std=gnu99` for `short_term.c`; no `-DNDEBUG`.
- IR anchor: `CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.ll:115507`.
- Metadata anchor: `!79763 = !DILocation(line: 0, scope: !79748)`, where `!79748` is `Fast_Short_term_synthesis_filtering` at source line 293.
- Recovery basis: `%51` consumes `%13`; `%13` is produced from `S->v[1]` with valid location `!79764 = line 308, column 13`, matching source `va [i] = v [i]`.
- Confidence is `nearby`, not `exact`, because the reported instruction itself has no statement-level DILocation and O2 vectorization merged array fragments across statements.
- No local SeaHorn O0 or O2-noinline run exists for libsndfile, so inline-specific attribution is not supported.

## Paper Use

- include_in_main_table: `yes`
- include_as_failure_boundary: `yes`
- caveats: `Use as a debug-location recovery / line-zero case. Do not present as a confirmed source-level undefined-read bug.`
