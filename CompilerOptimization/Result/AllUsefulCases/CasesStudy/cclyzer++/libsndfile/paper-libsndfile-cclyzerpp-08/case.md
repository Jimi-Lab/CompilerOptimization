# paper-libsndfile-cclyzerpp-08

## Identity

- repo: `libsndfile`
- tool: `cclyzer++`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `ColumnOutOfRange`
- case_kind: `LocationInvalid`
- case_uid: `cclyzerpp.libsndfile.O2g.014162`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/ir/libsndfile_sndfile_convert_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/all_cases.csv`
- raw_row_or_line: `phi_instr:4495:bc1d95214ca140dac45d768c9b0ab843b978b625`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/snippets/cclyzerpp_libsndfile_O2g_015562.source.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/snippets/cclyzerpp_libsndfile_O2g_015562.ir.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/snippets/cclyzerpp_libsndfile_O2g_015562.row.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/all_cases.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/relations;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/commands/command.txt;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/status/run_status.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/log/cclyzerpp.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/report/final_report.md;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/analysis_manifest.json;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/inventory/relation_row_counts.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/index/ir_instruction_index.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/map/native_fact_source_map.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g/ValueCases/report/final_native_output_analysis.md`

## Reported Location

- reported_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.c`
- reported_line: `289`
- reported_column: `22`
- location_validity: `column_out_of_range`
- source_region: `project_source`

## IR Anchor

- mode: `phi_instr`
- ir_function: `<llvm-link>:sfe_apply_metadata_changes`
- ir_instruction: `<llvm-link>:sfe_apply_metadata_changes:367`
- ir_line: ``
- ir_snippet:

```llvm
%291 = select i1 %289, i1 true, i1 %290, !dbg !87444
```

## Source / Message

- source_snippet:

```text
					{	tens *= 10 ;
```

- message: `Wanted-PhiMergeLocationDrift; phi_instr; ColumnOutOfRange; phi_incoming_count=2`
- root_cause_hint: `Mem2Reg_or_Phi-node_merge_or_CFG_simplification`
- inventory_confidence: `medium`
- notes: `source_exists=1; original_priority=P0; mapping_status=ColumnOutOfRange; phenomenon=Wanted-PhiMergeLocationDrift`

## Manual Study Checklist

- [x] Confirm all referenced artifacts exist.
- [x] Validate why the reported location is invalid or drifted.
- [x] Locate the IR instruction and debug metadata in the `.ll` file.
- [x] Build 1-3 candidate recovered source locations.
- [x] Run the LLM recovery prompt using `input.json`.
- [x] Verify the LLM output manually.
- [x] Write the paper-ready narrative below.

## Paper-Ready Narrative

cclyzer++ reports a `PhiMergeHotspot` candidate at `programs/common.c:289:22`. The
reported source location is invalid by column drift. In the normalized LLVM14
O2-g `.ll`, the flagged instruction is:

```llvm
%291 = select i1 %289, i1 true, i1 %290, !dbg !87444
```

with `!87444 = !DILocation(line: 289, column: 22, scope: !87443)` where
`!87443` is a lexical block inside `sfe_apply_metadata_changes`
(`programs/common.c:234`). The source line 289 is:

```c
{   tens *= 10 ;        // line 289 — arithmetic in a while-loop body
```

### The Drift: CFG Simplification Creates a Phantom Location

The `select` instruction in the IR is:

```
%289 = icmp eq %struct.sf_private_tag* %21, null     ← psf1 == NULL?
%290 = icmp eq %struct.sf_private_tag* %21, %22      ← psf1 == psf2?
%291 = select i1 %289, i1 true, i1 %290              ← psf1==NULL || psf1==psf2
```

This is a boolean short-circuit OR: `!psf1 || (psf1 == psf2)`. O2's CFG
Simplification pass transformed it from a conditional branch into a single
`select` (conditional move). The instruction was then scheduled into a
position in the optimized function where the nearest available debug
location was line 289 — but line 289 belongs to a completely different
control-flow region (a `while` loop body doing `tens *= 10` for number
width computation).

```
Source code layout                    O2-optimized IR layout
─────────────────────                ─────────────────────────
...                                    block %287:
if (psf1)                              ...
  ...                                  %289 = icmp eq psf1, null
                                       %290 = icmp eq psf1, psf2
...                                    %291 = select %289, true, %290
while (u / tens >= 10)                 br i1 %291, ...      ← uses result
{   tens *= 10 ;    ← line 289                              ← !dbg points HERE
    width ++ ;
}
```

O2's instruction scheduler merged the NULL-check and equality-check into one
`select`, and placed it adjacent to code whose debug location was from
line 289. The `select` inherited the debug location of the nearby code —
but line 289 is `tens *= 10`, a multiplication assignment, which has
nothing to do with the boolean OR logic.

### Column Out of Range

Column 22 on line 289 falls within the `*=` operator of `tens *= 10`.
The actual IR instruction is a boolean `select`, not an arithmetic
operation. The column is semantically out of range — it leads a developer
to a multiplication operator when the actual IR operation is a boolean
conditional move.

### Root Cause: O2 CFG Simplification + Instruction Scheduling

```
O2 CFG Simplification:
  if (cond) then ... else ...
      │
      ▼
  %x = select i1 cond, val_true, val_false   ← no branch, just a conditional move
      │
      ▼
O2 Instruction Scheduling:
  places the select near unrelated code (the while-loop body)
      │
      ▼
The select inherits the debug location of the nearby code (line 289:22)
      │
      ▼
cclyzer++: writes pos(refmode, 289, 22) → column 22 semantically wrong
```

### Recovered Source Location

The `select` instruction belongs to the NULL-pointer-guard logic in
`sfe_apply_metadata_changes`, not to line 289. The true source location
should be in the `270-295` range of `programs/common.c` where the
`psf` pointer checks and metadata application logic reside.

### Paper Taxonomy

This case demonstrates a variant of **时空错乱 (Trace-loss)** where the
line number is valid but the column is semantically wrong:
- O2 CFG Simplification replaces a branch with a `select`
- Instruction scheduling places the `select` near unrelated code
- The `select` inherits the debug location of the unrelated code
- The reported location (`line:289, col:22 = tens *= 10`) is
  plausibly valid syntax but semantically unrelated to the boolean logic

Unlike the SeaHorn/DG LineZero cases where the location is completely
absent (`0:0`), this is a **ColumnDrift** case where the location exists
but points to the wrong code. The developer reading this report would
be directed to a multiplication assignment, completely missing the
actual boolean logic. This is a subtler and arguably more dangerous
form of location drift — the location looks valid at first glance but
leads to wrong conclusions.
