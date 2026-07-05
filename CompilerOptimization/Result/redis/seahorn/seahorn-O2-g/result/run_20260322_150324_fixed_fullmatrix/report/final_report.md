# Redis SeaHorn Full Matrix Report (fixed image)

## Environment
- Docker image: `seahorn/seahorn-llvm14:fixed`
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/artifacts/redis-server_O2_g.bc`
- Run root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/redis/seahorn/seahorn-O2-g/result/run_20260322_150324_fixed_fullmatrix`

## Execution Matrix Status
| Step | Name | Exit | Elapsed(s) |
|---|---|---:|---:|
| 01 | inspect_profiler | 0 | 3 |
| 02 | inspect_mem_stats | 245 | 3 |
| 03 | inspect_callgraph_stats | 245 | 2 |
| 04 | horn_orig_reg | 247 | 139 |
| 05 | horn_orig_ptr | 247 | 49 |
| 06 | horn_orig_mem | 247 | 46 |
| 07 | smc_typeoff | 245 | 4 |
| 08 | smc_typeon | 245 | 3 |
| 09 | smc_instrument | 245 | 3 |
| 10 | ndc_instrument | 247 | 49 |
| 11 | crab_instrument | 247 | 48 |
| 12 | horn_smc_reg | SKIP | 0 |
| 13 | horn_smc_ptr | SKIP | 0 |
| 14 | horn_smc_mem | SKIP | 0 |
| 15 | horn_ndc_reg | SKIP | 0 |
| 16 | horn_ndc_ptr | SKIP | 0 |
| 17 | horn_ndc_mem | SKIP | 0 |
| 18 | horn_crab_ptr | SKIP | 0 |
| 19 | term | 250 | 11 |

## Main Hard-Gate Checks
| Artifact | Exists | Main Present | Decision |
|---|---:|---:|---|
| `redis-server_O2_g.smc.bc` | 0 | 0 | invalid_input |
| `redis-server_O2_g.ndc.bc` | 1 | 0 | invalid_input |
| `redis-server_O2_g.crab.bc` | 1 | 0 | invalid_input |

## Produced/Not Produced Outputs (No Hiding)
- `smc_bc`: NOT produced
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
| horn_orig_reg | reg | large |  | error | 247 | 139 |
| horn_orig_ptr | ptr | large | sea-cs | error | 247 | 49 |
| horn_orig_mem | mem | small | sea-cs | error | 247 | 46 |
| horn_smc_reg |  |  |  | invalid_input | SKIP | 0 |
| horn_smc_ptr |  |  |  | invalid_input | SKIP | 0 |
| horn_smc_mem |  |  |  | invalid_input | SKIP | 0 |
| horn_ndc_reg |  |  |  | invalid_input | SKIP | 0 |
| horn_ndc_ptr |  |  |  | invalid_input | SKIP | 0 |
| horn_ndc_mem |  |  |  | invalid_input | SKIP | 0 |
| horn_crab_ptr |  |  |  | invalid_input | SKIP | 0 |

## Notes
- This report does not hide failures. Any non-produced artifact or invalid input is explicit in summary files.
- Hard-gate policy: transformed artifacts that lose `main` are marked `invalid_input` and excluded from valid Horn conclusions.
