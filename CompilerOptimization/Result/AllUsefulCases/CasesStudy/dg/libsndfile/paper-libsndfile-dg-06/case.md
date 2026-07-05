# paper-libsndfile-dg-06

## Identity

- repo: `libsndfile`
- tool: `dg`
- universe: `O2-g`
- selection_type: `repeat-location-variant`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `dg.libsndfile.O2g.0003190`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/work/libsndfile_convert.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/log/cda_dod_ntscd.lines.stdout.log`
- raw_row_or_line: `11`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/summary/line_hits.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/log/cda_dod_ntscd.lines.stdout.log`

## Reported Location

- reported_file: ``
- reported_line: `0`
- reported_column: `0`
- location_validity: `line_zero`
- source_region: `unknown`

## IR Anchor

- mode: `cda_dod_ntscd`
- ir_function: `aiff_open` (same line:0 branch as case-05: `br i1 %1023, label %1031, label %1026, !dbg !42042`)
- ir_instruction: `br i1 %1023, label %1031, label %1026, !dbg !42042`
- ir_line: `CompilerResult/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/work/libsndfile_convert.ll:64013`
- ir_snippet:

```llvm
br i1 %1023, label %1031, label %1026, !dbg !42042
```

- debug_metadata:

```llvm
!42042 = !DILocation(line: 0, scope: !41936, inlinedAt: !42036)
!41936 = distinct !DISubprogram(name: "aiff_read_header", file: "aiff.c", line: 398, spFlags: DISPFlagOptimized)
!42036 = distinct !DILocation(line: 249, column: 17, scope: aiff.c:249)
```

> Note: This is the same line:0 branch as case-05. The target `113:2` maps to 4 different source files due to inline-induced multi-file ambiguity.

## Source / Message

- source_snippet:

```text
Target 113:2 maps to 4 files — inline-induced multi-file ambiguity:

ALACBitUtilities.c:113 — bit buffer manipulations (BitBufferPeek)
g721.c:113 — ADPCM decoder filter (update function call)
avr.c:113 — AVR header reader (psf_binheader_readf call)
common.c:113 — psf_log_printf format string parser

All four are inline-expanded helper functions whose control flow has been
merged by O2. The same IR instruction (branch with line:0 from inlined
aiff_read_header) controls code in all four compilation contexts.
```

- message: `0:0 -> 113:2`
- root_cause_hint: `O2 multi-level inline → debug location collapse to line:0 → NTSCD amplifies the edge count 10x vs DOD alone`
- inventory_confidence: `0.95`
- notes: `all_cases_case_id=3190;all_cases_step=cda_dod_ntscd;collected_from=all_cases.undefined_read_block;native_output_line=11;source_resolution=missing;summary_csv_row=1549;source_count=0 for 0:0, source_count=4 for 113:2; This is the cross-algorithm validation case for case-05 — same line:0 branch artifact detected by a different CDA variant. DOD+NTSCD produces 42,080 line:0 edges vs only 3,938 for DOD alone — a 10.7x amplification.`

## Manual Study Checklist

- [x] Confirm all referenced artifacts exist.
- [x] Validate why the reported location is invalid or drifted.
- [x] Locate the IR instruction and debug metadata in the `.ll` file.
- [x] Build 1-3 candidate recovered source locations.
- [x] Run the LLM recovery prompt using `input.json`.
- [x] Verify the LLM output manually.
- [x] Write the paper-ready narrative below.

## Paper-Ready Narrative

DG's CDA in DOD+NTSCD mode reports a control dependence edge `0:0 -> 113:2`
in `cda_dod_ntscd.lines.stdout.log:11`. The source location `0:0` is
invalid (line 0). The target `113:2` maps to 4 different source files:
`ALACBitUtilities.c:113`, `g721.c:113`, `avr.c:113`, and `common.c:113`
— a case of inline-induced multi-file ambiguity.

The `0:0` source is the same line:0 conditional branch as case-05:
`br i1 %1023, label %1031, label %1026, !dbg !42042` in the `aiff_open`
function, with `!42042 = !DILocation(line: 0, scope: !41936, inlinedAt: !42036)`
where `!41936` is the inlined `aiff_read_header` function (`aiff.c:398`).
The debug location collapsed to `line: 0` because O2 could not precisely
map the optimized branch back to a single source line after inlining
`aiff_read_header` into `aiff_open`.

### Cross-Algorithm Amplification

This case's primary paper value lies in the **quantitative comparison**
between CDA algorithm variants:

| CDA Mode | line:0 edges | Amplification |
|----------|-------------|---------------|
| `cda_dod` (case-05) | 3,938 | 1× (baseline) |
| `cda_dod_ntscd` (this case) | **42,080** | **10.7×** |

DOD (Decisive Order Dependence) captures standard control dependencies,
finding ~4K edges whose source has collapsed to line:0. NTSCD
(Non-Termination Sensitive Control Dependence) adds dependencies arising
from non-terminating paths (infinite loops, `abort()`, etc.). The 10.7×
amplification means that **the majority of line:0 artifacts in the IR
are associated with non-termination-sensitive control flow paths** —
loops and exit conditions whose debug locations were aggressively
collapsed by O2's CFG transformations.

### Mechanism

```
O2 inlines aiff_read_header → aiff_open
    │
    ▼
O2 CFG transformations (Loop Unroll, Jump Threading, CFG Simplify)
    │
    ▼
Conditional branch debug location collapses to !DILocation(line: 0, ...)
    │
    ▼
DG DOD tracing finds the branch controls 4 instruction instances (113:2 in
4 different inlined contexts)
    │
    ▼
DG DOD+NTSCD additionally traces non-termination paths through the same
branch → 10.7× more edges exposed
    │
    ▼
Output: thousands of "0:0 -> X:Y" edges
```

### Recovered Source Locations

Since the branch is from inlined `aiff_read_header`:
1. `aiff.c:249` — the call site where `aiff_read_header` was inlined
2. `aiff.c:398` — the `aiff_read_header` function definition
3. For target `113:2`: any of the 4 files (ALACBitUtilities.c, g721.c, avr.c, common.c)

### Relationship to Case-05

| Dimension | Case-05 | Case-06 (this case) |
|-----------|---------|---------------------|
| CDA algorithm | DOD | DOD + NTSCD |
| IR source | `br i1 %1023 ... !dbg !42042` | **Same** |
| Target line | 313:15 | 113:2 |
| line:0 edges (total) | 3,938 | 42,080 |
| selection_type | `unique-location` | `repeat-location-variant` |
| Paper role | Primary discovery | Cross-algorithm amplification evidence |

This case demonstrates that more comprehensive CDA algorithms expose
proportionally MORE O2-induced line:0 artifacts — the problem scales
with analysis depth, not just with code size.
