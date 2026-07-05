# Clam Scan Final Report

## Metadata
- target: flatbuffers
- universe: O2
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc
- docker_image: seahorn/clam-llvm14:nightly
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/clam/LLVM14-O2-g/run_20260425_235741
- status_counts: {'timeout': 1}

## Command Matrix
| checker | domain | status | return_code | log |
| --- | --- | --- | --- | --- |
| null | zones | timeout | 137 | /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/clam/LLVM14-O2-g/run_20260425_235741/log/null_zones.log |

## High-Volume Warning Hotspots
| file | line | checker | domain | warning_count | example_property |
| --- | --- | --- | --- | --- | --- |

## Notes
- JSON reliability: this image can emit empty JSON if Boost is too old.
- If a config times out, the runner explicitly kills the container before moving on.
- The earlier run_20260425_230006 attempt used an unsafe timeout wrapper and should be treated as aborted evidence only.
