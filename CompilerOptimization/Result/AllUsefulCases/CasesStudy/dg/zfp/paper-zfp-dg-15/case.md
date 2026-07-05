# paper-zfp-dg-15

## Identity

- repo: `zfp`
- tool: `dg`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `dg.zfp.O2g.0000001`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/dg/dg-LLVM14-O2-g/high_precision_20260402_154412`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/dg/dg-LLVM14-O2-g/high_precision_20260402_154412/work/zfp.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/dg/dg-LLVM14-O2-g/high_precision_20260402_154412/log/cda_dod.pass1.lines.stdout.log`
- raw_row_or_line: `3`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/dg/dg-LLVM14-O2-g/high_precision_20260402_154412/summary/line_hits.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/dg/dg-LLVM14-O2-g/high_precision_20260402_154412/log/cda_dod.pass1.lines.stdout.log`

## Reported Location

- reported_file: ``
- reported_line: `0`
- reported_column: `0`
- location_validity: `line_zero`
- source_region: `unknown`

## IR Anchor

- mode: `cda_dod`
- ir_function: `zfp_read_header`
- ir_instruction: `call void @llvm.dbg.value(metadata i64 %35, metadata !4257, metadata !DIExpression()), !dbg !4267`
- ir_line: `zfp.ll:7627`
- ir_snippet:

```llvm
call void @llvm.dbg.value(metadata i64 %35, metadata !4257, metadata !DIExpression()), !dbg !4267
```

- normalized_input_ir_snippet:

```llvm
; zfp_read_header — the entire function; every dbg.value uses !dbg !4267 (line:0)
define i64 @zfp_read_header(%struct.zfp_stream* %0, %struct.zfp_field* %1, i32 %2) !dbg !4250 {

block %3:   ; function entry — dbg.value(0:0)×4
  call void @llvm.dbg.value(metadata %struct.zfp_stream* %0, ...), !dbg !4267
  call void @llvm.dbg.value(metadata %struct.zfp_field* %1, ...), !dbg !4267
  call void @llvm.dbg.value(metadata i32 %2, ...), !dbg !4267
  call void @llvm.dbg.value(metadata i64 0, ...), !dbg !4267
  br i1 %5, label %23, label %6                       ; mask & ZFP_HEADER_MAGIC ?

block %6:   ; read magic bytes 'z' 'f' 'p' version → check → %23 or %57(return 0)
  ...

block %23:  ; merge after MAGIC check — dbg.value(0:0)
  call void @llvm.dbg.value(metadata i64 %24, ...), !dbg !4267
  br i1 %26, label %34, label %27                     ; mask & ZFP_HEADER_META ?

block %27:  ; read META
  %30 = tail call i64 @stream_read_bits(...)           ; read metadata bits
  call void @llvm.dbg.value(metadata i64 %30, ...), !dbg !4267   ; dbg.value(0:0)
  %31 = tail call i32 @zfp_field_set_metadata(...), !dbg !4294   ; ← 1278:10
  %32 = icmp eq i32 %31, 0, !dbg !4294
  call void @llvm.dbg.value(metadata i64 undef, ...), !dbg !4267 ; dbg.value(0:0)
  br i1 %32, label %57, label %34                      ; success → %34, fail → return 0

block %34:  ; merge after META — THIS IS WHERE THE 0:0 DEPENDENT LIVES
  %35 = phi i64 [ %33, %27 ], [ %24, %23 ]
  call void @llvm.dbg.value(metadata i64 %35, ...), !dbg !4267   ; ← THE 0:0 INSTRUCTION
  br i1 %37, label %55, label %38                     ; mask & ZFP_HEADER_MODE ?

block %57:  ; return point — phi merges all failure paths
  %58 = phi i64 [ %56, %55 ], [ 0, %50 ], [ 0, %27 ], ...
  ret i64 %58
}
```

- debug_metadata:

```llvm
!4267 = !DILocation(line: 0, scope: !4250)
!4250 = distinct !DISubprogram(name: "zfp_read_header", scope: !82, file: !82, line: 1265, ...,
    spFlags: DISPFlagDefinition | DISPFlagOptimized)
!82 = !DIFile(filename: "Target/zfp/src/zfp.c", ...)

!4294 = !DILocation(line: 1278, column: 10, scope: !4295)
!4295 = distinct !DILexicalBlock(scope: !4259, file: !82, line: 1278, column: 9)
```

## Source / Message

- source_snippet:

```text
zfp.c:1265-1295 — zfp_read_header

