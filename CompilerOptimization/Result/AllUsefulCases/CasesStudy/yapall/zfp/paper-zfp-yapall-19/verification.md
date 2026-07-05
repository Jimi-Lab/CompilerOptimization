# Verification: paper-zfp-yapall-19

## Verdict

- label: `function-only`  <!-- exact | nearby | function-only | wrong | unrecoverable -->
- verified_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/template/decodei.c`
- verified_line: `9`
- verified_source_text: `return REVERSIBLE(zfp) ? _t2(rev_decode_block, Int, DIMS)(zfp->stream, zfp->minbits, zfp->maxbits, iblock) : _t2(decode_block, Int, DIMS)(zfp->stream, zfp->minbits, zfp->maxbits, zfp->maxprec, iblock);`

## Checks

- [x] Raw artifact line/row matches `input.json`.
- [x] Reported location invalidity is independently confirmed.
- [x] IR instruction and debug metadata are located.
- [x] Recovered line is checked against the source tree.
- [x] If inline is claimed, caller/callee attribution is separated.
- [x] If evidence is insufficient, `unrecoverable` is justified rather than guessed.

## Evidence Notes

### Raw Issue Verification

Raw log line 17 confirms:
```
invalid_load	zfp_decode_block_int64_2:zfp_decode_block_int64_2:2:8	*null
```

This matches `input.json`: `kind=invalid_load; operand=zfp_decode_block_int64_2:zfp_decode_block_int64_2:2:8; allocation=*null`.

### Debug Metadata Chain

```
IR instruction (line 44915 in .ll):
  %9 = load %struct.bitstream*, %struct.bitstream** %8, align 8, !dbg !18006, !tbaa !1267

!18006 = !DILocation(line: 0, scope: !17976)           ← line: 0!
!17976 = !DISubprogram(name: "zfp_decode_block_int64_2",
                        file: !10290, line: 7, scopeLine: 8)
!10290 = !DIFile(filename: "Target/zfp/src/template/decodei.c",
                 checksum: "1ae21529d348c455943de4c8f3de3641")
```

The DILocation explicitly has `line: 0` — this is LLVM's indicator for "no specific source location / compiler-synthesized instruction."

### Why Line 0

The function body is a single line (line 9): a ternary expression that calls different decode functions depending on `REVERSIBLE(zfp)`. Both branches of the ternary pass `zfp->stream`, `zfp->minbits`, `zfp->maxbits` as arguments. Under O2, LLVM **hoists** these common field accesses above the conditional branch, merging the two copies into one. Since the merged instruction no longer belongs to a unique source position, LLVM sets `DILocation(line: 0)`.

Additionally, `REVERSIBLE(zfp)` expands to `((zfp)->minexp < ZFP_MIN_EXP)` where `ZFP_MIN_EXP = -1074`. The `minexp < -1074` comparison retains `!dbg !18007` (line 9) because it is NOT shared between the two branches — it appears only in the condition.

### Inline Stack

```
decodei.c:9:28                           ← zfp_decode_block_int64_2 → rev_decode_block_int64_2
  └─ revdecode.c:41:21                   ← rev_decode_block_int64_2 → stream_read_bits
       └─ inline.c:254                   ← stream_read_bits (底层)
```

All three prologues have `line: 0` for hoisted/merged instructions — a cascading effect of O2 inlining + hoisting.

### Correct Source Location

The load instruction corresponds to the `zfp->stream` field access in line 9. Since this field access appears identically in both ternary branches, it cannot be attributed to a specific column — only to the function's sole source line (line 9).

### yapall Analysis Accuracy

yapall reports `*null` as the allocation because its k=0, flow-insensitive analysis cannot prove that `zfp->stream` is non-null. In practice, `zfp->stream` is always a valid pointer in a properly initialized `zfp_stream`. This is a pointer-analysis over-approximation, not a real program bug.

## Paper Use

- include_in_main_table: `true` — canonical example of O2 code-hoisting causing `line: 0` DWARF collapse
- include_as_failure_boundary: `false`
- caveats: `Reported line=0 is a genuine debug-info quality issue (LLVM hoisting), not a tool bug. The yapall invalid_load itself is an analysis over-approximation (*null for a struct field). Use this case to illustrate (a) O2 hoisting → line:0 collapse, (b) the cascading effect when combined with inlining, and (c) the distinction between debug-info quality issues vs pointer-analysis precision issues.`
