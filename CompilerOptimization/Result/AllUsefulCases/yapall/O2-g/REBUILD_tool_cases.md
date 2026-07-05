# Rebuild yapall O2-g tool_cases.csv

## What This File Is

`tool_cases.csv` is a standardized case table generated from existing yapall
ValueCases outputs. The collector does not rerun yapall.

Current large output:

- `CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/tool_cases.csv`

## Inputs

Run selection:

- `CompilerOptimization/Result/AllUsefulCases/yapall/result.txt`

Selected raw run directories:

- `CompilerOptimization/Result/zopfli/yapall/LLVM14-O2-g/run_20260427_yapall_docker_smoke`
- `CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked`
- `CompilerOptimization/Result/masscan/yapall/LLVM14-O2-g/run_20260506_yapall_docker_masscan_linked_rescan`
- `CompilerOptimization/Result/tengine/yapall/LLVM14-O2-g/run_20260427_yapall_docker_tengine_linked`
- `CompilerOptimization/Result/lepton/yapall/LLVM14-O2-g/run_20260427_yapall_docker_lepton_linked`
- `CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0`

Main raw input files:

- `ValueCases/*_yapall_value_cases.csv`
- `ValueCases/raw_issues.csv`
- `ValueCases/ll_provenance.csv`
- `status/run_status.tsv`
- `commands/commands.log`
- `report/final_report.md`

The exact selected `ValueCases` CSVs are recorded in:

- `collection_manifest.json`

## Rebuild Command

From anywhere:

```bash
bash /home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/scripts/rebuild_tool_cases.sh
```

Equivalent manual command:

```bash
cd /home/jimi/PaperExperiment
python3 CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/scripts/collect_yapall_o2g_cases.py
```

Then refresh the P0 audit:

```bash
cd /home/jimi/PaperExperiment
python3 CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/scripts/audit_yapall_p0.py
```

## Outputs Overwritten

The collector rewrites these files in `CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/`:

- `tool_cases.csv`
- `tool_runs.csv`
- `weak_evidence_summary.csv`
- `collection_manifest.json`
- `case_collection_report.md`
- `native_output_profile.md`

The P0 audit rewrites:

- `p0_unique_locations.csv`
- `p0_final_audit.md`

## Notes

- Universe: `LLVM14-O2-g` / paper `O2-g`.
- The collector reads existing run artifacts only; it does not invoke Docker or
  rerun yapall.
- New raw yapall runs must first be converted into `ValueCases` with
  `CompilerOptimization/Tools/yapall/AnalysisResult/build_yapall_valuecases.py`.
- `Useless-CodeConsistent` rows with no other candidate class are excluded from
  `tool_cases.csv`.
- The output is large. On the current workspace it is several GB and cannot be
  pushed to normal GitHub Git without a large-file strategy.
