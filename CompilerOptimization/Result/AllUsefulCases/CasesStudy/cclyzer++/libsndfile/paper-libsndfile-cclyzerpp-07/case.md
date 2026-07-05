# paper-libsndfile-cclyzerpp-07

## Identity

- repo: `libsndfile`
- tool: `cclyzer++`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `ColumnOutOfRange`
- case_kind: `LocationInvalid`
- case_uid: `cclyzerpp.libsndfile.O2g.014160`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/ir/libsndfile_sndfile_convert_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/all_cases.csv`
- raw_row_or_line: `phi_instr:4493:fabfbb94c97292e99b8ecac0ae696cb2cc96fe67`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/snippets/cclyzerpp_libsndfile_O2g_015560.source.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/snippets/cclyzerpp_libsndfile_O2g_015560.ir.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/snippets/cclyzerpp_libsndfile_O2g_015560.row.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/all_cases.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/relations;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/commands/command.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/status/run_status.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/log/cclyzerpp.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/report/final_report.md;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/analysis_manifest.json;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/inventory/relation_row_counts.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/index/ir_instruction_index.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/map/native_fact_source_map.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/report/final_native_output_analysis.md`

## Reported Location

- reported_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.c`
- reported_line: `193`
- reported_column: `30`
- location_validity: `column_out_of_range`
- source_region: `project_source`

## IR Anchor

- mode: `phi_instr`
- ir_function: `<llvm-link>:sfe_apply_metadata_changes`
- ir_instruction: `<llvm-link>:sfe_apply_metadata_changes:271`
- ir_line: ``
- ir_snippet:

```llvm
store i32 %209, i32* %210, align 4, !dbg !87358, !tbaa !33187
```

## Source / Message

- source_snippet:

```text
   191: 						if (lead_char != '0' && left_align == SF_FALSE)\n   192: 							width_specifier -- ;\n>> 193: \n   194: 						u = - ((unsigned) d) ;\n   195: 						}
```

- message: `Wanted-PhiMergeLocationDrift; phi_instr; ColumnOutOfRange; phi_incoming_count=3`
- root_cause_hint: `Mem2Reg_or_Phi-node_merge_or_CFG_simplification`
- inventory_confidence: `medium`
- notes: `source_exists=1; original_priority=P0; mapping_status=ColumnOutOfRange; phenomenon=Wanted-PhiMergeLocationDrift`

## Manual Study Checklist

- [ ] Confirm all referenced artifacts exist.
- [ ] Validate why the reported location is invalid or drifted.
- [ ] Locate the IR instruction and debug metadata in the `.ll` file.
- [ ] Build 1-3 candidate recovered source locations.
- [ ] Run the LLM recovery prompt using `input.json`.
- [ ] Verify the LLM output manually.
- [ ] Write the paper-ready narrative below.

## Paper-Ready Narrative

### Summary

This case reveals a **tool false positive** caused by a basename-disambiguation bug in cclyzer++'s source-file resolution logic, not a genuine debug-info quality problem. The tool reported `src/common.c:193:30` as `ColumnOutOfRange` (line 193 is blank), but the debug metadata correctly points to `programs/common.c:193:30` where `binfo.coding_history_size = (uint32_t) slen ;` is a valid location. The debug metadata is fully correct; the invalidity is an artifact of the tool's file-resolution pipeline.

### Debug Metadata Chain (verified)

```
!3908 = !DIFile(filename: "Target/libsndfile/programs/common.c",
                directory: "/home/jimi/PaperExperiment/CompilerOptimization")
!87069 = !DISubprogram(name: "sfe_apply_metadata_changes", file: !3908, line: 234)
!87165 = !DISubprogram(name: "merge_broadcast_info", file: !3908, line: 105)
!87205 = !DILocation(line: 265, column: 31, scope: !87158)    ← call site
!87203 = !DILexicalBlock(scope: !87199, file: !3908, line: 189) ← else branch
!87358 = !DILocation(line: 193, column: 30, scope: !87203, inlinedAt: !87205)
```

The store instruction `store i32 %209, i32* %210, align 4, !dbg !87358` corresponds to the inlined statement `binfo.coding_history_size = (uint32_t) slen ;` at `programs/common.c:193`. The `inlinedAt` chain correctly traces to the call site `merge_broadcast_info(...)` at `programs/common.c:265`. All metadata is internally consistent and correct.

### Root Cause: `resolve_difile` Basename Ambiguity

The bug is in `analyze_native_value_cases.py:resolve_difile()` (line 1520). The function resolves DIFile references to filesystem paths using a candidate list with fixed priority:

1. Source-index basename matches under `target_root` (via `is_under`)
2. The DIFile's own `directory/filename` resolution (`raw` path)
3. Source-index basename matches (unfiltered, second pass)
4. Returns `dedup_paths(candidates)[0]` — always the **first** candidate

The project has two `common.c` files:
- `Target/libsndfile/src/common.c` (1849 lines) — library formatting/logging
- `Target/libsndfile/programs/common.c` (503 lines) — tool metadata handling

`build_source_index()` (line 835) walks `target_root` with `os.walk`, which visits `src/` before `programs/` alphabetically. Both files are indexed under the key `"common.c"`, with `src/common.c` appearing first.

When `resolve_difile("3908")` is called:
- `raw` = `/home/jimi/.../Target/libsndfile/programs/common.c` (correct, from DIFile directory+filename)
- But `source_index["common.c"][0]` = `src/common.c` (first alphabetically)
- `dedup_paths(...)[0]` returns `src/common.c` because it was added before `raw`

**Result**: All debug locations in `merge_broadcast_info` and `sfe_apply_metadata_changes` (both in `programs/common.c`) are mapped to `src/common.c`.

### ColumnOutOfRange Mechanism

With the wrong file resolved, the validation (line 1425) reads `src/common.c:193`:
- Actual content: empty line (blank separator between lines 192 and 194 in the `case 'd':` integer-formatting block)
- `len(source_line_text)` = 0, so `max_valid_column` = 1
- Reported column 30 > 1 → **ColumnOutOfRange**

If the correct file `programs/common.c:193` were used:
- Content: `binfo.coding_history_size = (uint32_t) slen ;` (length 56)
- Column 30 ≤ 57 → **MappedExact**

### Phi-Merge Context (Why This Case Was Flagged)

The store instruction appears in basic block `%204`, one of three predecessors (`%204`, `%199`, `%168`) feeding into block `%211` which contains phi node `%215 = phi i8* [...]`. The `phi_instr` analysis pipeline in cclyzer++ flags instructions in phi-merge contexts under the hypothesis that Mem2Reg/CFG-simplification may corrupt their debug locations. In this case, the debug location itself is intact — the corruption is in the tool's own file-resolution layer.

### Significance for the Paper

This case serves as a **boundary example** demonstrating that:
1. Not all `ColumnOutOfRange` / `LineOutOfRange` classifications indicate real debug-info degradation
2. Tool-internal file resolution can be the single point of failure, especially for projects with same-basename source files
3. The `Wanted-PhiMergeLocationDrift` phenomenon label can be misleading — the phi-merge pattern is coincidental to the actual failure (file disambiguation)
4. DIFile metadata in LLVM IR is generally reliable; tool pipelines should trust DIFile directory+filename resolution over basename-only source indexing when the DIFile-resolved path exists on disk
