# paper-zfp-seahorn-13

## Identity

- repo: `zfp`
- tool: `seahorn`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `seahorn.zfp.O2g.000001`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/log/sea.smc.instrument.stderr.log`
- raw_row_or_line: `6`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/summary/all_cases.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/log/sea.smc.instrument.stderr.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/log/commands.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/seahorn/seahorn-O2-g/result/run_20260322_223731_fixed_fullmatrix/report/final_report.md`

## Reported Location

- reported_file: `Target/zfp/include/zfp/bitstream.inl`
- reported_line: `0`
- reported_column: `0`
- location_validity: `line_zero`
- source_region: `project_source`

## IR Anchor

- mode: `smc_instrument`
- ir_function: `stream_copy` (with inlined `stream_read_bits`)
- ir_instruction: `%31 = phi i64 [ %22, %25 ], [ %22, %24 ], [ poison, %28 ], !dbg !4775`
- ir_line: `CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.ll:8405`
- ir_snippet:

```llvm
%31 = phi i64 [ %22, %25 ], [ %22, %24 ], [ poison, %28 ], !dbg !4775
```

- normalized_input_ir_snippet:

```llvm
; Block %12: outer loop header of stream_copy (line 415)
  %14 = load i64, i64* %7, align 8           ; load s->bits
  %15 = icmp ult i64 %14, 64                  ; s->bits < 64 ?
  br i1 %15, label %16, label %28             ; if not, skip to %28

; Block %16: read word, merge into value (lines 259-263)
  %20 = load i64, i64* %18                    ; stream_read_word(s)
  %21 = shl i64 %20, %14                      ; word << s->bits
  %22 = add i64 %21, %17                      ; value += word << s->bits

; Block %24: s->bits == 0 after subtraction (line 269)
  store i64 0, i64* %6                        ; s->buffer = 0
  br label %30

; Block %25: s->bits != 0 after subtraction (lines 273-275)
  %26 = sub nuw nsw i64 64, %14
  %27 = lshr i64 %20, %26                     ; buffer >>= wsize - s->bits
  store i64 %27, i64* %6
  br label %30

; Block %28: s->bits >= 64 — DEAD CODE (line 278-283)
  %29 = add i64 %14, -64                       ; just decrement bit count
  store i64 %29, i64* %7
  br label %30

; Block %30: merge point
  %31 = phi i64 [ %22, %25 ], [ %22, %24 ], [ poison, %28 ]
  ; value returned by stream_read_bits, then fed to stream_write_bits
```

- debug_metadata:

```llvm
!4775 = !DILocation(line: 0, scope: !4438, inlinedAt: !4757)
!4438 = distinct !DILexicalBlock(scope: !4428, file: !114, line: 257, column: 7)
!4428 = distinct !DILexicalBlock(scope: !4421, file: !114, line: 257, column: 7)
!4421 = distinct !DISubprogram(name: "stream_read_bits", file: !114, line: 253, ...)
!4757 = distinct !DILocation(line: 416, column: 40, scope: !4749)
!4749 = distinct !DILexicalBlock(scope: !4741, file: !114, line: 415, column: 21)
!4741 = distinct !DISubprogram(name: "stream_copy", file: !114, line: 413, ...)
!114 = !DIFile(filename: "Target/zfp/include/zfp/bitstream.inl", ...)
```

## Source / Message

- source_snippet:

```text
bitstream.inl:253-285 — stream_read_bits (inlined into stream_copy at line 416)

inline_ uint64
stream_read_bits(bitstream* s, bitstream_count n)
{
  uint64 value = s->buffer;                        // line 256
  if (s->bits < n) {                               // line 257 ← !4438 scope
    /* keep fetching wsize bits until enough bits are buffered */
    do {
      s->buffer = stream_read_word(s);             // line 261
      value += (uint64)s->buffer << s->bits;       // line 262
      s->bits += wsize;                            // line 263
    } while (sizeof(s->buffer) < sizeof(value) && s->bits < n);
    s->bits -= n;                                  // line 266
    if (!s->bits) {                                // line 267
      s->buffer = 0;                               // line 269 → block %24
    }
    else {
      s->buffer >>= wsize - s->bits;               // line 273 → block %25
      value &= ((uint64)2 << (n - 1)) - 1;         // line 275
    }
  }
  else {                                           // line 278 → block %28 (DEAD when n=64)
    s->bits -= n;                                  // line 280
    s->buffer >>= n;                               // line 281
    value &= ((uint64)1 << n) - 1;                 // line 282 ← UB when n=64!
  }
  return value;                                    // line 284
}

bitstream.inl:412-424 — stream_copy (calling context)

inline_ void
stream_copy(bitstream* dst, bitstream* src, bitstream_size n)
{
  while (n > wsize) {                              // line 415
    bitstream_word w = (bitstream_word)stream_read_bits(src, wsize);  // line 416 ← !4757
    stream_write_bits(dst, w, wsize);              // line 417
    n -= wsize;                                    // line 418
  }
  ...
}
```

