# Clam Scan Final Report

## Metadata
- target: zopfli
- universe: O2
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc
- docker_image: seahorn/clam-llvm14:nightly
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/clam/LLVM14-O2-g/run_20260426_140526
- status_counts: {'tool failure': 1}

## Command Matrix
| checker | domain | status | return_code | log |
| --- | --- | --- | --- | --- |
| null | zones | tool failure | 137 | /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/clam/LLVM14-O2-g/run_20260426_140526/log/null_zones.log |

## High-Volume Warning Hotspots
| file | line | checker | domain | warning_count | example_property |
| --- | --- | --- | --- | --- | --- |

## Notes
- JSON reliability: this image can emit empty JSON if Boost is too old.
- If a config times out, the runner explicitly kills the container before moving on.
- The earlier run_20260425_230006 attempt used an unsafe timeout wrapper and should be treated as aborted evidence only.
