# Verification: paper-libsndfile-phasar-02

## Verdict

- label: `exact`
- verified_file: `CompilerOptimization/Target/libsndfile/src/GSM610/long_term.c`
- verified_line: `616`
- verified_source_text: `R = SASR_L (L_max << temp, 16) ;`

## Checks

- [x] Raw artifact line/row matches `input.json`.
- [x] Reported location invalidity is independently confirmed.
- [x] IR instruction and debug metadata are located.
- [x] Recovered line is checked against the source tree.
- [x] If inline is claimed, caller/callee attribution is separated.
- [x] If evidence is insufficient, `unrecoverable` is justified rather than guessed.

## Evidence Notes

- `psr-report.txt` use block 267 starts at raw report line 4688 and reports `Variable(s): L_max`, `Line: 616`, source text `R = SASR_L (L_max << temp, 16) ;`, function `Gsm_Long_Term_Predictor`, and file `/work/PaperExperiment/CompilerOptimization/Target/libsndfile/src/GSM610/gsm610_priv.h`.
- The reported file is invalid for that line: `CompilerOptimization/Target/libsndfile/src/GSM610/gsm610_priv.h` has 337 lines, so line 616 is out of range.
- The reported source text exactly exists in `CompilerOptimization/Target/libsndfile/src/GSM610/long_term.c:616`, inside `Calculation_of_the_LTP_parameters`, which is inlined into `Gsm_Long_Term_Predictor` at `long_term.c:884`.
- The O2-g `.ll` contains the reported instruction as `%2334 = shl i32 %2251, %2333, !dbg !80276` in the `Gsm_Long_Term_Predictor` body. `!80276 = !DILocation(line: 616, column: 20, scope: !80055, inlinedAt: !80102)`.
- `!80055` is `Calculation_of_the_LTP_parameters` with `file: !7292`, and `!7292` is `Target/libsndfile/src/GSM610/long_term.c`; `!80102` is the inlined-at call site `line: 884` in `Gsm_Long_Term_Predictor`.
- The header `gsm610_priv.h` is present in nearby debug metadata because `SASR_L` is an inline helper declared at `gsm610_priv.h:66`; this is the callee scope for the following `llvm.dbg.value` metadata, not the caller statement location.

## Paper Use

- include_in_main_table: `yes`
- include_as_failure_boundary: `yes`
- caveats: `Only O2-g Phasar IFDS-uninit evidence is present under the local libsndfile/phasar result tree; no local O0/O2-noinline Phasar libsndfile run was found for cross-universe recovery comparison. Treat the case as a location-attribution failure, not as evidence for or against a real source-level uninitialized-use bug.`