1265: static size_t
1266: zfp_read_header(zfp_stream* zfp, zfp_field* field, uint mask)
1267: {
1268:   size_t bits = 0;
1269:   if (mask & ZFP_HEADER_MAGIC) {
1270:     if (stream_read_bits(zfp->stream, 8) != 'f' ||
1271:         stream_read_bits(zfp->stream, 8) != 'p' ||
1272:         stream_read_bits(zfp->stream, 8) != zfp_codec_version)
1273:       return 0;
1274:     bits += ZFP_MAGIC_BITS;
1275:   }
1276:   if (mask & ZFP_HEADER_META) {
1277:     uint64 meta = stream_read_bits(zfp->stream, ZFP_META_BITS);
1278:     if (!zfp_field_set_metadata(field, meta))   // ← 1278:10 (the !)
1279:       return 0;
1280:     bits += ZFP_META_BITS;
1281:   }
1282:   if (mask & ZFP_HEADER_MODE) {
1283:     uint64 mode = stream_read_bits(zfp->stream, ZFP_MODE_SHORT_BITS);
1284:     bits += ZFP_MODE_SHORT_BITS;
1285:     if (mode > ZFP_MODE_SHORT_MAX) {
1286:       uint size = ZFP_MODE_LONG_BITS - ZFP_MODE_SHORT_BITS;
1287:       mode += stream_read_bits(zfp->stream, size) << ZFP_MODE_SHORT_BITS;
1288:       bits += size;
1289:     }
1290:     if (zfp_stream_set_mode(zfp, mode) == zfp_mode_null)
1291:       return 0;
1292:     bits += ZFP_MODE_BITS;
1293:   }
1294:   return bits;
1295: }
```

- message: `0:0 -> 1278:10`
- root_cause_hint: `O2 collapses ALL dbg.value debug locations in zfp_read_header to line:0 — function-scope, not from inlining`
- inventory_confidence: `0.95`
- notes: `source_resolution=missing;summary_csv=line_hits.csv;summary_row=2;source_candidate_index=1;source_count=0;native_output_line=3; resolved_source=/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/zfp.c; The entire function zfp_read_header (98 lines of IR) has every dbg.value annotated with !4267 = !DILocation(line: 0, scope: !4250). O2 wrote line:0 directly on the function scope — NOT through an inlinedAt chain. This is a different mechanism from case-13 (zfp seahorn) where line:0 came from triple-inlined functions.`

## Manual Study Checklist

- [x] Confirm all referenced artifacts exist.
- [x] Validate why the reported location is invalid or drifted.
- [x] Locate the IR instruction and debug metadata in the `.ll` file.
- [x] Build 1-3 candidate recovered source locations.
- [x] Run the LLM recovery prompt using `input.json`.
- [x] Verify the LLM output manually.
- [x] Write the paper-ready narrative below.

## Paper-Ready Narrative

DG's CDA (DOD mode) reports a control dependence edge `0:0 -> 1278:10` in
`zfp_read_header` (zfp.c:1265). The reported source location `0:0` is
invalid — line 0 does not exist in any source file.

### The 0:0 Source

In the O2-g bitcode for zfp, the function `zfp_read_header` has EVERY
`dbg.value` intrinsic annotated with the same debug location:

```llvm
!4267 = !DILocation(line: 0, scope: !4250)
!4250 = distinct !DISubprogram(name: "zfp_read_header", file: !82, line: 1265, ...)
```

The `line: 0` is directly scoped to `zfp_read_header` itself — it is NOT
produced by an `inlinedAt` chain. This is a case where O2 collapsed the
debug locations of the function's own variable-tracking intrinsics to
line 0, without any cross-function inlining being the direct cause.

### The 1278:10 Target

The target `1278:10` corresponds to the conditional branch at zfp.c:1278:

```c
if (!zfp_field_set_metadata(field, meta))
    return 0;
