# phasar_O0_DebInfo - PhASAR redis full record

## Build & bitcode
- Source (original): `/work/PaperExperiment/CompilerOptimization/Target/redis`
- Source (writable copy): `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/work/redis`
- Build dir: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/build`
- Bitcode: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/artifacts`
- Verify log: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs/verify.log`

## Analysis summary
- Total analyses: 17
- ok: 7
- timeout: 2
- oom_or_killed: 6
- error: 2
- CSV: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs/summary.csv`

## Runs
- Per-analysis outputs: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/runs`
- Emit-IR run: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/runs/ifds-uninit_emit_ir`

## Logs
- Configure/build: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs/distclean.log`, `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs/build.log`
- Dry-run/bitcode: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs/make_dryrun.log`, `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs/generate_bc.log`, `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs/llvm_link.log`, `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs/verify.log`
- Analysis logs: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O0_DebInfo/logs`

## Analysis table

| analysis | exit_code | status | elapsed_sec |
| --- | ---: | --- | ---: |
| ifds-uninit | 137 | oom_or_killed | 396 |
| ifds-taint | 0 | ok | 178 |
| sparse-ifds-taint | 0 | ok | 180 |
| ide-xtaint | 0 | ok | 93 |
| ifds-type | 0 | ok | 95 |
| ide-lca | 137 | oom_or_killed | 344 |
| ifds-solvertest | 0 | ok | 97 |
| ide-solvertest | 0 | ok | 91 |
| inter-mono-solvertest | 0 | ok | 161 |
| inter-mono-taint | 124 | timeout | 420 |
| ide-stdio-ts | 137 | oom_or_killed | 44 |
| ide-iia | 137 | oom_or_killed | 78 |
| ide-fiia | 137 | oom_or_killed | 69 |
| ide-openssl-ts | 137 | oom_or_killed | 39 |
| ifds-const | 124 | timeout | 420 |
| intra-mono-fca | 139 | error | 25 |
| intra-mono-solvertest | 139 | error | 25 |
