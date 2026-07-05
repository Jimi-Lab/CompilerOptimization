# Tengine SeaHorn Full Matrix Report (fixed image)

- Docker image: `seahorn/seahorn-llvm14:fixed`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/tengine.bc`
- main_present: `True`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/seahorn/seahorn-O2-g/result/run_20260322_185943_fixed_fullmatrix`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) |
|---|---|---:|---:|
| 01 | inspect_profiler | 0 | 1 |
| 02 | inspect_mem_stats | 0 | 1 |
| 03 | inspect_callgraph_stats | 0 | 1 |
| 04 | smc_typeoff | 0 | 1 |
| 05 | smc_typeon | 0 | 1 |
| 06 | smc_instrument | 245 | 1 |
| 07 | horn_smc_reg | 3 | 0 |
| 08 | horn_smc_ptr | 3 | 0 |
| 09 | horn_smc_mem | 3 | 0 |
| 10 | ndc_instrument | 0 | 1 |
| 11 | horn_ndc_reg | 0 | 47 |
| 12 | horn_ndc_ptr | 247 | 171 |
| 13 | horn_ndc_mem | 247 | 104 |
| 14 | crab_instrument | 0 | 3 |
| 15 | horn_crab_ptr | 0 | 3 |
| 16 | term | 0 | 6 |

## Produced/Not Produced Outputs (No Hiding)
- `smc_bc`: NOT produced
- `ndc_bc`: produced
- `crab_bc`: produced
- Full failure list: `summary/failure_inventory.csv`

## SMC Top File Distribution
| File | Case Count |
|---|---:|
| `Target/Tengine/examples/common/tengine_operations.c` | 132 |
| `Target/Tengine/examples/common/stb_image.h` | 84 |
| `Target/Tengine/examples/common/stb_image_write.h` | 50 |
| `Target/Tengine/examples/common/common.h` | 2 |
| `Target/Tengine/examples/tm_classification.c` | 2 |

## Horn Result Comparison
| Mode | Track | Step | DSA | Result | Exit | Elapsed(s) |
|---|---|---|---|---|---:|---:|
| horn_smc_reg | reg | large |  | error | 3 | 0 |
| horn_smc_ptr | ptr | large | sea-cs | error | 3 | 0 |
| horn_smc_mem | mem | small | sea-cs | error | 3 | 0 |
| horn_ndc_reg | reg | large |  | sat | 0 | 47 |
| horn_ndc_ptr | ptr | large | sea-cs | error | 247 | 171 |
| horn_ndc_mem | mem | small | sea-cs | error | 247 | 104 |
| horn_crab_ptr | ptr | large | sea-cs | unsat | 0 | 3 |