```

In the IR, this branch (`br i1 %32, label %57, label %34`) controls whether
execution reaches block `%34`, where the `bits` counter is updated via a
`dbg.value` annotated with `!dbg !4267` (line:0).

### The CDA Edge: Verified Control Flow

DG's CDA correctly computes this control dependence:

1. Block `%27` contains the `zfp_field_set_metadata` call and the branch
   `br i1 %32`. The branch has debug location `1278:10`.
2. Block `%34` is reached ONLY when `zfp_field_set_metadata` succeeds
   (`%32 == 0`). The `dbg.value` in this block tracks the updated `bits`
   value.
3. Block `%34` is in the post-dominance frontier of block `%27` — the
   branch at `%27` determines whether `%34` executes. Therefore, every
   instruction in block `%34` is control-dependent on the terminator of
   block `%27`.
4. DG's `dumpCda()` iterates over block `%34`'s instructions, calls
   `getInstName()` on each, and prints the dependency edge.

When `getInstName()` is called on the `dbg.value` in block `%34`, it reads
`getDebugLoc().getLine()` = 0, producing `0:0`. The dependency is the
branch at `1278:10`. The output is `0:0 -> 1278:10`.

### Why O2 Collapsed the Debug Location

Unlike case-13 (zfp seahorn) where `line: 0` came from triple-inlined
SSE intrinsics, this case demonstrates a different mechanism: O2 assigns
`line: 0` to ALL `dbg.value` instructions in `zfp_read_header` at the
function scope level. The function calls `stream_read_bits` and
`zfp_field_set_metadata` — both defined as `inline_` in headers. After
inlining and optimization, O2 can no longer map the variable-tracking
`dbg.value` intrinsics back to specific source lines within the function,
and defaults to `line: 0`.

The scope `!4250` carries `spFlags: DISPFlagOptimized`, confirming that
O2 optimization passes processed this function.

### The DG Output in Context

The full CDA output for this function shows the dependency graph around `1278:10`:

```
1278:10 -> 1278:10       ; self-dependence (block-level)
1278:9 -> 1278:10        ; the ! operator at column 9
0:0 -> 1278:10           ; ← the dbg.value in block %34 (this case)
(no dbg) br i1 %32...    ; a branch with no debug location at all
0:0 -> 1278:10           ; another dbg.value in another dependent block
1282:12 -> 1278:10        ; the MODE check also depends on the META check
```

The `0:0` entries (3 total) and the `(no dbg)` entry together demonstrate
that O2 has degraded debug information in multiple ways within this single
function — some instructions lost their line number entirely (line:0),
while others lost ALL debug metadata (no dbg).

### Recovered Source Locations

The `dbg.value` in block `%34` tracks the `bits` variable. The best
recovered source locations are:

1. **zfp.c:1280** — `bits += ZFP_META_BITS;` — this is the line where
   `bits` is updated after a successful metadata read, exactly matching
   the semantics of the `dbg.value` in block `%34`.
2. **zfp.c:1274** — `bits += ZFP_MAGIC_BITS;` — the MAGIC block's
   equivalent bits update, merged via phi in block `%34`.
3. **zfp.c:1268** — `size_t bits = 0;` — the initialization, tracked by
   the dbg.value at function entry (also line:0).

### Paper Taxonomy Fit

This case maps to **时空错乱 (Trace-loss)** in a distinct variant:

- **Not from inlining**: The `line: 0` scope is the function itself
  (`!4250 = zfp_read_header`), not an inlined callee. This is the
  function's own debug information being collapsed.
- **Not from a branch**: The `0:0` instruction is a `dbg.value` (variable
  tracking intrinsic), not a conditional branch. The CDA edge correctly
  identifies that this tracking point is control-dependent on a real
  branch — but the tracking point's location is lost.
- **Systemic within the function**: ALL `dbg.value` calls in
  `zfp_read_header` use the same `line: 0` debug location. This is not a
  single-instruction anomaly but a function-wide debug info degradation.

### Comparison with Related Cases

| Dimension | SeaHorn case-13 (zfp) | DG case-05 (libsndfile) | **DG case-15 (zfp)** |
|-----------|----------------------|------------------------|---------------------|
| line:0 scope | inlined function (inlinedAt) | function itself | **function itself** |
| IR instruction | phi node | dbg.value | **dbg.value** |
| O2 mechanism | triple-inline + DCE poison | O2 dbg.value collapse | **O2 dbg.value collapse (function-wide)** |
| Tool output type | bug report (FP) | dependency edge | **dependency edge** |
| CDA edge verifiable | N/A (SeaHorn) | partially | **fully — exact CFG path traced** |

The O2-g compilation evidence is valid: the recorded compile command uses
`clang-14 -O2 -g` with no `-DNDEBUG`. No local DG O0 or O2-noinline run
directory exists for this target.
