# phasar_O0_DebInfo - PhASAR curl full record

## Build & bitcode
- Source: `/work/PaperExperiment/CompilerOptimization/Target/Curl/7.68.0/curl-curl-7_68_0`
- Build dir: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/build`
- Bitcode: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/artifacts`
- Verify log: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/logs/verify.log`

## Analysis summary
- Total analyses: 17
- ok: 7
- timeout: 5
- oom_or_killed: 3
- error: 2
- CSV: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/logs/summary.csv`

## Runs
- Per-analysis outputs: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/runs`
- Emit-IR run: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/runs/ifds-uninit_emit_ir`

## Logs
- Configure/build: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/logs/configure.log`, `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/logs/build.log`
- Bitcode generation: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/logs/generate_bc.log`, `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/logs/llvm_link.log`, `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/logs/verify.log`
- Analysis logs: `/work/PaperExperiment/CompilerOptimization/Result/curl/phasar/phasar_O0_DebInfo/logs`

## Analysis table

| analysis | exit_code | status | elapsed_sec |
| --- | ---: | --- | ---: |
| ifds-uninit | 124 | timeout | 421 |
| ifds-taint | 0 | ok | 28 |
| sparse-ifds-taint | 0 | ok | 28 |
| ide-xtaint | 0 | ok | 13 |
| ifds-type | 0 | ok | 13 |
| ide-lca | 124 | timeout | 421 |
| ifds-solvertest | 0 | ok | 13 |
| ide-solvertest | 0 | ok | 13 |
| inter-mono-solvertest | 0 | ok | 27 |
| inter-mono-taint | 124 | timeout | 420 |
| ide-stdio-ts | 137 | oom_or_killed | 24 |
| ide-iia | 124 | timeout | 421 |
| ide-fiia | 124 | timeout | 420 |
| ide-openssl-ts | 137 | oom_or_killed | 24 |
| ifds-const | 137 | oom_or_killed | 229 |
| intra-mono-fca | 139 | error | 7 |
| intra-mono-solvertest | 139 | error | 6 |
