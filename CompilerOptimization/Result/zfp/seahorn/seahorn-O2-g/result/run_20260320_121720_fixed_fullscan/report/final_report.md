# zfp SeaHorn Static Analysis Report (fixed image fullscan)

## Environment
- Docker image: `seahorn/seahorn-llvm14:fixed`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/artifacts/zfp_O2_g.bc`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260320_121720_fixed_fullscan`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) |
|---|---|---:|---:|
| 01 | inspect_profiler | 0 | 1 |
| 02 | inspect_mem_stats | 0 | 1 |
| 03 | inspect_callgraph_stats | 0 | 2 |
| 04 | smc_typeoff | 0 | 1 |
| 05 | smc_typeon | 0 | 1 |
| 06 | smc_instrument | 0 | 1 |
| 07 | horn_smc_reg | 247 | 51 |
| 08 | horn_smc_ptr | 247 | 50 |
| 09 | horn_smc_mem | 247 | 49 |
| 10 | ndc_instrument | 247 | 44 |
| 11 | horn_ndc_reg | 0 | 1 |
| 12 | horn_ndc_ptr | 0 | 0 |
| 13 | horn_ndc_mem | 0 | 0 |
| 14 | crab_instrument | 247 | 46 |
| 15 | horn_crab_ptr | 0 | 1 |
| 16 | term | 247 | 58 |

## Produced/Not Produced Outputs (No Hiding)
- `smc_bc`: produced
- `ndc_bc`: produced
- `crab_bc`: produced
- Full failure list: `summary/failure_inventory.csv`

## SMC Top File Distribution
| File | Case Count |
|---|---:|
| `Target/zfp/src/template/codecf.c` | 120 |
| `Target/zfp/src/template/encode.c` | 108 |
| `Target/zfp/src/template/encodef.c` | 44 |
| `Target/zfp/src/template/decode.c` | 22 |
| `Target/zfp/src/template/revencodef.c` | 8 |
| `Target/zfp/src/template/revencode.c` | 8 |
| `Target/zfp/include/zfp/bitstream.inl` | 2 |

## SMC Top File:Line Distribution
| File:Line | Case Count |
|---|---:|
| `Target/zfp/src/template/codecf.c:29` | 72 |
| `Target/zfp/src/template/codecf.c:30` | 48 |
| `Target/zfp/src/template/encode.c:154` | 32 |
| `Target/zfp/src/template/encode.c:225` | 32 |
| `Target/zfp/src/template/encodef.c:56` | 24 |
| `Target/zfp/src/template/encodef.c:57` | 20 |
| `Target/zfp/src/template/decode.c:37` | 20 |
| `Target/zfp/src/template/encode.c:106` | 16 |
| `Target/zfp/src/template/encode.c:193` | 16 |
| `Target/zfp/src/template/revencodef.c:37` | 8 |
| `Target/zfp/src/template/encode.c:50` | 6 |
| `Target/zfp/src/template/encode.c:78` | 6 |
| `Target/zfp/src/template/revencode.c:25` | 6 |
| `Target/zfp/include/zfp/bitstream.inl:0` | 2 |
| `Target/zfp/src/template/decode.c:74` | 2 |

## Horn Result Comparison
| Mode | Track | Step | DSA | Result | Exit | Elapsed(s) |
|---|---|---|---|---|---:|---:|
| horn_smc_reg | reg | large |  | error | 247 | 51 |
| horn_smc_ptr | ptr | large | sea-cs | error | 247 | 50 |
| horn_smc_mem | mem | small | sea-cs | error | 247 | 49 |
| horn_ndc_reg | reg | large |  | unsat | 0 | 1 |
| horn_ndc_ptr | ptr | large | sea-cs | unsat | 0 | 0 |
| horn_ndc_mem | mem | small | sea-cs | unsat | 0 | 0 |
| horn_crab_ptr | ptr | large | sea-cs | unsat | 0 | 1 |

## Notes
- This report does not hide failures. Any non-produced artifact is explicitly listed above and in failure_inventory.csv.
- `term` can still end with UNKNOWN/parser warning; see logs for exact details.
