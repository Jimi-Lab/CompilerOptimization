# DG High Precision Scan: lepton_O2_g.bc

- image: `dg-llvm14:latest`
- bitcode: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc`
- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/dg/dg-LLVM14-O2-g/high_precision_20260402_153121`
- verdict: `PARTIAL PASS`
- completed: `7`
- completed_with_warnings: `2`
- failed: `7`
- timed_out: `1`

## Method
- No hidden steps and no omitted failures.
- No `-q` in the main matrix except the diagnostic-only ICFG NTSCD check.
- All textual scans used `--c-lines`.
- All graph dumps used `--dot`; PTA graph dumps also used `--ir`.
- Every executed command is recorded in `commands.log`.

## Output Files
- `commands.log`: every raw docker command.
- `summary/steps.csv`: per-analysis status, timing, logs, and dot files.
- `summary/failures.csv`: only failed or timed-out analyses.
- `summary/line_hits.csv`: line/column hits resolved to source-file candidates from LLVM debug info.
- `summary/warnings.csv`: precision and compatibility warnings from stderr.

## Truthful Result Summary
- Successful:
  - `CDA standard`
  - `CDA ntscd`
  - `CDA ntscd2`
  - `CDA dod`
  - `CDA dod+ntscd`
  - `CDA ntscd-ranganath`
  - `CDA dod-ranganath`
- Successful with warnings:
  - `CDA ntscd --cda-icfg --use-pta --pta-field-sensitive 64 -q`
  - `CDA ntscd --cda-icfg --use-pta --pta-field-sensitive 64 --ir`
- Failed / timed out:
  - `PTA fi`: text completed with warnings, but `--ir --dot` timed out at `900s`
  - `PTA fs --pta-field-sensitive 64`: failed (`exit 137`)
  - `PTA inv --pta-field-sensitive 64`: failed (`exit 137`)
  - `DDA ssa + PTA fi`: failed (`exit 137`) with `[RWG] error: could not determine the called function in a call via pointer:`
  - `DDA ssa + PTA fs --pta-field-sensitive 64`: failed (`exit 137`)
  - `DDA ssa + PTA inv --pta-field-sensitive 64`: failed (`exit 137`)
  - `CDA standard --cda-icfg`: unsupported, explicit error
  - `CDA ntscd --cda-icfg` textual/`--c-lines`/`--dot`: unsupported, explicit error

## Warning Profile
- Key warnings are preserved in `summary/warnings.csv`, notably:
  - `IntToPtr with constant`
  - `WARNING: Non-0 memset`
  - `[pta] UNHANDLED` entries (`insertvalue` etc.)
  - `ShuffleVector instruction is not supported, loosing precision`

## Source-Line Mapping
- `summary/line_hits.csv` contains mapped source-line candidates from `--c-lines` output.
- Examples include real lepton files such as:
  - `CompilerOptimization/Target/lepton/src/io/MemReadWriter.hh`
  - `CompilerOptimization/Target/lepton/src/io/BoundedMemWriter.hh`
  - `CompilerOptimization/Target/lepton/src/lepton/thread_handoff.cc`
  - `CompilerOptimization/Target/lepton/src/lepton/concat.cc`

## Bottom Line
- DG is only partially usable for this whole-program `lepton_O2_g.bc` sample.
- CDA (non-ICFG) is broadly runnable here under current budgets.
- PTA/DDA remain unstable: `fs/inv` and all DDA variants failed, and `pta fi` graph dump timed out.
- ICFG CDA follows the current DG limitation policy:
  - `standard --cda-icfg` unsupported
  - `ntscd --cda-icfg` usable only in `-q` / `--ir`, not in textual/`--c-lines`/`--dot` mode.
