# Zopfli SeaHorn Static Analysis Report (zopfli_only bc)

## Environment
- Docker image: `seahorn/seahorn-llvm14:nightly`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/seahorn/seahorn-O2-g/result/run_20260319_131231_zopfli_only`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) | Status |
|---|---|---:|---:|---|
| 01 | inspect_profiler | 0 | 0 | ok |
| 02 | inspect_mem_stats | 0 | 0 | ok |
| 03 | inspect_callgraph_stats | 0 | 0 | ok |
| 04 | smc_typeoff | 0 | 0 | ok |
| 05 | smc_typeon | 0 | 0 | ok |
| 06 | smc_instrument | 0 | 0 | ok |
| 07 | horn_smc_reg | 0 | 26 | ok |
| 08 | horn_smc_ptr | 0 | 1090 | ok |
| 09 | horn_smc_mem | 114 | 2 | error |
| 10 | ndc_instrument | 0 | 0 | ok |
| 11 | horn_ndc_reg | 0 | 31 | ok |
| 12 | horn_ndc_ptr | 0 | 72 | ok |
| 13 | horn_ndc_mem | 114 | 5 | error |
| 14 | crab_instrument | 0 | 0 | ok |
| 15 | horn_crab_ptr | 0 | 1 | ok |
| 16 | term | 0 | 2 | ok |

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
| horn_smc_reg | reg | large |  | sat | 0 | 26 |
| horn_smc_ptr | ptr | large | sea-cs | sat | 0 | 1090 |
| horn_smc_mem | mem | small | sea-cs | error | 114 | 2 |
| horn_ndc_reg | reg | large |  | sat | 0 | 31 |
| horn_ndc_ptr | ptr | large | sea-cs | sat | 0 | 72 |
| horn_ndc_mem | mem | small | sea-cs | error | 114 | 5 |
| horn_crab_ptr | ptr | large | sea-cs | unsat | 0 | 1 |

## Notes
- `crab-inst` incompatibility in this SeaHorn image is handled by fallback copy to keep matrix runnable.
- `term` uses patched termination module to bypass image z3 compatibility issue.
- Completed steps: 16/16
