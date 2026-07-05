# phasar_O2_noinline_RelWithDebInfo - PhASAR redis full record

## Build & bitcode
- Source (original): `/work/PaperExperiment/CompilerOptimization/Target/redis`
- Source (writable copy): `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/work/redis`
- Build dir: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/build`
- Bitcode: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/artifacts`
- Verify log: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs/verify.log`

## Analysis summary
- Total analyses: 17
- ok: 8
- timeout: 3
- oom_or_killed: 4
- error: 2
- CSV: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs/summary.csv`

## Runs
- Per-analysis outputs: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/runs`
- Emit-IR run: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/runs/ifds-uninit_emit_ir`

## Logs
- Configure/build: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs/distclean.log`, `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs/build.log`
- Dry-run/bitcode: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs/make_dryrun.log`, `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs/generate_bc.log`, `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs/llvm_link.log`, `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs/verify.log`
- Analysis logs: `/work/PaperExperiment/CompilerOptimization/Result/redis/phasar_O2_noinline_RelWithDebInfo/logs`

## Analysis table

| analysis | exit_code | status | elapsed_sec |
| --- | ---: | --- | ---: |
| ifds-uninit | 124 | timeout | 420 |
| ifds-taint | 0 | ok | 88 |
| sparse-ifds-taint | 0 | ok | 89 |
| ide-xtaint | 0 | ok | 52 |
| ifds-type | 0 | ok | 55 |
| ide-lca | 124 | timeout | 420 |
| ifds-solvertest | 0 | ok | 54 |
| ide-solvertest | 0 | ok | 48 |
| inter-mono-solvertest | 0 | ok | 127 |
| inter-mono-taint | 0 | ok | 139 |
| ide-stdio-ts | 137 | oom_or_killed | 31 |
| ide-iia | 137 | oom_or_killed | 79 |
| ide-fiia | 137 | oom_or_killed | 56 |
| ide-openssl-ts | 137 | oom_or_killed | 33 |
| ifds-const | 124 | timeout | 421 |
| intra-mono-fca | 139 | error | 18 |
| intra-mono-solvertest | 139 | error | 18 |
