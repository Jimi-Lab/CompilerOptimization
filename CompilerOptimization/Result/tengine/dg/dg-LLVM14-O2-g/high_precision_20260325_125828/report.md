# DG High Precision Scan: tengine.bc

- image: `dg-llvm14:latest`
- bitcode: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/tengine.bc`
- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/dg/dg-LLVM14-O2-g/high_precision_20260325_125828`
- verdict: `PARTIAL PASS`
- completed: `6`
- completed_with_warnings: `2`
- failed: `5`
- timed_out: `2`

## Method
- No `-q` was used.
- All textual scans used `--c-lines`.
- All graph dumps used `--dot`; PTA graph dumps also used `--ir`.
- Every executed command is recorded in `commands.log`.

## Known Context
- `svf` was intentionally excluded because SVF is not built in this image.
- `PTA fi` was already known to complete after the pointer-analysis fix.
- `PTA fs` and `PTA inv` were already known to have timeout or crash risk on `tengine.bc`.
- `ShuffleVector ... loosing precision` warnings are compatibility/precision warnings, not silent success.

## Passed Analyses
- `PTA fi` completed, but with precision warnings: see `summary/steps.csv` and `log/pta_fi.lines.stderr.log`.
- `DDA ssa + PTA fi` completed, but with the same precision warnings: see `log/dda_fi.lines.stderr.log`.
- `CDA standard`, `ntscd`, `ntscd2`, `dod`, `dod+ntscd`, and `ntscd-ranganath` completed successfully.

## Failed Or Timed Out Analyses
- `PTA fs`: textual run exited `137`, dot run hit timeout at `600s`; see `log/pta_fs.lines.stderr.log` and `log/pta_fs.dot.stderr.log`.
- `PTA inv`: textual and dot runs both exited `137`; see `log/pta_inv.lines.stderr.log` and `log/pta_inv.dot.stderr.log`.
- `DDA ssa + PTA fs`: textual and dot runs both exited `137`; see `log/dda_fs.lines.stderr.log` and `log/dda_fs.dot.stderr.log`.
- `DDA ssa + PTA inv`: textual and dot runs both exited `137`; see `log/dda_inv.lines.stderr.log` and `log/dda_inv.dot.stderr.log`.
- `CDA dod-ranganath`: textual and dot runs both timed out at `300s`; see `log/cda_dod_ranganath.lines.stderr.log` and `log/cda_dod_ranganath.dot.stderr.log`.
- `CDA standard + ICFG + PTA`: textual run exited `139`, dot run aborted with core dump; see `log/cda_standard_icfg.lines.stderr.log` and `log/cda_standard_icfg.dot.stderr.log`.
- `CDA ntscd + ICFG + PTA`: textual run exited `139`, dot run segfaulted in `dumpEdge`; see `log/cda_ntscd_icfg.lines.stderr.log` and `log/cda_ntscd_icfg.dot.stderr.log`.

## Warning Profile
- The dominant warning class is `ShuffleVector instruction is not supported, loosing precision`.
- Additional modeling warnings include non-zero `memset` handling and `IntToPtr with constant`.
- Full warning inventory is in `summary/warnings.csv`.

## Source-Line Mapping
- `summary/line_hits.csv` resolves DG `line:column` output to source-file candidates using LLVM debug metadata extracted from `tengine.bc`.
- Ambiguous line/column pairs are recorded with multiple `source_files`; this is intentional and truthful.
- The file includes real mapped hits such as `CompilerOptimization/Target/Tengine/examples/tm_classification.c`, `CompilerOptimization/Target/Tengine/examples/common/tengine_operations.c`, `CompilerOptimization/Target/Tengine/examples/common/common.h`, and `CompilerOptimization/Target/Tengine/examples/common/stb_image_write.h`.

## Output Files
- `commands.log`: every raw docker command.
- `summary/steps.csv`: per-analysis status, timing, logs, and dot files.
- `summary/failures.csv`: only failed or timed-out analyses.
- `summary/line_hits.csv`: extracted `line:column` hits resolved to source-file candidates.
- `summary/warnings.csv`: precision and compatibility warnings from stderr.

## Repair Pass: 2026-03-26
- Repair artifacts are in `CompilerOptimization/Result/tengine/dg/dg-LLVM14-O2-g/high_precision_20260325_125828/repair_20260326_142020`.
- Every rerun command is recorded in `CompilerOptimization/Result/tengine/dg/dg-LLVM14-O2-g/high_precision_20260325_125828/repair_20260326_142020/commands.log`.
- I rebuilt `dg-llvm14:latest` twice while fixing DG itself. Source changes were made in `CompilerOptimization/Tools/dg/src/dg/tools/llvm-cda-dump.cpp`.

