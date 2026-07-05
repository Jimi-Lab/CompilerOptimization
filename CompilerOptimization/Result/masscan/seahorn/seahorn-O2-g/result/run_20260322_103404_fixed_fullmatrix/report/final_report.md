# masscan SeaHorn Full Matrix Report (fixed image)

## Environment
- Docker image: `seahorn/seahorn-llvm14:fixed`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/seahorn/seahorn-O2-g/result/run_20260322_103404_fixed_fullmatrix`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) |
|---|---|---:|---:|
| 01 | inspect_profiler | 0 | 1 |
| 02 | inspect_mem_stats | 0 | 1 |
| 03 | inspect_callgraph_stats | 0 | 1 |
| 04 | smc_typeoff | 0 | 7 |
| 05 | smc_typeon | 0 | 7 |
| 06 | smc_instrument | 245 | 4 |
| 07 | horn_smc_reg | 3 | 0 |
| 08 | horn_smc_ptr | 3 | 0 |
| 09 | horn_smc_mem | 3 | 0 |
| 10 | ndc_instrument | 247 | 144 |
| 11 | horn_ndc_reg | 0 | 1 |
| 12 | horn_ndc_ptr | 0 | 0 |
| 13 | horn_ndc_mem | 0 | 0 |
| 14 | crab_instrument | 247 | 60 |
| 15 | horn_crab_ptr | 0 | 1 |
| 16 | term | 247 | 154 |

## Produced/Not Produced Outputs (No Hiding)
- `smc_bc`: NOT produced
- `ndc_bc`: produced
- `crab_bc`: produced
- Full failure list: `summary/failure_inventory.csv`

## SMC Top File Distribution
| File | Case Count |
|---|---:|
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/out-grepable.c` | 32 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/massip-rangesv4.c` | 16 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/proto-preprocess.c` | 16 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/main.c` | 12 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/proto-smb.c` | 12 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/main-ptrace.c` | 4 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/output.c` | 4 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/rawsock.c` | 4 |

## SMC Top File:Line Distribution
| File:Line | Case Count |
|---|---:|
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/out-grepable.c:21` | 32 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/massip-rangesv4.c:804` | 16 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/main.c:1196` | 12 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/proto-smb.c:833` | 12 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/main-ptrace.c:89` | 4 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/output.c:116` | 4 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/proto-preprocess.c:114` | 4 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/proto-preprocess.c:371` | 4 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/proto-preprocess.c:375` | 4 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/proto-preprocess.c:381` | 4 |
| `CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/work/masscan-src/src/rawsock.c:896` | 4 |

## Horn Result Comparison
| Mode | Track | Step | DSA | Result | Exit | Elapsed(s) |
|---|---|---|---|---|---:|---:|
| horn_smc_reg | reg | large |  | error | 3 | 0 |
| horn_smc_ptr | ptr | large | sea-cs | error | 3 | 0 |
| horn_smc_mem | mem | small | sea-cs | error | 3 | 0 |
| horn_ndc_reg | reg | large |  | unsat | 0 | 1 |
| horn_ndc_ptr | ptr | large | sea-cs | unsat | 0 | 0 |
| horn_ndc_mem | mem | small | sea-cs | unsat | 0 | 0 |
| horn_crab_ptr | ptr | large | sea-cs | unsat | 0 | 1 |

## Notes
- This report does not hide failures. Any non-produced artifact is explicitly listed above and in failure_inventory.csv.
