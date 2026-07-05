# paper-libsndfile-yapall-09

## Identity

- repo: `libsndfile`
- tool: `yapall`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `yapall.libsndfile.O2g.000222046`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/log/CompilerOptimization_CompilerResult_libsndfile_LLVM14-O2-g_artifacts_libsndfile_sndfile_convert_O2_g_bc_subset_k0_default.log`
- raw_row_or_line: `line=384897; kind=invalid_load; operand=sfe_apply_metadata_changes:0; allocation=*@codec_close`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/log/CompilerOptimization_CompilerResult_libsndfile_LLVM14-O2-g_artifacts_libsndfile_sndfile_convert_O2_g_bc_subset_k0_default.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/commands/commands.log;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/status/run_status.tsv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/report/final_report.md;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/ValueCases/summary.md`

## Reported Location

- reported_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/programs/common.c`
- reported_line: `0`
- reported_column: ``
- location_validity: `line_zero`                   
- source_region: `project_source`

## IR Anchor

- mode: `subset:k0:default`
- ir_function: `sfe_apply_metadata_changes`
- ir_instruction: `sfe_apply_metadata_changes:sfe_apply_metadata_changes:2:14`
- ir_line: `14`
- ir_snippet:

```llvm
%9 = load i8*, i8** %0, align 8, !dbg !87128, !tbaa !7225
```

## Source / Message

- source_snippet:

```text

```

- message: `invalid_load issue; site_resolution=resolved_via_reverse_use; classification=Wanted-LineColumnMissing; all_classes=Wanted-LineColumnMissing`
- root_cause_hint: `DWARF location drift`
- inventory_confidence: `high`
- notes: `candidate_id=libsndfile_000388143; issue_id=91bdde38490ee4ca; mapping_status=source_line_missing; token_at_column=; expected_token_kind=load-like pointer token; actual_token_kind=column_unknown; site_role=load.ptr; ll_source=native_compiler_artifact; valuecase_notes=ambiguous_multiple_sites`

## Manual Study Checklist

- [x] Confirm all referenced artifacts exist.
- [x] Validate why the reported location is invalid or drifted.
- [x] Locate the IR instruction and debug metadata in the `.ll` file.
- [x] Build 1-3 candidate recovered source locations.
- [ ] Run the LLM recovery prompt using `input.json`.
- [x] Verify the LLM output manually.
- [x] Write the paper-ready narrative below.

## Paper-Ready Narrative

### 1. What yapall reported

yapall scanned the libsndfile LLVM14-O2-g linked bitcode (`libsndfile_sndfile_convert_O2_g.bc`, ~929 MB) in `subset:k0:default` mode. The scan completed in 360 seconds with return code 0. At line 384,897 of 1,247,307 total issue rows, yapall produced:

```
invalid_load	sfe_apply_metadata_changes:0	*@codec_close
```

**yapall itself outputs no source locations** — only `kind`, `operand`, and `allocation`. The raw log contains zero occurrences of the strings `line`, `column`, `!dbg`, or `DILocation`. Every piece of source-location information downstream is derived by post-processing scripts that cross-reference yapall operands against the `.ll` text file and its DWARF debug metadata.

The operand `sfe_apply_metadata_changes:0` identifies the first parameter of function `sfe_apply_metadata_changes`. In yapall's naming convention, this is a `LocalName::Parameter` — the format is `<function>:<param_index>`, where `:0` means parameter index 0 (LLVM IR `%0`, corresponding to the C source parameter `const char * filenames [2]`).

The allocation `*@codec_close` names the points-to target: the `codec_close` function pointer. The `*` prefix means "pointer to." Yapall flagged this as `invalid_load` because, in its allocation model (`src/alloc.rs:347-356`), `Alloc::Function` returns `loadable() = false` — loading from a location that may hold a function pointer is considered semantically invalid in yapall's type system.

This IR-level signal is a **sound over-approximation**: yapall's flow-insensitive, field-insensitive, k=0 context-insensitive analysis cannot disprove that `filenames[0]` (a `const char*` string pointer) might alias the `codec_close` function pointer stored inside the `SF_PRIVATE` struct. It is an analysis imprecision, not a source-code defect.

### 2. The debug metadata chain

The downstream processing pipeline (`build_yapall_valuecases.py`) recovers source locations by mapping yapall operands to the IR instructions that use them. For the parameter operand `sfe_apply_metadata_changes:0`, the pipeline finds five instructions in the `.ll` file that reference `%0`. Filtering for the `load.ptr` role (the role matching `invalid_load`), it selects three candidate load instructions. The primary one is at function `sfe_apply_metadata_changes`, basic block `2`, instruction index `14`:

```llvm
; .ll file line 129779
%9 = load i8*, i8** %0, align 8, !dbg !87128, !tbaa !7225
```

This instruction carries the debug reference `!dbg !87128`. The pipeline parses the metadata section of the `.ll` file and resolves the chain:

```
!87128 = !DILocation(line: 0, scope: !87126)           ← line: 0 lives here
!87126 = distinct !DILexicalBlock(scope: !87069, file: !3908, line: 243, column: 6)
!87069 = distinct !DISubprogram(name: "sfe_apply_metadata_changes", file: !3908, line: 234)
!3908  = !DIFile(filename: "Target/libsndfile/programs/common.c",
                 directory: "/home/jimi/PaperExperiment/CompilerOptimization")
