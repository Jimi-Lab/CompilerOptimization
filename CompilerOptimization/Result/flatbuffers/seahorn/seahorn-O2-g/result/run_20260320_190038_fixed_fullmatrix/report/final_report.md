# Flatbuffers SeaHorn Full Matrix Report (fixed image)

## Environment
- Docker image: `seahorn/seahorn-llvm14:fixed`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/seahorn/seahorn-O2-g/result/run_20260320_190038_fixed_fullmatrix`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) |
|---|---|---:|---:|
| 01 | inspect_profiler | 0 | 13 |
| 02 | inspect_mem_stats | 0 | 15 |
| 03 | inspect_callgraph_stats | 0 | 74 |
| 04 | smc_typeoff | 247 | 195 |
| 05 | smc_typeon | 247 | 177 |
| 06 | smc_instrument | 247 | 177 |
| 07 | horn_smc_reg | 0 | 1 |
| 08 | horn_smc_ptr | 0 | 0 |
| 09 | horn_smc_mem | 0 | 0 |
| 10 | ndc_instrument | 247 | 53 |
| 11 | horn_ndc_reg | 0 | 1 |
| 12 | horn_ndc_ptr | 0 | 0 |
| 13 | horn_ndc_mem | 0 | 0 |
| 14 | crab_instrument | 247 | 55 |
| 15 | horn_crab_ptr | 0 | 1 |
| 16 | term | 250 | 27 |

## Produced/Not Produced Outputs (No Hiding)
- `smc_bc`: produced
- `ndc_bc`: produced
- `crab_bc`: produced
- Full failure list: `summary/failure_inventory.csv`

## SMC Top File Distribution
- No SMC cases extracted.

## SMC Top File:Line Distribution
- No line-level SMC cases extracted.

## Horn Result Comparison
| Mode | Track | Step | DSA | Result | Exit | Elapsed(s) |
|---|---|---|---|---|---:|---:|
| horn_smc_reg | reg | large |  | unsat | 0 | 1 |
| horn_smc_ptr | ptr | large | sea-cs | unsat | 0 | 0 |
| horn_smc_mem | mem | small | sea-cs | unsat | 0 | 0 |
| horn_ndc_reg | reg | large |  | unsat | 0 | 1 |
| horn_ndc_ptr | ptr | large | sea-cs | unsat | 0 | 0 |
| horn_ndc_mem | mem | small | sea-cs | unsat | 0 | 0 |
| horn_crab_ptr | ptr | large | sea-cs | unsat | 0 | 1 |

## Notes
- This report does not hide failures. Any non-produced artifact is explicitly listed above and in failure_inventory.csv.
