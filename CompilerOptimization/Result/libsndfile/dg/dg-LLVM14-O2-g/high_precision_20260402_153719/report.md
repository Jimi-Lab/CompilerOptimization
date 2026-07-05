# DG High Precision Scan: libsndfile_sndfile_convert_O2_g.bc

- image: `dg-llvm14:latest`
- bitcode: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719`
- verdict: `PARTIAL PASS`
- completed: `7`
- completed_with_warnings: `5`
- failed: `4`
- timeout: `0`
- unsupported: `2`

## Requirements Satisfaction
- No `-q` was used in main report steps.
- All textual report commands used `--c-lines`.
- All graph report commands used `--dot`; PTA graph commands additionally used `--ir`.
- Every command was logged in `commands.log`.
- Diagnostic-only commands are explicitly marked in `summary/steps.csv`.

## ICFG CDA Truthful Handling
- `standard --cda-icfg` is treated as unsupported.
- `ntscd --cda-icfg --use-pta` was tested with diagnostic `-q` and `--ir`.
- `ntscd` textual/`--c-lines`/`--dot` ICFG modes are recorded as unsupported when rejected by DG.

## Completed
- `PTA`: `fi`, `fs`, `inv` completed with warnings in both text (`--c-lines`) and dot outputs.
- `CDA` non-ICFG: `standard`, `ntscd`, `ntscd2`, `dod`, `dod+ntscd`, `ntscd-ranganath`, `dod-ranganath` completed in both text and dot outputs.
- `CDA ICFG` diagnostics: `ntscd --cda-icfg --use-pta` completed in `-q` and `--ir` modes.

## Failed
- `DDA ssa + PTA fi`: text and dot failed with `exit 137`; key stderr includes `[RWG] error: could not determine the called function in a call via pointer:`.
- `DDA ssa + PTA fs`: text and dot failed with `exit 137`; same key RWG error.
- `DDA ssa + PTA inv`: text failed with `exit 137` and dot timed out at `1200s`; key RWG error.
- `CDA standard --cda-icfg --use-pta`: explicit DG rejection with `ERROR: standard CDA does not support --cda-icfg in DG` (exit 2).

## Unsupported
- `CDA ntscd --cda-icfg --use-pta` textual mode (`--c-lines`) is unsupported and rejected explicitly.
- `CDA ntscd --cda-icfg --use-pta` dot mode (`--c-lines --dot`) is unsupported and rejected explicitly.
- Rejection message: `ERROR: llvm-cda-dump textual/--dot dumping for ICFG CDA is currently unsupported; use --ir or -q`.

## Key Warnings
- `[pta] UNHANDLED` warnings are present in PTA and DDA logs.
- `ShuffleVector instruction is not supported, loosing precision` appears repeatedly.
- `WARNING: Non-0 memset` appears repeatedly.

## Result Files
- `commands.log`: full executed command history.
- `summary/steps.csv`: per-step status, timing, commands, and log/dot paths.
- `summary/failures.csv`: failed and unsupported rows.
- `summary/line_hits.csv`: extracted `line:column` mappings resolved to source-file candidates.
- `summary/warnings.csv`: collected warning lines.
