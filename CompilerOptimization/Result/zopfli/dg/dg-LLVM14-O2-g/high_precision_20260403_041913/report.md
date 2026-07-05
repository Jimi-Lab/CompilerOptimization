# DG High Precision Scan: zopfli_O2_g_zopfli_only.bc

- image: `dg-llvm14:latest`
- bitcode: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc`
- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/dg/dg-LLVM14-O2-g/high_precision_20260403_041913`
- verdict: `PARTIAL PASS`
- completed: `7`
- completed_with_warnings: `8`
- failed: `2`
- timed_out: `0`
- unsupported_or_explicit_errors: `2`

## Method
- No `-q` was used in the main report matrix; only the documented ICFG NTSCD diagnostic check uses `-q`.
- All textual scans used `--c-lines`.
- All graph dumps used `--dot`; PTA graph dumps also used `--ir`.
- Every executed command is preserved in `commands.log`.
- Non-ICFG CDA modes follow staged retry timeouts: `300s`, then `1800s`, then `3600s`; `dod-ranganath` uses `7200s`.

## Truthfulness Rules Applied
- `standard --cda-icfg` is recorded as unsupported if DG reports it unsupported.
- `ntscd --cda-icfg --use-pta` is only full-supported for diagnostic `-q` / `--ir`; textual / `--c-lines` / `--dot` are recorded exactly as DG returns them.
- Failures, timeouts, crashes, and unsupported modes are not hidden.

## Output Files
- `commands.log`
- `log/` raw stdout/stderr
- `dot/` graph files
- `summary/steps.csv`
- `summary/failures.csv`
- `summary/line_hits.csv`
- `summary/warnings.csv`
