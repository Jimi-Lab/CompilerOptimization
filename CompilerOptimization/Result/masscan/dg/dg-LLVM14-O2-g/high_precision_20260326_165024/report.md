# DG High Precision Scan: masscan_O2_g.bc

- image: `dg-llvm14:latest`
- bitcode: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc`
- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/dg/dg-LLVM14-O2-g/high_precision_20260326_165024`
- verdict: `PARTIAL PASS`
- completed: `7`
- completed_with_warnings: `0`
- failed: `5`
- timed_out: `4`
- unsupported_expected: `2`

## Method
- Followed the workflow from `CompilerOptimization/Result/tengine/dg/executor.md`.
- No `-q` for normal report steps; all textual runs use `--c-lines`.
- All graph runs use `--dot`; PTA dot runs also use `--ir`.
- Every command was logged in `commands.log` before execution.

## ICFG CDA policy
- `standard --cda-icfg` is treated as unsupported and expected to fail explicitly.
- `ntscd --cda-icfg --use-pta` is analysis-only (`-q` and `--ir`), while textual/c-lines/dot are treated as unsupported in this DG image.

## Repair Pass: 2026-03-31
- Ordered repair diagnostics are in `CompilerOptimization/Result/masscan/dg/dg-LLVM14-O2-g/high_precision_20260326_165024/repair_20260331_103410`.
- Every command from that pass is recorded in `CompilerOptimization/Result/masscan/dg/dg-LLVM14-O2-g/high_precision_20260326_165024/repair_20260331_103410/commands.log`.
- Repair summary: `CompilerOptimization/Result/masscan/dg/dg-LLVM14-O2-g/high_precision_20260326_165024/repair_20260331_103410/summary/steps.csv`

## What I Changed In DG
- `CompilerOptimization/Tools/dg/src/dg/lib/llvm/PointerAnalysis/Instructions.cpp`
  - aggregate and vector returns that do not contain pointers are no longer pessimistically modeled as `UNKNOWN_MEMORY`
  - this removes a clearly bogus source of PTA imprecision on programs that return plain `{i64, i64}`-style structs

## Truthful Repair Outcome
- `pta_fs`: still fails with `exit 137` after the DG fix; no stable repair found yet.
- `pta_inv`: still fails with `exit 137` after the DG fix; no stable repair found yet.
- `dda_fs`: still fails with `exit 137`; it remains blocked on the PTA fs failure.
- `dda_inv`: still fails with `exit 137`; it remains blocked on the PTA inv failure.
- `pta_fi`: still times out at `1200s` in quiet mode.
- `dda_fi`: still times out at `1200s` in quiet mode.
- `cda_ntscd_icfg_q`: still times out at `1200s`.
- `cda_ntscd_icfg_ir`: still times out at `1200s`.

## Interpretation
- The masscan failures are not just report-format issues. They remain real scalability / memory-pressure problems for DG on this whole-program LLVM14 bitcode.
- The aggregate-return source fix removed one obvious unsoundness source, but it did not by itself make the masscan PTA or DDA runs complete.
- In this repair pass, none of the originally failing or timing-out masscan steps were fully recovered.
