# libsndfile SeaHorn Full Matrix Report (fixed image)

## Environment
- Docker image: `seahorn/seahorn-llvm14:fixed`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) |
|---|---|---:|---:|
| 01 | inspect_profiler | 0 | 2 |
| 02 | inspect_mem_stats | 0 | 2 |
| 03 | inspect_callgraph_stats | 0 | 6 |
| 04 | smc_typeoff | 0 | 2 |
| 05 | smc_typeon | 0 | 2 |
| 06 | smc_instrument | 0 | 2 |
| 07 | horn_smc_reg | 247 | 110 |
| 08 | horn_smc_ptr | 247 | 48 |
| 09 | horn_smc_mem | 247 | 81 |
| 10 | ndc_instrument | 247 | 157 |
| 11 | horn_ndc_reg | 0 | 1 |
| 12 | horn_ndc_ptr | 0 | 0 |
| 13 | horn_ndc_mem | 0 | 0 |
| 14 | crab_instrument | 247 | 49 |
| 15 | horn_crab_ptr | 0 | 1 |
| 16 | term | 247 | 152 |

## Produced/Not Produced Outputs (No Hiding)
- `smc_bc`: produced
- `ndc_bc`: produced
- `crab_bc`: produced
- Full failure list: `summary/failure_inventory.csv`

## SMC Top File Distribution
| File | Case Count |
|---|---:|
| `Target/libsndfile/src/common.h` | 438 |
| `Target/libsndfile/src/GSM610/short_term.c` | 58 |
| `Target/libsndfile/src/GSM610/lpc.c` | 36 |
| `Target/libsndfile/src/ALAC/alac_encoder.c` | 32 |
| `Target/libsndfile/src/ALAC/dp_enc.c` | 28 |
| `Target/libsndfile/src/pcm.c` | 20 |
| `Target/libsndfile/src/GSM610/rpe.c` | 18 |
| `Target/libsndfile/src/GSM610/long_term.c` | 12 |
| `Target/libsndfile/src/ALAC/dp_dec.c` | 12 |
| `Target/libsndfile/src/common.c` | 8 |
| `Target/libsndfile/src/xi.c` | 8 |
| `Target/libsndfile/src/GSM610/gsm610_priv.h` | 8 |
| `Target/libsndfile/src/command.c` | 4 |
| `Target/libsndfile/src/ulaw.c` | 4 |
| `Target/libsndfile/src/alaw.c` | 4 |

## SMC Top File:Line Distribution
| File:Line | Case Count |
|---|---:|
| `Target/libsndfile/src/common.h:976` | 222 |
| `Target/libsndfile/src/common.h:967` | 216 |
| `Target/libsndfile/src/GSM610/short_term.c:234` | 48 |
| `Target/libsndfile/src/ALAC/alac_encoder.c:810` | 16 |
| `Target/libsndfile/src/ALAC/alac_encoder.c:800` | 16 |
| `Target/libsndfile/src/GSM610/short_term.c:0` | 10 |
| `Target/libsndfile/src/common.c:1399` | 8 |
| `Target/libsndfile/src/GSM610/long_term.c:502` | 8 |
| `Target/libsndfile/src/GSM610/lpc.c:137` | 8 |
| `Target/libsndfile/src/GSM610/rpe.c:47` | 8 |
| `Target/libsndfile/src/ALAC/dp_dec.c:346` | 8 |
| `Target/libsndfile/src/ALAC/dp_enc.c:99` | 8 |
| `Target/libsndfile/src/ALAC/dp_enc.c:107` | 8 |
| `Target/libsndfile/src/ALAC/dp_enc.c:352` | 8 |
| `Target/libsndfile/src/pcm.c:431` | 6 |

## Horn Result Comparison
| Mode | Track | Step | DSA | Result | Exit | Elapsed(s) |
|---|---|---|---|---|---:|---:|
| horn_smc_reg | reg | large |  | error | 247 | 110 |
| horn_smc_ptr | ptr | large | sea-cs | error | 247 | 48 |
| horn_smc_mem | mem | small | sea-cs | error | 247 | 81 |
| horn_ndc_reg | reg | large |  | unsat | 0 | 1 |
| horn_ndc_ptr | ptr | large | sea-cs | unsat | 0 | 0 |
| horn_ndc_mem | mem | small | sea-cs | unsat | 0 | 0 |
| horn_crab_ptr | ptr | large | sea-cs | unsat | 0 | 1 |

## Notes
- This report does not hide failures. Any non-produced artifact is explicitly listed above and in failure_inventory.csv.
