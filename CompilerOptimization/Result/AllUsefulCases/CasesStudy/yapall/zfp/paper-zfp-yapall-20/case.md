# paper-zfp-yapall-20

## Identity

- repo: `zfp`
- tool: `yapall`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `yapall.zfp.O2g.001940781`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/log/CompilerOptimization_CompilerResult_zfp_LLVM14-O2-g_artifacts_zfp_O2_g_bc_subset_k0_default.log`
- raw_row_or_line: `line=35; kind=invalid_load; operand=zfp_encode_block_float_2:zfp_encode_block_float_2:534:24; allocation=*null`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/log/CompilerOptimization_CompilerResult_zfp_LLVM14-O2-g_artifacts_zfp_O2_g_bc_subset_k0_default.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/commands/commands.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/status/run_status.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/report/final_report.md;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/ValueCases/summary.md`

## Reported Location

- reported_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/template/encodef.c`
- reported_line: `0`
- reported_column: ``
- location_validity: `line_zero`
- source_region: `project_source`

## IR Anchor

- mode: `subset:k0:default`
- ir_function: `zfp_encode_block_float_2`
- ir_instruction: `zfp_encode_block_float_2:zfp_encode_block_float_2:534:24`
- ir_line: `24`
- ir_snippet:

```llvm
%549 = load %struct.bitstream*, %struct.bitstream** %548, align 8, !dbg !12037, !tbaa !1267
```

## Source / Message

- source_snippet:

```text

```

- message: `invalid_load issue; site_resolution=resolved_exact_operand_instruction; classification=Wanted-LineColumnMissing; all_classes=Wanted-LineColumnMissing;InlineAttributionDrift;WrongFunctionAttribution`
- root_cause_hint: `DWARF location drift;inline`
- inventory_confidence: `high`
- notes: `candidate_id=zfp_000000020; issue_id=69a99da45e28c45c; mapping_status=source_line_missing; token_at_column=; expected_token_kind=load-like pointer token; actual_token_kind=column_unknown; site_role=operand_definition; ll_source=native_compiler_artifact`

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

This case demonstrates a **triple-layer debug-info degradation** under O2: (1) inlining crosses a function boundary, (2) code hoisting collapses the debug location to `line: 0`, and (3) function attribution becomes wrong because the scope points to the inlined callee while the IR instruction resides in the caller. All three classifications — `Wanted-LineColumnMissing`, `InlineAttributionDrift`, and `WrongFunctionAttribution` — are triggered simultaneously, representing three dimensions of the same root phenomenon.

### Source Structure

`encodef.c` contains a public wrapper (`zfp_encode_block_float_2` at line 96) that delegates to a private implementation (`encode_block_float_2` at line 63):

```c
// Private implementation (line 63-90)
static uint
encode_block_float_2(zfp_stream* zfp, const float* fblock)
{
  uint bits = 1;
  int emax = exponent_block_float(fblock, BLOCK_SIZE);                    // line 67
  uint maxprec = precision(emax, zfp->maxprec, zfp->minexp, DIMS);       // line 68
  uint e = maxprec ? (uint)(emax + EBIAS) : 0;                           // line 69
  if (e) {                                                                // line 71 ← scope line
    stream_write_bits(zfp->stream, 2 * e + 1, bits);                     // line 75 ← stream use
    encode_block_int64_2(zfp->stream, ...);                               // line 79 ← stream use
  } else {
    stream_write_bit(zfp->stream, 0);                                     // line 83 ← stream use
  }
}

// Public wrapper (line 96-99)
size_t
zfp_encode_block_float_2(zfp_stream* zfp, const float* fblock)
{
  return REVERSIBLE(zfp)                                                  // line 98
    ? rev_encode_block_float_2(zfp, fblock)
    : encode_block_float_2(zfp, fblock);                                  // ← col 79: inlinedAt site
}
```

### O2 Optimization → Triple Classification

Under O2, `encode_block_float_2` is inlined into `zfp_encode_block_float_2` at line 98. Then, inside the inlined body, `zfp->stream` — which is used at lines 75, 79, and 83 across the `if (e)` / `else` branches — is **hoisted** above the `if (e)` check and merged into a single load instruction:

```llvm
; ★ Hoisted from inside encode_block_float_2 — scope=callee, line=0
%548 = getelementptr ... %0, i32 4     ; &zfp->stream      !dbg !12037 (line:0)
%549 = load ... %548                     ; zfp->stream       !dbg !12037 (line:0) ← TARGET

; ★ The if(e) branch retains its line:
br i1 %547, label %932, label %550       ;                    !dbg !12038 (line:71)
```

The debug metadata reveals the triple anomaly:
```
!12037 = DILocation(line: 0, scope: !12021, inlinedAt: !12023)
  scope:     !12021 → encode_block_float_2, line 71  (callee's if(e) block)
  inlinedAt: !12023 → zfp_encode_block_float_2, line 98, col 79 (caller's call site)
```

### Why Three Classifications Fire

| Classification | Mechanism | Evidence |
|---|---|---|
| **Wanted-LineColumnMissing** | `DILocation(line: 0)` | Hoisting merged `zfp->stream` from three source locations across if/else → no single line |
| **InlineAttributionDrift** | `inlinedAt` chain exists | Callee `encode_block_float_2` is inlined into caller `zfp_encode_block_float_2` |
| **WrongFunctionAttribution** | `ir_function ≠ scope_function` | IR function is `zfp_encode_block_float_2`; scope function is `encode_block_float_2` |

### Contrast: Why Some Instructions Keep Their Line

`zfp->maxprec` at line 68 retains `!dbg !12024 (line:68)` because it is accessed **once**, before the `if (e)` branch. It is not shared across branches, so no merging/hoisting occurs — the debug location survives intact. This contrast confirms that `line: 0` is specifically caused by hoisting of shared subexpressions.

### Correct Location Recovery

The `zfp->stream` load serves three distinct source locations (lines 75, 79, 83). After hoisting and merging, no single column-level recovery is possible. The best function-level recovery points to the scope function `encode_block_float_2` at line 75 (`stream_write_bits(zfp->stream, ...)`) — the primary semantic use of the loaded value.

### Significance for the Paper

1. **Multi-dimensional degradation**: This case shows that a single O2 optimization (inlining + hoisting) can simultaneously trigger three distinct location-mismatch classifications
2. **Hoisting vs non-hoisting contrast**: The side-by-side comparison of `zfp->maxprec` (line preserved) vs `zfp->stream` (line:0) provides direct evidence that hoisting is the proximate cause
3. **Template amplification**: Like case 19, the C template structure concentrates complexity into few source lines, magnifying the effect of each optimization
4. **Cascading inline+hoist**: Demonstrates that the line:0 problem from case 19 is compounded when the hoisted code crosses an inline boundary, creating additional function-attribution problems