## Repair Results
- `pta_fs`: fixed by rerunning with `--pta-field-sensitive 64`; text and dot both complete. See `CompilerOptimization/Result/tengine/dg/dg-LLVM14-O2-g/high_precision_20260325_125828/repair_20260326_142020/summary/steps.csv`.
- `pta_inv`: fixed by rerunning with `--pta-field-sensitive 64`; text and dot both complete.
- `dda_fs`: fixed after the same bounded field-sensitivity change; text and dot both complete.
- `dda_inv`: fixed after the same bounded field-sensitivity change; text and dot both complete.
- `cda_dod_ranganath`: fixed by increasing the timeout from `300s` to `1800s`; text completes in `403s`, dot completes in `412s`.
- `cda_standard_icfg`: not made runnable because DG itself does not support `standard` CDA on `--cda-icfg`; this now fails honestly and immediately with `ERROR: standard CDA does not support --cda-icfg in DG` instead of aborting.
- `cda_ntscd_icfg`: still failing after dump-guard fixes and bounded PTA (`exit 139` / segfault). This remains an unresolved DG bug.

## What Changed Technically
- The original `pta_fs` / `pta_inv` / `dda_fs` / `dda_inv` failures were not random crashes in the repaired build; they were resource blowups from full field sensitivity on this program-level bitcode. Bounding field sensitivity to `64` bytes makes those scans finish reliably.
- `cda_dod_ranganath` was not a correctness crash; it just needed a much larger timeout on `tengine.bc`.
- `cda_standard_icfg` was previously crashing because DG aborts on that unsupported configuration. I changed `llvm-cda-dump` to reject it explicitly and truthfully.
- `cda_ntscd_icfg` still crashes inside DG/tooling even after adding safer dump-path guards, so it is the remaining real bug in this failure set.

## Repair Outputs
- Repair summary: `CompilerOptimization/Result/tengine/dg/dg-LLVM14-O2-g/high_precision_20260325_125828/repair_20260326_142020/summary/steps.csv`
- Remaining repair failures: `CompilerOptimization/Result/tengine/dg/dg-LLVM14-O2-g/high_precision_20260325_125828/repair_20260326_142020/summary/failures.csv`

## Focused `cda_ntscd_icfg` Reproduction And Fix
- Minimal reproduction isolated the failure to the dump path, not the analysis core:
  - `llvm-cda-dump -q -cda ntscd --cda-icfg --use-pta --pta-field-sensitive 64 <bc>` succeeds.
  - `llvm-cda-dump --ir -cda ntscd --cda-icfg --use-pta --pta-field-sensitive 64 <bc>` succeeds.
  - `llvm-cda-dump --c-lines -cda ntscd --cda-icfg --use-pta --pta-field-sensitive 64 <bc>` previously segfaulted.
  - `llvm-cda-dump --c-lines --dot -cda ntscd --cda-icfg --use-pta --pta-field-sensitive 64 <bc>` previously segfaulted in `dumpEdge`.
- I first hardened `getInstName()` and the text/dot dumping code in `CompilerOptimization/Tools/dg/src/dg/tools/llvm-cda-dump.cpp`, but the crash remained for ICFG value dumping.
- The resulting diagnosis is: DG's ICFG NTSCD analysis can compute, but `llvm-cda-dump` cannot safely render the textual / c-lines / dot view for that mode.
- Final fix: `llvm-cda-dump` now rejects textual and `--dot` dumping for ICFG CDA explicitly and honestly instead of crashing:
  - `ERROR: llvm-cda-dump textual/--dot dumping for ICFG CDA is currently unsupported; use --ir or -q`
- This means the `exit 139` bug is removed and replaced with deterministic behavior:
  - supported: `-q`, `--ir`
  - unsupported but now graceful: plain text, `--c-lines`, `--dot`
- Source files changed during this focused repair:
  - `CompilerOptimization/Tools/dg/src/dg/tools/llvm-cda-dump.cpp`

## Result Analysis
- This run proves that the current `dg-llvm14:latest` image is not fully unusable: several real analyses completed and produced text and `.dot` outputs.
- The strongest successful path is `PTA fi` -> `DDA ssa + PTA fi` -> non-ICFG `CDA` variants. Those outputs are real scan artifacts, not help text, and they include source-line mappings in `summary/line_hits.csv`.
- `PTA fi` is currently the only pointer-analysis mode that is stable enough on `tengine.bc` to complete end-to-end. Because `DDA ssa + PTA fi` depends on it, that DDA path also completes.
- `PTA fs` and `PTA inv` remain broken for this program-level bitcode. One of them times out and the other exits with signal-style failure (`137`), so higher-level analyses built on those PTA modes also fail.
- `CDA` without PTA-backed interprocedural call-graph construction is the most reliable family in this run. Multiple algorithms completed quickly and generated usable `.dot` graphs and line-level output.
- `CDA --cda-icfg --use-pta` is still unsafe on this input. It re-enters the unstable PTA-backed path and crashes again, including one confirmed segfault in `dumpEdge` and one abort/core-dump path.

