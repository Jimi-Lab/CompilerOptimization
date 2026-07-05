# Flatbuffers Baseline + Slice + Hard-Gate Report

- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc`
- image: `seahorn/seahorn-llvm14:fixed`
- run_root: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/seahorn/seahorn-O2-g/result/run_20260320_194406_baseline_slice_hardgate`

## Deliverables
- step log: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/seahorn/seahorn-O2-g/result/run_20260320_194406_baseline_slice_hardgate/summary/steps.csv`
- gate checks: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/seahorn/seahorn-O2-g/result/run_20260320_194406_baseline_slice_hardgate/summary/gate_checks.csv`
- artifacts: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/seahorn/seahorn-O2-g/result/run_20260320_194406_baseline_slice_hardgate/artifact`

## Notes
- hard gate policy: if transformed artifact loses `main`, mark `invalid_input` and skip horn result collection for that artifact.
