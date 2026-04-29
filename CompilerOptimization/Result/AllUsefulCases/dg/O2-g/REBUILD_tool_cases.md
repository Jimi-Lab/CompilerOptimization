# Rebuild dg O2-g tool_cases.csv

## What This File Is

`tool_cases.csv` is a standardized case table generated from existing dg
high_precision run summaries. The collector does not rerun dg.

Current large output:

- `CompilerOptimization/Result/AllUsefulCases/dg/O2-g/tool_cases.csv`

## Inputs

Run selection:

- `CompilerOptimization/Result/AllUsefulCases/dg/result.txt`

Selected raw run directories:

- `CompilerOptimization/Result/flatbuffers/dg/dg-LLVM14-O2-g/high_precision_20260326_164052`
- `CompilerOptimization/Result/lepton/dg/dg-LLVM14-O2-g/high_precision_20260402_153121`
- `CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719`
- `CompilerOptimization/Result/masscan/dg/dg-LLVM14-O2-g/high_precision_20260326_165024`
- `CompilerOptimization/Result/redis/dg/dg-LLVM14-O2-g/high_precision_20260409_123302`
- `CompilerOptimization/Result/tengine/dg/dg-LLVM14-O2-g/high_precision_20260325_125828`
- `CompilerOptimization/Result/zfp/dg/dg-LLVM14-O2-g/high_precision_20260402_154412`
- `CompilerOptimization/Result/zopfli/dg/dg-LLVM14-O2-g/high_precision_20260403_041913`

Main raw input files in each selected run:

- `summary/line_hits.csv`
- `summary/warnings.csv`
- `summary/failures.csv`
- `summary/steps.csv`
- `commands.log`
- `report.md`
- `work/*.ll`

The exact selected runs and per-target counts are recorded in:

- `collection_manifest.json`
- `tool_runs.csv`

## Rebuild Command

From anywhere:

```bash
bash /home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/dg/O2-g/scripts/rebuild_tool_cases.sh
```

Equivalent manual command:

```bash
cd /home/jimi/PaperExperiment
python3 CompilerOptimization/Result/AllUsefulCases/dg/O2-g/scripts/collect_dg_o2g_cases.py
```

## Outputs Overwritten

The collector rewrites these files in `CompilerOptimization/Result/AllUsefulCases/dg/O2-g/`:

- `tool_cases.csv`
- `tool_runs.csv`
- `collection_manifest.json`
- `case_collection_report.md`
- `native_output_profile.md`

## Notes

- Universe: `LLVM14-O2-g` / paper `O2-g`.
- The collector expands dg `line_hits.csv` rows. If one native row maps to
  multiple source candidates, the collector emits one standardized case per
  candidate.
- The collector also preserves warnings and failures as weak evidence or
  degradation evidence.
- The output is large. On the current workspace it is several GB and cannot be
  pushed to normal GitHub Git without a large-file strategy.
