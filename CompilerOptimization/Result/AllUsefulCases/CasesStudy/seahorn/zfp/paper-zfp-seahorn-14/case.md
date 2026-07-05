# paper-zfp-seahorn-14

## Identity

- repo: `zfp`
- tool: `seahorn`
- universe: `O2-g`
- selection_type: `repeat-location-variant`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `seahorn.zfp.O2g.000157`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/log/sea.smc.stats.typeoff.stderr.log`
- raw_row_or_line: `164`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/summary/all_cases.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/log/sea.smc.stats.typeoff.stderr.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/log/commands.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/report/final_report.md`

## Reported Location

- reported_file: `Target/zfp/include/zfp/bitstream.inl`
- reported_line: `0`
- reported_column: `0`
- location_validity: `line_zero`
- source_region: `project_source`

## IR Anchor

- mode: `smc_typeoff`
- ir_function: `stream_copy` (with inlined `stream_read_bits`)
- ir_instruction: `%31 = phi i64 [ %22, %25 ], [ %22, %24 ], [ poison, %28 ], !dbg !4775`
- ir_line: `CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.ll:8405`
- ir_snippet:

```llvm
%31 = phi i64 [ %22, %25 ], [ %22, %24 ], [ poison, %28 ], !dbg !401
```

> Note: This is the **same IR instruction** as case-13 (paper-zfp-seahorn-13).
> The `!dbg !401` in the SeaHorn log is SeaHorn's instrumented-bitcode metadata
> numbering; the corresponding normalized `.ll` metadata is `!4775`.
> See case-13 for the complete IR context, control-flow graph, and source mapping.

## Source / Message

- source_snippet:

```text
Same source as case-13: bitstream.inl:253-285 (stream_read_bits, inlined into stream_copy).

The phi node at block %30 merges the return value of stream_read_bits:

  if (s->bits < n) {          // line 257 — block %12, enters blocks %16/%24/%25
    ...
    if (!s->bits) {
      s->buffer = 0;          // line 269 — block %24: value = %22
    } else {
      ...
      value &= ...;           // line 275 — block %25: value = %22
    }
  }
  else {                      // line 278 — block %28: DEAD PATH
    s->bits -= n;             // line 280
    ...
    value &= (1 << n) - 1;    // line 282: n=64 → (1<<64) is UB
  }
  return value;               // line 284 — block %30: phi merges all three paths
```

- message: `Possible read of undefined value at`
- root_cause_hint: `Cross-step reproduction — same DCE-poison phi node as case-13, independently detected by smc_typeoff (no type-aware DSA, stats-only mode)`
- inventory_confidence: `0.95`
- notes: `all_cases_case_id=164;all_cases_step=07;all_cases_name=smc_typeoff;collected_from=all_cases.undefined_read_block;resolved_source=/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/include/zfp/bitstream.inl; This is case-13's sibling — same IR instruction, different pipeline step. The same phi poison is independently detected by three SeaHorn configurations: smc_typeoff (case 164, step 07), smc_typeon (case 322, step 08), and smc_instrument (case 6, step 09).`

## Manual Study Checklist

- [x] Confirm all referenced artifacts exist.
- [x] Validate why the reported location is invalid or drifted.
- [x] Locate the IR instruction and debug metadata in the `.ll` file.
- [x] Build 1-3 candidate recovered source locations.
- [x] Run the LLM recovery prompt using `input.json`.
- [x] Verify the LLM output manually.
- [x] Write the paper-ready narrative below.

## Paper-Ready Narrative

SeaHorn reports a possible read of an undefined value at
`Target/zfp/include/zfp/bitstream.inl:0:0` during the `smc_typeoff` step
(step 07). The flagged instruction is:

```
%31 = phi i64 [ %22, %25 ], [ %22, %24 ], [ poison, %28 ]
```

This is the **same IR instruction** as case-13 (paper-zfp-seahorn-13), but
detected by a **different pipeline configuration**.

### The Three Independent Detections

The same phi node with the same `poison` incoming edge is independently
flagged by all three SMC pipeline steps in the zfp fixed full matrix:

| Case ID | Step | Configuration | DSA Mode |
|---------|------|---------------|----------|
| 164 (this case) | 07 — `smc_typeoff` | `--print-smc-stats` | type-unaware |
| 322 | 08 — `smc_typeon` | `--print-smc-stats --sea-dsa-type-aware` | type-aware |
| 6 (case-13) | 09 — `smc_instrument` | `-o output.smc.bc` | type-unaware |

The three commands differ in their DSA configuration and output mode:

- **`smc_typeoff`** (this case): runs `sea smc-checks --print-smc-stats`
  without type-aware DSA — stats-only mode
- **`smc_typeon`**: same as typeoff but with `--sea-dsa-type-aware` enabled
- **`smc_instrument`** (case-13): runs `sea smc-checks` without
  `--print-smc-stats`, outputting an instrumented `.smc.bc` file

All three invoke the same underlying `seahorn` binary, which always runs
the `CanReadUndef` pass. The `poison` in the phi node is detected
regardless of DSA type-awareness.

### Paper Significance: Cross-Configuration Reproducibility

This case provides a distinct form of evidence compared to case-13:

1. **Tool-configuration independence**: The detection persists across
   different DSA configurations (type-aware vs. type-unaware) and across
   stats-only vs. instrumentation modes. This rules out the possibility
   that the finding is an artifact of a specific SeaHorn configuration.

2. **Multi-step corroboration**: Three independent invocations of the
   `CanReadUndef` pass on the same bitcode produce identical findings.
   This supports the paper's core claim that the problem originates in
   the **optimized IR itself** (the `poison` placed by O2's DCE), not in
   any particular tool's analysis choices.

3. **Redundancy as signal**: While `selection_type: repeat-location-variant`
   might appear to be "just a duplicate," in the paper's methodology it
   serves as a cross-validation mechanism — when multiple tool
   configurations independently flag the same IR artifact, the
   attribution to O2 optimization (rather than tool noise) is strengthened.

### Root Cause (Identical to Case-13)

The `poison` originates from O2's dead code elimination: when
`stream_read_bits` is inlined with the constant `n = 64`, the `else`
branch (`s->bits >= 64`) is provably unreachable (bitstream invariant
`s->bits < 64`). The compiler marks the phi incoming edge from the dead
block with `poison`. Multi-level inlining collapses the debug location
to `line: 0`. For the complete IR analysis, see case-13.

### Recovered Source Locations

Same as case-13:
1. `bitstream.inl:257` — the `if (s->bits < n)` branch point
2. `bitstream.inl:416` — the call site `stream_read_bits(src, wsize)` in `stream_copy`
3. `bitstream.inl:282` — the UB-triggering line in the dead else branch

### Relationship to Case-13

| Dimension | Case-13 | Case-14 (this case) |
|-----------|---------|---------------------|
| IR instruction | `%31 = phi ... poison` | **Same** |
| Pipeline step | 09 — `smc_instrument` | 07 — `smc_typeoff` |
| DSA config | type-unaware (instrument) | type-unaware (stats-only) |
| Paper role | Primary discovery | Cross-step reproducibility evidence |
| selection_type | `unique-location` | `repeat-location-variant` |

Both cases together demonstrate that the O2-induced poison artifact is a
**stable, tool-configuration-independent property of the optimized IR**,
not a quirk of any single SeaHorn invocation.