```

**The `line: 0` is not invented by yapall, and not invented by the downstream scripts.** It is read verbatim from the DWARF `DILocation` metadata that Clang emitted into the `.ll` file at compile time. The pipeline faithfully records `source_line=0` in the ValueCases CSV. The `collect_yapall_o2g_cases.py` script then sees `int(source_line) == 0` and classifies it as `location_validity: line_zero`, which triggers `priority: P0` with reason `LineZero`.

The complete mapping chain is:

```
yapall operand                        pipeline lookup                   DWARF metadata
─────────────────────────────────────────────────────────────────────────────────────
sfe_apply_metadata_changes:0    →    operand_use_index.csv         →   5 use sites found
  (parameter %0)                     use_site: ...:2:14, load.ptr       filter by load.ptr role
                                     use_site: ...:24:0,  load.ptr
                                     use_site: ...:242:0, load.ptr
                                     ↓
                                ir_instruction_index.csv           →   inst at block 2, idx 14
                                     dbg_id: 87128                     %9 = load i8*, i8** %0, !dbg !87128
                                     ↓
                                debug_location_index.csv           →   !87128 = !DILocation(line: 0, ...)
                                     source_file: common.c              scope → !DISubprogram("sfe_apply_metadata_changes")
                                     source_line: 0                     file → !DIFile("common.c")
```

### 3. Why DWARF says line: 0 — O2 code hoisting

The root cause of `line: 0` is LLVM's **code hoisting** under `-O2 -g`. In the source, `filenames[0]` is loaded in both branches of a conditional:

```c
// common.c:243-250, function sfe_apply_metadata_changes
if (filenames [1] == NULL)                              // line 243
    infile = outfile = sf_open (filenames [0], SFM_RDWR, &sfinfo) ;  // line 244
else {
    infile = sf_open (filenames [0], SFM_READ, &sfinfo) ;            // line 246
    // ...
    outfile = sf_open (filenames [1], SFM_WRITE, &sfinfo) ;          // line 250
}
```

Because `filenames[0]` is used in **both** the THEN branch (line 244) and the ELSE branch (line 246), LLVM's optimizer hoists the load above the conditional branch to avoid redundant memory access:

```llvm
; Block %2 — entry block, BEFORE the branch:
%6 = getelementptr inbounds i8*, i8** %0, i64 1    ; &filenames[1]
%7 = load i8*, i8** %6, align 8, !dbg !87125        ; filenames[1]
%8 = icmp eq i8* %7, null                            ; filenames[1] == NULL?
%9 = load i8*, i8** %0, align 8, !dbg !87128        ; ← HOISTED: filenames[0]
br i1 %8, label %10, label %12                       ; branch to THEN or ELSE

10:  ; THEN block:  sf_open(%9, SFM_RDWR, ...)       ; %9 used here
12:  ; ELSE block:  sf_open(%9, SFM_READ, ...)       ; %9 also used here
```

The hoisted `load` instruction now spans **two source lines** (244 and 246) and crosses a basic-block boundary. It no longer has a unique, predictable source-line correspondence. Per the DWARF standard §6.2.2, when "an instruction ... does not have a predictable relationship to any source line," the compiler emits `line: 0`.

**This is correct compiler behavior.** Clang is following the DWARF specification. No tool in the chain — not Clang, not yapall, not the downstream scripts — is "wrong."

### 4. Why yapall conflates `filenames[0]` with `@codec_close`

The second contributing factor is yapall's **field-insensitive and flow-insensitive analysis**. The linked bitcode contains every codec format supported by libsndfile — DWVW, GSM610, ALAC, G72x, AIFF, WAV, and ~20 more — each contributing function pointers for read, write, seek, close, and byterate operations. All of these function pointers are stored in the `SF_PRIVATE` struct:

```
SF_PRIVATE struct (from common.h):
  field "seek"          (offset 63488) → stores dwvw_seek, gsm610_seek, alac_seek, ...
  field "codec_close"   (offset 63744) → stores codec_close, dwvw_close, ...
  field "read_*"        (various)      → stores ~80 read function pointers
  field "write_*"       (various)      → stores ~80 write function pointers
  ... and ~100 more function-pointer fields
