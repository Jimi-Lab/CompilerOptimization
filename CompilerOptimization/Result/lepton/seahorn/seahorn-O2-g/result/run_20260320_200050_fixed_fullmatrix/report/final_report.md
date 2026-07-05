# Lepton SeaHorn Full Matrix Report (fixed image)

## Environment
- Docker image: `seahorn/seahorn-llvm14:fixed`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g/lepton_artifacts/lepton_O2_g.bc`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/seahorn/seahorn-O2-g/result/run_20260320_200050_fixed_fullmatrix`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) |
|---|---|---:|---:|
| 01 | inspect_profiler | 0 | 1 |
| 02 | inspect_mem_stats | 0 | 3 |
| 03 | inspect_callgraph_stats | 0 | 9 |
| 04 | smc_typeoff | 0 | 5 |
| 05 | smc_typeon | 0 | 5 |
| 06 | smc_instrument | 245 | 4 |
| 07 | horn_smc_reg | 3 | 0 |
| 08 | horn_smc_ptr | 3 | 0 |
| 09 | horn_smc_mem | 3 | 0 |
| 10 | ndc_instrument | 0 | 3 |
| 11 | horn_ndc_reg | 0 | 251 |
| 12 | horn_ndc_ptr | 247 | 189 |
| 13 | horn_ndc_mem | 247 | 134 |
| 14 | crab_instrument | 0 | 61 |
| 15 | horn_crab_ptr | 0 | 40 |
| 16 | term | 250 | 4 |

## Produced/Not Produced Outputs (No Hiding)
- `smc_bc`: NOT produced
- `ndc_bc`: produced
- `crab_bc`: produced
- Full failure list: `summary/failure_inventory.csv`

## SMC Top File Distribution
| File | Case Count |
|---|---:|
| `Target/lepton/src/vp8/model/model.hh` | 114 |
| `Target/lepton/src/vp8/util/block_context.hh` | 92 |
| `Target/lepton/src/lepton/idct.cc` | 32 |
| `Target/lepton/src/lepton/bitops.hh` | 16 |
| `Target/lepton/src/io/MemMgrAllocator.cc` | 12 |
| `Target/lepton/src/lepton/jpgcoder.cc` | 10 |
| `Target/lepton/src/lepton/uncompressed_components.hh` | 8 |
| `Target/lepton/src/vp8/util/billing.cc` | 4 |
| `Target/lepton/src/lepton/socket_serve.cc` | 2 |
| `Target/lepton/src/lepton/recoder.cc` | 2 |
| `Target/lepton/src/lepton/vp8_encoder.cc` | 2 |

## SMC Top File:Line Distribution
| File:Line | Case Count |
|---|---:|
| `Target/lepton/src/vp8/util/block_context.hh:57` | 24 |
| `Target/lepton/src/vp8/util/block_context.hh:70` | 24 |
| `Target/lepton/src/vp8/util/block_context.hh:71` | 24 |
| `Target/lepton/src/vp8/model/model.hh:1026` | 24 |
| `Target/lepton/src/vp8/model/model.hh:949` | 24 |
| `Target/lepton/src/vp8/model/model.hh:1011` | 24 |
| `Target/lepton/src/vp8/util/block_context.hh:75` | 20 |
| `Target/lepton/src/lepton/bitops.hh:326` | 16 |
| `Target/lepton/src/lepton/idct.cc:171` | 16 |
| `Target/lepton/src/lepton/idct.cc:179` | 16 |
| `Target/lepton/src/vp8/model/model.hh:1025` | 12 |
| `Target/lepton/src/vp8/model/model.hh:1010` | 12 |
| `Target/lepton/src/io/MemMgrAllocator.cc:439` | 10 |
| `Target/lepton/src/lepton/uncompressed_components.hh:72` | 8 |
| `Target/lepton/src/vp8/model/model.hh:705` | 6 |

## Horn Result Comparison
| Mode | Track | Step | DSA | Result | Exit | Elapsed(s) |
|---|---|---|---|---|---:|---:|
| horn_smc_reg | reg | large |  | error | 3 | 0 |
| horn_smc_ptr | ptr | large | sea-cs | error | 3 | 0 |
| horn_smc_mem | mem | small | sea-cs | error | 3 | 0 |
| horn_ndc_reg | reg | large |  | sat | 0 | 251 |
| horn_ndc_ptr | ptr | large | sea-cs | error | 247 | 189 |
| horn_ndc_mem | mem | small | sea-cs | error | 247 | 134 |
| horn_crab_ptr | ptr | large | sea-cs | unsat | 0 | 40 |

## Notes
- This report does not hide failures. Any non-produced artifact is explicitly listed above and in failure_inventory.csv.
