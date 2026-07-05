# paper-libsndfile-seahorn-04

## Identity

- repo: `libsndfile`
- tool: `seahorn`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `seahorn.libsndfile.O2g.000119`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/log/sea.smc.instrument.stderr.log`
- raw_row_or_line: `124`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/summary/all_cases.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/log/sea.smc.instrument.stderr.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/log/commands.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/report/final_report.md`

## Reported Location

- reported_file: `Target/libsndfile/src/alaw.c`
- reported_line: `0`
- reported_column: `0`
- location_validity: `line_zero`
- source_region: `project_source`

## IR Anchor

- mode: `smc_instrument`
- ir_function: `alaw_write_f2alaw`
- ir_instruction: `%29 = insertelement <4 x float> poison, float %28, i64 0, !dbg !19110`
- ir_line: `CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.ll:24015`
- ir_snippet:

```llvm
%28 = fmul float %9, %26, !dbg !19110
%29 = insertelement <4 x float> poison, float %28, i64 0, !dbg !19110
%30 = call i32 @llvm.x86.sse.cvtss2si(<4 x float> %29) #48, !dbg !19110
```

- normalized_input_ir_snippet:

```llvm
%25 = getelementptr inbounds float, float* %19, i64 %24, !dbg !19106
%26 = load float, float* %25, align 4, !dbg !19106, !tbaa !9054
%27 = fcmp ult float %26, 0.000000e+00, !dbg !19109
%28 = fmul float %9, %26, !dbg !19110
%29 = insertelement <4 x float> poison, float %28, i64 0, !dbg !19110
%30 = call i32 @llvm.x86.sse.cvtss2si(<4 x float> %29) #48, !dbg !19110
```

- debug_metadata:

```llvm
!19110 = !DILocation(line: 0, scope: !19107, inlinedAt: !19101)
!19107 = distinct !DILexicalBlock(scope: !19108, file: !947, line: 342, column: 8)
!19108 = distinct !DILexicalBlock(scope: !19104, file: !947, line: 342, column: 2)
!19101 = distinct !DILocation(line: 518, column: 3, scope: !19088)
!947 = !DIFile(filename: "Target/libsndfile/src/alaw.c", ...)
```

## Source / Message

- source_snippet:

```text
alaw.c:339-347 — f2alaw_array (inlined into alaw_write_f2alaw at line 518)

static inline void
f2alaw_array (const float *ptr, int count, unsigned char *buffer, float normfact)
{	for (int i = 0 ; i < count ; i++)
    {	if (ptr [i] >= 0)
            buffer [i] = alaw_encode [psf_lrintf (normfact * ptr [i])] ;   // ← line 343
        else
            buffer [i] = 0x7F & alaw_encode [- psf_lrintf (normfact * ptr [i])] ; // ← line 345
        } ;
} /* f2alaw_array */

common.h:964-971 — psf_lrintf (also inlined)

static inline int psf_lrintf (float x)
{
    #ifdef USE_SSE2
        return _mm_cvtss_si32 (_mm_load_ss (&x)) ;   // ← line 967, SSE2 intrinsic
    #else
        return lrintf (x) ;
    #endif
} /* psf_lrintf */
```

- message: `Possible read of undefined value at`
- root_cause_hint: `SSE2 intrinsic _mm_load_ss → insertelement poison + triple-inline debug-location collapse to line 0`
- inventory_confidence: `0.95`
- notes: `all_cases_case_id=124;all_cases_step=06;all_cases_name=smc_instrument;collected_from=all_cases.undefined_read_block;resolved_source=/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/alaw.c; The same insertelement pattern also appears in ulaw_write_f2alaw (ulaw.c, !dbg !18183, line 23019) — both are instances of the SSE2 psf_lrintf inline chain; SeaHorn log reports the instruction under both ulaw.c (line 638) and alaw.c (line 648) due to shared inline function expanded in two compilation units`

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
`Target/libsndfile/src/alaw.c:0:0` for an O2-g bitcode instruction:
`%29 = insertelement <4 x float> poison, float %28, i64 0`. The reported
source location is invalid (line 0). In the normalized LLVM14 O2-g `.ll`,
the instruction appears at line 24015 inside `alaw_write_f2alaw` and is
annotated with `!19110 = !DILocation(line: 0, scope: !19107, inlinedAt: !19101)`.
The scope `!19107` is a lexical block inside `f2alaw_array` at `alaw.c:342`,
and the inlined-at location `!19101` points to `alaw.c:518`, the call site
in `alaw_write_f2alaw`.

The instruction belongs to a triple-inlined SSE2 float-to-int conversion chain:

```
alaw_write_f2alaw (alaw.c:505)
  → f2alaw_array (alaw.c:339, inlined at line 518)
    → psf_lrintf (common.h:964, inlined at line 343/345)
      → _mm_load_ss / _mm_cvtss_si32 (SSE2 intrinsic, common.h:967)
```

The `insertelement <4 x float> poison, float %28, i64 0` is the compiler's
lowering of `_mm_load_ss(&x)` — it inserts a single float `%28` (which is
`normfact * ptr[i]`) into element 0 of a `<4 x float>` vector, leaving
elements 1–3 as `poison`. The subsequent `llvm.x86.sse.cvtss2si` intrinsic
only reads element 0 by SSE ISA definition — the `poison` in elements 1–3
is never accessed and is explicitly "don't care" in x86 SSE semantics.

SeaHorn's abstract interpreter does not model the SSE ISA partial-register
semantics. It sees `poison` in the vector and flags it as a potential
undefined-value read, producing a false positive. Three levels of function
inlining (`f2alaw_array` → `psf_lrintf` → SSE intrinsic) caused the
innermost debug location to collapse to `line: 0`, rendering the reported
source location completely unusable (line-zero drift).

The best recovered source locations are:

1. `alaw.c:343` — `buffer[i] = alaw_encode[psf_lrintf(normfact * ptr[i])]`
   (the positive-value branch where `_mm_cvtss_si32` executes)
2. `common.h:967` — `return _mm_cvtss_si32(_mm_load_ss(&x))`
   (the SSE2 intrinsic itself)
3. `alaw.c:345` — the negative-value branch equivalent

This is a compound artifact: **SSE2 `poison` semantics (FP trigger)** +
**triple-inline debug collapse (location drift)**. The case should be
classified as `FP-LocationDrift` / SSE poison false positive, not as a
trustworthy undefined-read location.

The O2-g compilation evidence is valid: the recorded compile command for
`alaw.c` is `clang-14 -O2 -g -std=gnu99` with `-DUSE_SSE2`, and no
`-DNDEBUG`. The same pattern exists in the sibling function
`ulaw_write_f2alaw` (ulaw.c, IR line 23019, `!dbg !18183`), providing
cross-file replication of the same SSE inline pathology. No local SeaHorn
O0 or O2-noinline run directory exists for this target, so inline-specific
attribution relies on the metadata chain alone.
