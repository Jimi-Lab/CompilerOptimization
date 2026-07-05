# phasar_O2_RelWithDebInfo - PhASAR curl full record

## Build & bitcode
- Source: `/work/PaperExperiment/CompilerOptimization/Target/Curl/7.68.0/curl-curl-7_68_0`
- Build dir: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/build`
- Bitcode: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/artifacts`
- Verify log: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/logs/verify.log`

## Analysis summary
- Total analyses: 17
- ok: 9
- timeout: 3
- oom_or_killed: 3
- error: 2
- CSV: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/logs/summary.csv`

## Runs
- Per-analysis outputs: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/runs`
- Emit-IR run: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/runs/ifds-uninit_emit_ir`

## Logs
- Configure/build: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/logs/configure.log`, `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/logs/build.log`
- Bitcode generation: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/logs/generate_bc.log`, `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/logs/llvm_link.log`, `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/logs/verify.log`
- Analysis logs: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O2_RelWithDebInfo/logs`

## Analysis table

| analysis | exit_code | status | elapsed_sec |
| --- | ---: | --- | ---: |
| ifds-uninit | 0 | ok | 28 |
| ifds-taint | 0 | ok | 13 |
| sparse-ifds-taint | 0 | ok | 13 |
| ide-xtaint | 0 | ok | 7 |
| ifds-type | 0 | ok | 7 |
| ide-lca | 137 | oom_or_killed | 395 |
| ifds-solvertest | 0 | ok | 8 |
| ide-solvertest | 0 | ok | 7 |
| inter-mono-solvertest | 0 | ok | 15 |
| inter-mono-taint | 0 | ok | 17 |
| ide-stdio-ts | 137 | oom_or_killed | 216 |
| ide-iia | 124 | timeout | 420 |
| ide-fiia | 124 | timeout | 421 |
| ide-openssl-ts | 137 | oom_or_killed | 207 |
| ifds-const | 124 | timeout | 421 |
| intra-mono-fca | 139 | error | 4 |
| intra-mono-solvertest | 139 | error | 4 |
