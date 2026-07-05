# Zopfli SeaHorn Static Analysis Report (fixed image rerun)

## Environment
- Docker image: `seahorn/seahorn-llvm14:fixed`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260320_102609_fixed`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) |
|---|---|---:|---:|
| 01 | inspect_profiler | 0 | 0 |
| 02 | inspect_mem_stats | 0 | 0 |
| 03 | inspect_callgraph_stats | 0 | 0 |
| 04 | smc_typeoff | 0 | 0 |
| 05 | smc_typeon | 0 | 0 |
| 06 | smc_instrument | 0 | 0 |
| 07 | horn_smc_reg | 0 | 24 |
| 08 | horn_smc_ptr | 0 | 1097 |
| 09 | horn_smc_mem | 114 | 2 |
| 10 | ndc_instrument | 0 | 0 |
| 11 | horn_ndc_reg | 0 | 38 |
| 12 | horn_ndc_ptr | 0 | 61 |
| 13 | horn_ndc_mem | 114 | 5 |
| 14 | crab_instrument | 0 | 1 |
| 15 | horn_crab_ptr | 0 | 1 |
| 16 | term | 0 | 2 |

## Produced/Not Produced Outputs (No Hiding)
- `smc_bc`: produced
- `ndc_bc`: produced
- `crab_bc`: produced
- Full failure list: `summary/failure_inventory.csv`

## SMC Top File Distribution
| File | Case Count |
|---|---:|
| `CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/work/zopfli_rebuild/src/zopfli/cache.c` | 8 |
| `CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/work/zopfli_rebuild/src/zopfli/deflate.c` | 8 |
| `CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/work/zopfli_rebuild/src/zopfli/lz77.c` | 8 |

## SMC Top File:Line Distribution
| File:Line | Case Count |
|---|---:|
| `CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/work/zopfli_rebuild/src/zopfli/cache.c:102` | 8 |
| `CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/work/zopfli_rebuild/src/zopfli/deflate.c:492` | 8 |
| `CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/work/zopfli_rebuild/src/zopfli/lz77.c:498` | 8 |

## Horn Result Comparison
| Mode | Track | Step | DSA | Result | Exit | Elapsed(s) |
|---|---|---|---|---|---:|---:|
| horn_smc_reg | reg | large |  | sat | 0 | 24 |
| horn_smc_ptr | ptr | large | sea-cs | sat | 0 | 1097 |
| horn_smc_mem | mem | small | sea-cs | error | 114 | 2 |
| horn_ndc_reg | reg | large |  | sat | 0 | 38 |
| horn_ndc_ptr | ptr | large | sea-cs | sat | 0 | 61 |
| horn_ndc_mem | mem | small | sea-cs | error | 114 | 5 |
| horn_crab_ptr | ptr | large | sea-cs | unsat | 0 | 1 |

## Notes
- This report does not hide failures. Any non-produced artifact is explicitly listed above and in failure_inventory.csv.
- `term` can still end with UNKNOWN/parser warning even after compatibility fixes; see logs for exact details.