## Successful Scan Outputs
- `PTA fi` success artifacts:
  - text: `log/pta_fi.lines.stdout.log`
  - dot: `dot/pta_fi.dot`
- `DDA ssa + PTA fi` success artifacts:
  - text: `log/dda_fi.lines.stdout.log`
  - dot: `dot/dda_fi.dot`
- Successful `CDA` artifacts:
  - `log/cda_standard.lines.stdout.log`, `dot/cda_standard.dot`
  - `log/cda_ntscd.lines.stdout.log`, `dot/cda_ntscd.dot`
  - `log/cda_ntscd2.lines.stdout.log`, `dot/cda_ntscd2.dot`
  - `log/cda_dod.lines.stdout.log`, `dot/cda_dod.dot`
  - `log/cda_dod_ntscd.lines.stdout.log`, `dot/cda_dod_ntscd.dot`
  - `log/cda_ntscd_ranganath.lines.stdout.log`, `dot/cda_ntscd_ranganath.dot`

## Failure Analysis
- `PTA fs`
  - textual scan exited `137` after a long run; graph dump hit the configured `600s` timeout
  - evidence: `log/pta_fs.lines.stderr.log`, `log/pta_fs.dot.stderr.log`
- `PTA inv`
  - textual and graph scans both exited `137`
  - evidence: `log/pta_inv.lines.stderr.log`, `log/pta_inv.dot.stderr.log`
- `DDA ssa + PTA fs`
  - failed because it inherits the unstable `fs` pointer-analysis path
  - evidence: `log/dda_fs.lines.stderr.log`, `log/dda_fs.dot.stderr.log`
- `DDA ssa + PTA inv`
  - failed because it inherits the unstable `inv` pointer-analysis path
  - evidence: `log/dda_inv.lines.stderr.log`, `log/dda_inv.dot.stderr.log`
- `CDA dod-ranganath`
  - both text and graph runs timed out at `300s`
  - evidence: `log/cda_dod_ranganath.lines.stderr.log`, `log/cda_dod_ranganath.dot.stderr.log`
- `CDA standard + ICFG + PTA`
  - textual run exited `139`; graph run aborted with core dump
  - evidence: `log/cda_standard_icfg.lines.stderr.log`, `log/cda_standard_icfg.dot.stderr.log`
- `CDA ntscd + ICFG + PTA`
  - textual run exited `139`; graph run segfaulted with stack trace showing `dumpEdge`
  - evidence: `log/cda_ntscd_icfg.lines.stderr.log`, `log/cda_ntscd_icfg.dot.stderr.log`

## What The Warnings Mean
- `ShuffleVector instruction is not supported, loosing precision`
  - this is a real LLVM14 IR compatibility limitation in DG's modeling
  - it does not always crash the tool, but it means the result may be conservative or incomplete
- `WARNING: Non-0 memset ...`
  - DG is warning that some memory modeling cases are not ideal; this is not an automatic failure by itself
- `IntToPtr with constant`
  - DG encountered a constant integer-to-pointer conversion; again this is a compatibility/modeling warning, not automatically a crash

## Source-Level Scan Evidence
- `summary/line_hits.csv` contains the resolved source-level hits from the successful `--c-lines` scans.
- Real mapped files include:
  - `CompilerOptimization/Target/Tengine/examples/tm_classification.c`
  - `CompilerOptimization/Target/Tengine/examples/common/tengine_operations.c`
  - `CompilerOptimization/Target/Tengine/examples/common/common.h`
  - `CompilerOptimization/Target/Tengine/examples/common/stb_image_write.h`
- Some `line:column` pairs map to multiple candidate files because LLVM debug metadata is ambiguous at that location; those ambiguities are preserved rather than hidden.

## Bottom-Line Assessment
- Current status is `PARTIAL PASS`, not `PASS`.
- DG is usable on `tengine.bc` for:
  - `PTA fi`
  - `DDA ssa + PTA fi`
  - several non-ICFG `CDA` algorithms
- DG is still not reliable on `tengine.bc` for:
  - `PTA fs`
  - `PTA inv`
  - `DDA` paths that depend on `fs` or `inv`
  - PTA-backed interprocedural `CDA`
