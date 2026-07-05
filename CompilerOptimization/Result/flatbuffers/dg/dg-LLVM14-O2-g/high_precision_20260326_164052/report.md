# DG High Precision Scan: flatbuffers_flatc_O2_g.bc

- image: `dg-llvm14:latest`
- bitcode: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc`
- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/dg/dg-LLVM14-O2-g/high_precision_20260326_164052`
- verdict: `PARTIAL PASS`
- completed: `0`
- completed_with_warnings: `8`
- failed: `2`
- timed_out: `7`

## Method
- Followed `CompilerOptimization/Result/tengine/dg/executor.md`.
- No `-q` was used for the main report matrix except the documented diagnostic-only ICFG NTSCD check.
- All textual scans used `--c-lines`.
- All graph dumps used `--dot`; PTA graph dumps also used `--ir`.
- Every executed command is recorded in `commands.log`.

## Known Constraints Applied
- `fs` and `inv` used `--pta-field-sensitive 64` following the tengine executor guidance.
- `dod-ranganath` used a longer timeout (`1800s`).
- `standard --cda-icfg` is treated as unsupported in DG.
- `ntscd --cda-icfg --use-pta` is treated as analysis-only: `-q` and `--ir` are diagnostic checks; textual/`--c-lines`/`--dot` are expected to fail explicitly.

## Output Files
- `commands.log`: every raw docker command.
- `summary/steps.csv`: per-analysis status, timing, logs, and dot files.
- `summary/failures.csv`: only failed or timed-out analyses.
- `summary/line_hits.csv`: line/column hits resolved to source-file candidates from LLVM debug info.
- `summary/warnings.csv`: precision and compatibility warnings from stderr.

## Truthful Result Summary
- Successful with warnings:
  - `PTA fi`
  - `PTA fs --pta-field-sensitive 64`
  - `PTA inv --pta-field-sensitive 64`
  - `DDA ssa + PTA fi`
  - `DDA ssa + PTA fs --pta-field-sensitive 64`
  - `DDA ssa + PTA inv --pta-field-sensitive 64`
  - `CDA ntscd --cda-icfg --use-pta --pta-field-sensitive 64 -q`
  - `CDA ntscd --cda-icfg --use-pta --pta-field-sensitive 64 --ir`
- Timed out:
  - `CDA standard`
  - `CDA ntscd`
  - `CDA ntscd2`
  - `CDA dod`
  - `CDA dod+ntscd`
  - `CDA ntscd-ranganath`
  - `CDA dod-ranganath` even with `1800s`
- Failed honestly due unsupported mode handling:
  - `CDA standard --cda-icfg --use-pta --pta-field-sensitive 64`
  - `CDA ntscd --cda-icfg --use-pta --pta-field-sensitive 64` textual / `--c-lines` / `--dot`

## Warning Profile
- The dominant warning family is C++-heavy unsupported IR in PTA/DDA:
  - `invoke`
  - `landingpad`
  - `resume`
- These appear as `[pta] UNHANDLED` warnings and are preserved in `summary/warnings.csv`.
- This means the successful PTA/DDA runs are usable, but conservative and not fully precise for exception-heavy paths.

## Source-Line Mapping
- `summary/line_hits.csv` contains resolved source-line candidates from `--c-lines` output.
- Real mapped flatbuffers source files include, for example:
  - `CompilerOptimization/Target/flatbuffers/include/flatbuffers/string.h`
  - `CompilerOptimization/Target/flatbuffers/include/flatbuffers/table.h`
  - `CompilerOptimization/Target/flatbuffers/src/reflection.cpp`
  - `CompilerOptimization/Target/flatbuffers/src/idl_gen_text.cpp`
  - `CompilerOptimization/Target/flatbuffers/src/idl_gen_binary.cpp`
  - `CompilerOptimization/Target/flatbuffers/src/flatc_main.cpp`

## Bottom Line
- DG is partially usable on this whole-program LLVM14 `-O2 -g` flatbuffers bitcode.
- The PTA and DDA matrix completes when `fs` / `inv` use `--pta-field-sensitive 64`.
- The non-ICFG CDA family is currently the weak point for this program-level sample: every tested mode timed out under the current budgets, including `dod-ranganath` at `1800s`.
- ICFG CDA follows the same truthful rule as in the tengine executor:
  - `standard --cda-icfg` is unsupported in DG
  - `ntscd --cda-icfg --use-pta` is usable only in `-q` / `--ir`; textual / `--c-lines` / `--dot` are explicitly unsupported