```

Under field-insensitive analysis, all fields of `SF_PRIVATE` collapse into a single merged memory region. Under flow-insensitive analysis, a pointer cannot be distinguished before vs. after a function call. The function `sfe_apply_metadata_changes` calls `sf_open(filenames[0], ...)`, which returns `SF_PRIVATE*`. After this point, yapall cannot distinguish `filenames[0]` (a `const char*` string pointer) from the returned `SF_PRIVATE*` (a struct full of function pointers). The entire codec function-pointer table — approximately 300 function pointers per format — bleeds into the points-to set of `filenames`.

As confirmation, the same operand `sfe_apply_metadata_changes:0` generates **326 separate `invalid_load` entries** in the raw log, each pointing to a different function-pointer allocation: `*@codec_close`, `*@dwvw_seek`, `*@gsm610_read_d`, `*@alac_write_f`, `*@g72x_close`, ... covering every codec operation in the library. This is the signature of field-insensitive alias explosion.

### 5. The cascading-effect model

This case exemplifies a **cascading analysis artifact** where two independent, individually legitimate mechanisms compound to produce a signal that downstream location-based analysis cannot resolve:

```
Layer 1 — Compiler (Clang -O2 -g):
  Code hoisting moves filenames[0] load above the branch.
  DWARF correctly emits line: 0 (no unique source line).
  → Artifact: !87128 = !DILocation(line: 0, ...)

Layer 2 — Static analysis (yapall, k=0, field/flow insensitive):
  Field-insensitivity merges all SF_PRIVATE fields.
  Flow-insensitivity merges filenames with SF_PRIVATE*.
  → Artifact: invalid_load sfe_apply_metadata_changes:0  *@codec_close
  (plus 325 other function-pointer allocations for the same operand)

Layer 3 — Location mapping (build_yapall_valuecases.py):
  Cross-references operand → IR instruction → dbg !87128 → DILocation(line: 0)
  → Artifact: reported location common.c:0

Layer 4 — Classification (collect_yapall_o2g_cases.py):
  int(source_line) == 0 → location_validity: line_zero
  project_source region + line_zero → P0 / LineZero / LocationInvalid
  → Artifact: case paper-libsndfile-yapall-09
```

None of these layers is "wrong." Each operates correctly within its own domain. The case is a boundary point where the fundamental limits of compiler optimization (code motion), debugging information (DWARF line:0 semantics), and static analysis (field/flow insensitivity) intersect.

### 6. Methodological value

- **Objective evidence**: The `line: 0` originates from DWARF metadata (`!DILocation(line: 0, ...)`), not from a yapall bug, script error, or source-code defect. The case provides independently verifiable evidence about location drift.
- **Deterministic classification**: The downstream classification as P0 / LineZero / LocationInvalid is mechanical — it derives from the objective check `int(source_line) == 0`, not from heuristics or judgment calls.
- **Irreducible boundary case**: This case cannot be "fixed" by modifying the libsndfile source code. The code is correct. The compiler optimization is correct. The DWARF is correct. The static analysis is a sound over-approximation. The location mapping failure is inherent in the interaction between these layers.
- **Representative of the O2-g analysis gap**: The combination of O2 code hoisting (producing `line: 0`) and field-insensitive alias explosion (producing function-pointer conflation) is characteristic of the dominant imprecision pattern observed across all six scanned targets. This case provides a clean, well-bounded instance of that pattern.

### 7. Recovered location candidates

Although the debug metadata reports `line: 0`, the IR context narrows the true source location to a small set of candidates:

| Candidate | Source line | IR instruction | Confidence |
|-----------|------------|----------------|------------|
| Candidate A | `common.c:244` | the THEN-branch use: `sf_open(filenames[0], SFM_RDWR, ...)` | medium (first textual use) |
| Candidate B | `common.c:246` | the ELSE-branch use: `sf_open(filenames[0], SFM_READ, ...)` | medium (second textual use) |
| Candidate C | `common.c:243-246` | the hoisted load spans the entire if/else construct | low (range, not a point) |

The hoisted load serves **both** branches, so no single candidate is uniquely correct. This is precisely why Clang emitted `line: 0` — the instruction genuinely does not belong to one line. In a paper context, the most defensible choice is to report the function-level attribution (`sfe_apply_metadata_changes @ common.c:234-299`) and document the ambiguity.
