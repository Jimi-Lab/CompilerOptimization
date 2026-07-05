# paper-zfp-cclyzerpp-18

## Identity

- repo: `zfp`
- tool: `cclyzer++`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `ColumnOutOfRange`
- case_kind: `LocationInvalid`
- case_uid: `cclyzerpp.zfp.O2g.001127`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/ir/zfp_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/all_cases.csv`
- raw_row_or_line: `subset.var_points_to:530509:6ce6292c88d45a54b0e6256c791b0654552ae916`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/snippets/cclyzerpp_zfp_O2g_046805.source.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/snippets/cclyzerpp_zfp_O2g_046805.ir.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/snippets/cclyzerpp_zfp_O2g_046805.row.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/all_cases.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/relations;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/commands/command.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/status/run_status.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/log/cclyzerpp.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/report/final_report.md;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/analysis_manifest.json;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/inventory/relation_row_counts.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/index/ir_instruction_index.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/map/native_fact_source_map.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927/ValueCases/report/final_native_output_analysis.md`

## Reported Location

- reported_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/zfp.c`
- reported_line: `35`
- reported_column: `23`
- location_validity: `column_out_of_range`
- source_region: `project_source`

## IR Anchor

- mode: `subset.var_points_to`
- ir_function: `print_error`
- ir_instruction: `<llvm-link>:print_error:8`
- ir_line: `35`
- ir_snippet:

```llvm
%7 = bitcast i8* %0 to float*, !dbg !39037
```

## Source / Message

- source_snippet:

```text
    *min = imin;
```

- message: `Wanted-AliasCollapseWithBadLocation; subset.var_points_to; ColumnOutOfRange; points_to_count=11`
- root_cause_hint: `SROA_or_Mem2Reg_or_Phi-node_merge_or_GVN`
- inventory_confidence: `medium`
- notes: `source_exists=1; original_priority=P0; mapping_status=ColumnOutOfRange; phenomenon=Wanted-AliasCollapseWithBadLocation`

## Manual Study Checklist

- [ ] Confirm all referenced artifacts exist.
- [ ] Validate why the reported location is invalid or drifted.
- [ ] Locate the IR instruction and debug metadata in the `.ll` file.
- [ ] Build 1-3 candidate recovered source locations.
- [ ] Run the LLM recovery prompt using `input.json`.
- [ ] Verify the LLM output manually.
- [ ] Write the paper-ready narrative below.

## Paper-Ready Narrative

TODO.
