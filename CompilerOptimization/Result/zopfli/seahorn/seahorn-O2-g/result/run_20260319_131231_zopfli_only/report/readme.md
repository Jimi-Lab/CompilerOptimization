# Zopfli SeaHorn Scan Readme

## Scope
- Target BC: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc`
- Output root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only`
- Docker image: `seahorn/seahorn-llvm14:nightly`
- Policy: static-analysis modes only (no `--bmc`, no `cex`, no `exe-cex`)

## Directory Layout
- `log/`: per-step stdout/stderr, command timeline, exit codes
- `artifact/`: instrumented intermediate BC files (`smc`, `ndc`, `crab`), term patch file
- `summary/`: `smc_cases.csv`, `horn_status.csv`, `overview.csv`
- `report/`: `final_report.md`

## Full Executed Command Sequence
Below are the exact commands executed (from `log/commands.log`), in order.

1. `timeout 1800 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea inspect-bitcode --profiler /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc'`
2. `timeout 1800 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea inspect-bitcode --mem-stats /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc'`
3. `timeout 1800 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea inspect-bitcode --mem-callgraph-stats /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc'`
4. `timeout 3600 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea smc-checks --print-smc-stats --smc-check-threshold=100000 /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc'`
5. `timeout 3600 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea smc-checks --print-smc-stats --smc-check-threshold=100000 --sea-dsa-type-aware /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc'`
6. `timeout 5400 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea smc-checks --smc-check-threshold=100000 /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc -o /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.smc.bc'`
7. `timeout 2400 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea horn /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.smc.bc --solve --step=large --track=reg --cpu 1800 --mem 24000'`
8. `timeout 4200 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea horn /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.smc.bc --solve --step=large --track=ptr --dsa sea-cs --cpu 3600 --mem 32000'`
9. `timeout 7800 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea horn /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.smc.bc --solve --step=small --track=mem --dsa sea-cs --cpu 7200 --mem 48000'`
10. `timeout 3600 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea ndc-inst /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc -o /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.ndc.bc'`
11. `timeout 2400 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea horn /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.ndc.bc --solve --step=large --track=reg --cpu 1800 --mem 24000'`
12. `timeout 4200 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea horn /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.ndc.bc --solve --step=large --track=ptr --dsa sea-cs --cpu 3600 --mem 32000'`
13. `timeout 7800 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea horn /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.ndc.bc --solve --step=small --track=mem --dsa sea-cs --cpu 7200 --mem 48000'`
14. `timeout 3600 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc '(sea crab-inst /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc -o /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.crab.bc || cp /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.crab.bc)'`
15. `timeout 4200 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea horn /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/zopfli_O2_g.crab.bc --solve --step=large --track=ptr --dsa sea-cs --cpu 3600 --mem 32000'`
16. `timeout 4200 docker run --rm --user '1000:1000' -v '/home/jimi/PaperExperiment:/work/PaperExperiment' -v '/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only/artifact/termination_patched.py:/home/usea/seahorn/lib/seapy/term/termination.py:ro' --workdir '/work/PaperExperiment' seahorn/seahorn-llvm14:nightly /bin/bash -lc 'sea term /work/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc --cpu 3600 --mem 24000'`

## Runtime and Exit Codes
From `log/exit_codes.csv`:

| step | exit_code | elapsed_sec |
|---|---:|---:|
| 01 | 0 | 0 |
| 02 | 0 | 0 |
| 03 | 0 | 0 |
| 04 | 0 | 0 |
| 05 | 0 | 0 |
| 06 | 0 | 0 |
| 07 | 0 | 26 |
| 08 | 0 | 1090 |
| 09 | 114 | 2 |
| 10 | 0 | 0 |
| 11 | 0 | 31 |
| 12 | 0 | 72 |
| 13 | 114 | 5 |
| 14 | 0 | 0 |
| 15 | 0 | 1 |
| 16 | 0 | 2 |

Notes:
- Step 09 and Step 13 failed with `exit_code=114` (see corresponding `*.stderr.log`).
- Remaining steps completed with `exit_code=0`.

## Parsing and Report Generation Process
After command execution, results were parsed and written as:
- `summary/smc_cases.csv`: extracted from both SMC stdout/stderr using pattern:
  - `Possible read of undefined value at`
  - followed by `--- File`, `--- Line`, `--- Column`, `--- Bitcode`
- `summary/horn_status.csv`: per Horn step status inferred by log text (`sat|unsat|unknown`) and exit code (`timeout|error`).
- `summary/overview.csv`: aggregated counts.
- `report/final_report.md`: matrix status + top file/line distribution + Horn comparison.

## Key Aggregated Outputs
From `summary/overview.csv`:
- `smc_case_total=24`
- `smc_typeoff_cases=12`
- `smc_typeon_cases=12`
- `unique_files=3`
- `unique_lines=3`
- `horn_sat_count=4`
- `horn_unsat_count=1`
- `horn_unknown_or_timeout_count=0`

## Important Workarounds Applied
1. `crab-inst` compatibility fallback:
   - If `sea crab-inst ...` fails, pipeline copies original BC to `artifact/zopfli_O2_g.crab.bc` to keep the matrix executable.
2. `term` command compatibility patch:
   - Mounted `artifact/termination_patched.py` over `/home/usea/seahorn/lib/seapy/term/termination.py` to avoid known image/z3 incompatibility while preserving execution trace.

## Where to Inspect Details
- Command timeline: `log/commands.log`
- Per-step exit/runtime: `log/exit_codes.csv`
- Detailed stderr for failures:
  - `log/sea.horn.smc.mem.stderr.log`
  - `log/sea.horn.ndc.mem.stderr.log`
- Final report: `report/final_report.md`