- message: `Possible read of undefined value at`
- root_cause_hint: `DCE/UB-based dead-code elimination → poison in phi node + multi-inline debug-location collapse to line 0`
- inventory_confidence: `0.95`
- notes: `all_cases_case_id=6;all_cases_step=09;all_cases_name=smc_instrument;collected_from=all_cases.undefined_read_block;resolved_source=/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/include/zfp/bitstream.inl; zfp has only 3 line-zero cases total (vs 42 in libsndfile); this is the only phi-node-poison case among them; the others are insertelement/shufflevector poison; this case represents the "Vanishing Node" pathology from the taxonomy — UB-based DCE eliminates a code path and replaces the phi incoming value with poison`

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
`Target/zfp/include/zfp/bitstream.inl:0:0` for an O2-g phi instruction:
`%31 = phi i64 [ %22, %25 ], [ %22, %24 ], [ poison, %28 ]`. The reported
source location is invalid (line 0). In the normalized LLVM14 O2-g `.ll`,
the instruction appears at line 8405 inside `stream_copy` and is annotated
with `!4775 = !DILocation(line: 0, scope: !4438, inlinedAt: !4757)`.
The scope `!4438` is a lexical block inside `stream_read_bits` at
`bitstream.inl:257`, and the inlined-at location `!4757` points to
`bitstream.inl:416`, the call site inside `stream_copy`.

### Root Cause: UB-Based Dead Code Elimination Creates Poison

The phi node merges the return value of `stream_read_bits` from three
control-flow paths inside the `if (s->bits < n)` branch at line 257:

| Block | Condition | Value | Status |
|-------|-----------|-------|--------|
| `%24` | `s->bits == 0` after subtract | `%22` (= value) | Live |
| `%25` | `s->bits != 0` after subtract | `%22` (= value) | Live |
| `%28` | `s->bits >= 64` (the `else` branch) | `poison` | **Dead** |

The critical mechanism: `stream_copy` (line 416) calls
`stream_read_bits(src, wsize)` where `wsize = 64` (constant, from
`#define wsize ((bitstream_count)(sizeof(bitstream_word) * CHAR_BIT))`
with `bitstream_word = uint64`). With `n = 64` constant-folded by the
inliner, the `else` branch at line 278 (`s->bits >= 64`) is
**provably unreachable**: the bitstream invariant guarantees
`s->bits < wsize = 64` at all times, so `s->bits >= 64` can never be true.

Furthermore, the C code inside the else branch contains
`value &= ((uint64)1 << n) - 1` (line 282). When `n = 64`, the shift
`(uint64)1 << 64` is **undefined behavior** in C (shift by type width).
This gives the compiler a second, independent reason to eliminate the path.

O2's Dead Code Elimination (DCE) recognizes the else branch as dead and
marks the corresponding phi incoming edge as `poison` — the compiler's
way of saying "this edge is never taken, I don't need to provide a real
value." The `poison` is never actually read at runtime because the
control-flow edge from block `%28` can never be traversed.

### Why Line 0?

Two levels of inlining (`stream_read_bits` → `stream_copy` → caller) plus
DCE on the dead path caused the compiler to lose precise line mapping for
this phi instruction. The scope correctly identifies the code as belonging
to `stream_read_bits` (bitstream.inl:257), but the line number collapsed
to 0.

### SeaHorn's Blind Spot

SeaHorn's `CanReadUndef` pass (source: `CanReadUndef.cc:98-106`) iterates
over all phi nodes and checks each incoming value. It finds `poison` from
block `%28` and flags it as "possible read of undefined value." SeaHorn
has no concept of **path feasibility** — it does not analyze whether the
poison-carrying edge can actually be taken at runtime. It trusts that if
`poison` appears as a phi incoming value, it represents a real risk.

### Recovered Source Locations

1. **`bitstream.inl:257`** — the `if (s->bits < n)` branch point inside
   `stream_read_bits`, where the phi's scope `!4438` originates
2. **`bitstream.inl:416`** — the call site `stream_read_bits(src, wsize)`
   inside `stream_copy`, where the inlining happened
3. **`bitstream.inl:282`** — the UB-triggering line
   `value &= ((uint64)1 << n) - 1` in the dead else branch

### Paper Taxonomy Fit

This case maps to **two** feature labels from the taxonomy simultaneously:

1. **靶点消失 (Vanishing Node)** — DCE eliminates a code path based on UB
   assumptions, replacing real values with `poison` in the IR
2. **时空错乱 (Trace-loss)** — multi-level inlining collapses the debug
   location to `line: 0`, rendering the reported location useless

Unlike the SSE vectorization cases (case-03 and case-04 from libsndfile),
where the FP mechanism is "vector poison that SSE ISA considers benign,"
this case demonstrates a fundamentally different pathology: **UB-driven
dead code elimination creating phantom phi edges**. The compiler uses UB
semantics to prove a path dead, then marks the surviving IR with `poison`
— and the static analyzer cannot distinguish compiler-introduced poison
from genuine uninitialized variables.

### Statistical Context

zfp has only 3 line-zero cases total (vs. 42 in libsndfile), and this is
the **only phi-node-poison case** among them. The other two are
`insertelement`/`shufflevector` vectorization artifacts. This case is the
sole representative of the "Vanishing Node + Trace-loss" compound
pathology in the zfp dataset, making it a high-value golden case.

The O2-g compilation evidence is valid: the recorded compile command uses
`clang-14 -O2 -g` with no `-DNDEBUG`. No local SeaHorn O0 or O2-noinline
run directory exists for this target, so inline-specific attribution
relies on the metadata chain alone (`!4757` inlinedAt `bitstream.inl:416`).
