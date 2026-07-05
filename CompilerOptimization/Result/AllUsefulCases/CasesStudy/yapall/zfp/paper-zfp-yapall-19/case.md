# paper-zfp-yapall-19

## Identity

- repo: `zfp`
- tool: `yapall`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `yapall.zfp.O2g.001940763`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/log/CompilerOptimization_CompilerResult_zfp_LLVM14-O2-g_artifacts_zfp_O2_g_bc_subset_k0_default.log`
- raw_row_or_line: `line=17; kind=invalid_load; operand=zfp_decode_block_int64_2:zfp_decode_block_int64_2:2:8; allocation=*null`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/log/CompilerOptimization_CompilerResult_zfp_LLVM14-O2-g_artifacts_zfp_O2_g_bc_subset_k0_default.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/commands/commands.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/status/run_status.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/report/final_report.md;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/ValueCases/summary.md`

## Reported Location

- reported_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/template/decodei.c`
- reported_line: `0`
- reported_column: ``
- location_validity: `line_zero`
- source_region: `project_source`

## IR Anchor

- mode: `subset:k0:default`
- ir_function: `zfp_decode_block_int64_2`
- ir_instruction: `zfp_decode_block_int64_2:zfp_decode_block_int64_2:2:8`
- ir_line: `8`
- ir_snippet:

```llvm
%9 = load %struct.bitstream*, %struct.bitstream** %8, align 8, !dbg !18006, !tbaa !1267
```

## Source / Message

- source_snippet:

```text

```

- message: `invalid_load issue; site_resolution=resolved_exact_operand_instruction; classification=Wanted-LineColumnMissing; all_classes=Wanted-LineColumnMissing`
- root_cause_hint: `DWARF location drift`
- inventory_confidence: `high`
- notes: `candidate_id=zfp_000000002; issue_id=ad1e554fe4a0c51d; mapping_status=source_line_missing; token_at_column=; expected_token_kind=load-like pointer token; actual_token_kind=column_unknown; site_role=operand_definition; ll_source=native_compiler_artifact`

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

This case demonstrates **O2 code-hoisting causing DWARF `line: 0` collapse** in a C template function. yapall reported `decodei.c:0` (LineZero) for an `invalid_load` issue. The debug metadata `!18006 = !DILocation(line: 0, scope: !17976)` explicitly records line 0 — this is LLVM's standard mechanism to mark compiler-synthesized/merged instructions that no longer have a unique source position. The root cause is O2 hoisting of common struct-field accesses (`zfp->stream`, `zfp->minbits`, `zfp->maxbits`) from two ternary branches into a single shared instruction above the branch, causing the debug location to collapse to line 0. This is a genuine debug-info quality degradation, not a tool artifact.

### The Template Source

`decodei.c` is zfp's C template for integer block decoding. The function body is a single line:

```c
// decodei.c line 7-10
size_t
_t2(zfp_decode_block, Int, DIMS)(zfp_stream* zfp, Int* iblock)
{
  return REVERSIBLE(zfp) ? _t2(rev_decode_block, Int, DIMS)(zfp->stream, zfp->minbits, zfp->maxbits, iblock)
                         : _t2(decode_block, Int, DIMS)(zfp->stream, zfp->minbits, zfp->maxbits, zfp->maxprec, iblock);
}
```

When `Int=int64, DIMS=2`, the template instantiates as `zfp_decode_block_int64_2`. The macro `REVERSIBLE(zfp)` expands to `((zfp)->minexp < -1074)`.

### O2 Transformation → line:0

Under O2, LLVM performs **code hoisting** (GVN/early-cse): the common field accesses `zfp->stream`, `zfp->minbits`, `zfp->maxbits` that appear identically in both ternary branches are hoisted above the conditional:

```llvm
; ★ Hoisted loads — line:0
%8 = getelementptr ... %0, i32 4     ; &zfp->stream       !dbg !18006 (line:0)
%9 = load ... %8                      ; zfp->stream        !dbg !18006 (line:0) ← yapall target
%10 = getelementptr ... %0, i32 0     ; &zfp->minbits       !dbg !18006 (line:0)
%11 = load ... %10                     ; zfp->minbits        !dbg !18006 (line:0)
%12 = getelementptr ... %0, i32 1     ; &zfp->maxbits       !dbg !18006 (line:0)
%13 = load ... %12                     ; zfp->maxbits        !dbg !18006 (line:0)

; ★ Condition — line:9 (unique to REVERSIBLE macro)
%5 = getelementptr ... %0, i32 3      ; &zfp->minexp        !dbg !18007 (line:9)
%6 = load ... %5                       ; zfp->minexp         !dbg !18007 (line:9)
%7 = icmp slt i32 %6, -1074            ; minexp < -1074     !dbg !18007 (line:9)
br i1 %7, label %14, label %199        ;                      !dbg !18007 (line:9)
```

The condition (`zfp->minexp < -1074`) retains `line:9` because it is NOT shared — it's unique to the `REVERSIBLE` macro expansion. The hoisted field accesses get `line:0` because the merged instruction belongs to both branches simultaneously, and LLVM's policy is to set `line: 0` when no single source location can be assigned.

### Cascading line:0 Through Inlining

The hoisted instructions are further affected by inlining. The ternary branches call `rev_decode_block_int64_2` and `decode_block_int64_2`, which themselves call `stream_read_bits`. All three functions' prologues exhibit the same `line: 0` pattern:

```
!18006 = !DILocation(line: 0, scope: !17976)              ← decodei.c (outer function)
!18019 = !DILocation(line: 0, scope: !18009, inlinedAt: !18020)  ← revdecode.c (inlined)
!18028 = !DILocation(line: 0, scope: !18022, inlinedAt: !18029)  ← inline.c (doubly inlined)
```

### yapall's invalid_load

yapall reports `invalid_load` because its k=0, flow-insensitive analysis associates the load operand with `*null` — the analysis cannot prove that `zfp->stream` is non-null. This is a pointer-analysis over-approximation (in a well-formed `zfp_stream`, the `stream` field is always valid), not a real program bug.

### Correct Location Recovery

The load instruction `%9` corresponds to the `zfp->stream` access in line 9. Since `zfp->stream` appears in both ternary branches at the same syntactic position (first argument), the correct recovery is:

- **File**: `Target/zfp/src/template/decodei.c`
- **Line**: 9
- **Granularity**: function-level only — precise column recovery is impossible because the instruction was merged from two source locations

### Significance for the Paper

1. **Canonical line:0 collapse**: demonstrates LLVM's documented behavior of setting `line: 0` when instruction hoisting merges code from multiple source positions
2. **Cascading effect with inlining**: shows how line:0 propagates through nested inline chains, creating entire prologues without debug location
3. **Template magnification**: C template functions with single-line bodies are particularly susceptible — the entire function body is one line, so any hoisting immediately loses all column information
4. **Distinct from tool bug**: unlike the cclyzer++ file-disambiguation case, this is a real debug-info quality degradation caused by the compiler optimizer
