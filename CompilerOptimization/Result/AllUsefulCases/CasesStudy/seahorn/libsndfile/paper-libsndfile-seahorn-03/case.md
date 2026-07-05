# paper-libsndfile-seahorn-03

## Identity

- repo: `libsndfile`
- tool: `seahorn`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `seahorn.libsndfile.O2g.000308`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/log/sea.smc.instrument.stderr.log`
- raw_row_or_line: `313`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/summary/all_cases.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/log/sea.smc.instrument.stderr.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/log/commands.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/report/final_report.md`

## Reported Location

- reported_file: `Target/libsndfile/src/GSM610/short_term.c`
- reported_line: `0`
- reported_column: `0`
- location_validity: `line_zero`
- source_region: `project_source`

## IR Anchor

- mode: `smc_instrument`
- ir_function: `Fast_Short_term_synthesis_filtering`
- ir_instruction: `%51 = insertelement <8 x float> poison, float %13, i64 0, !dbg !79763`
- ir_line: `CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.ll:115507`
- ir_snippet:

```llvm
%51 = insertelement <8 x float> poison, float %13, i64 0, !dbg !6786
```

- normalized_input_ir_snippet:

```llvm
%12 = load i16, i16* %11, align 2, !dbg !79764, !tbaa !7229
%13 = sitofp i16 %12 to float, !dbg !79764
...
%50 = icmp eq i32 %2, 0, !dbg !79771
%51 = insertelement <8 x float> poison, float %13, i64 0, !dbg !79763
%52 = shufflevector <2 x float> %25, <2 x float> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>, !dbg !79763
```

- debug_metadata:

```llvm
!79748 = distinct !DISubprogram(name: "Fast_Short_term_synthesis_filtering", scope: !78917, file: !78917, line: 293, type: !79699, scopeLine: 300, ...)
!79763 = !DILocation(line: 0, scope: !79748)
!79764 = !DILocation(line: 308, column: 13, scope: !79765)
!79771 = !DILocation(line: 311, column: 2, scope: !79748)
```

## Source / Message

- source_snippet:

```text
307     for (i = 0 ; i < 8 ; ++i)
308     {   va [i]  = v [i] ;
309         rrpa [i] = (float) rrp [i] * scalef ;
310         }
311     while (k--) {
```

- message: `Possible read of undefined value at`
- root_cause_hint: `O2 vectorization/debug-location collapse to line-zero DILocation`
- inventory_confidence: `0.95`
- notes: `all_cases_case_id=313;all_cases_step=06;all_cases_name=smc_instrument;collected_from=all_cases.undefined_read_block;resolved_source=/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/GSM610/short_term.c; raw SeaHorn log prints !dbg !6786, but the normalized LLVM14 input .ll carries the same instruction as !dbg !79763; the metadata node itself is line 0 in function scope`

## Manual Study Checklist

- [x] Confirm all referenced artifacts exist.
- [x] Validate why the reported location is invalid or drifted.
- [x] Locate the IR instruction and debug metadata in the `.ll` file.
- [x] Build 1-3 candidate recovered source locations.
- [x] Run the LLM recovery prompt using `input.json`.
- [x] Verify the LLM output manually.
- [x] Write the paper-ready narrative below.

## Paper-Ready Narrative

SeaHorn reports a possible read of an undefined value in
`Target/libsndfile/src/GSM610/short_term.c:0:0` for an O2-g bitcode instruction:
`%51 = insertelement <8 x float> poison, float %13, i64 0`. The reported
source location is invalid. In the normalized LLVM14 O2-g `.ll`, the same
instruction appears inside `Fast_Short_term_synthesis_filtering` at IR line
115507 and is annotated with `!79763 = !DILocation(line: 0, scope: !79748)`.
The scope `!79748` is the optimized local function
`Fast_Short_term_synthesis_filtering`, whose source definition starts at
`short_term.c:293`.

The nearest recoverable source semantics are the vectorized initialization of
the local synthesis-state array:

```c
for (i = 0 ; i < 8 ; ++i)
{   va [i]  = v [i] ;
    rrpa [i] = (float) rrp [i] * scalef ;
    }
while (k--) {
```

The operand `%13` is produced from a load of `S->v[1]` with a valid debug
location at `short_term.c:308:13`, and `%51/%52/%54/%55` assemble vector
fragments of `va[1..7]` before entering the loop at line 311. Therefore the
best recovered location for this particular raw row is `short_term.c:308`
(`va [i] = v [i]`), with `short_term.c:311` as a secondary nearby control-flow
candidate. This should be treated as `FP-LocationDrift` / line-zero debug
location collapse, not as a trustworthy source-level undefined-read location.

The O2-g compilation evidence is valid for the main universe: the recorded
compile command for `short_term.c` is `clang-14 -O2 -g -std=gnu99`, with no
`-DNDEBUG`. No local SeaHorn O0 or O2-noinline run directory exists for this
target, so inline-specific attribution is not supported by the current evidence.
