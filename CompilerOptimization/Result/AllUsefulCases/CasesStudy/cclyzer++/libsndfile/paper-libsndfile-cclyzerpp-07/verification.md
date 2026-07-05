# Verification: paper-libsndfile-cclyzerpp-07

## Verdict

- label: `exact`  <!-- exact | nearby | function-only | wrong | unrecoverable -->
- verified_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/programs/common.c`
- verified_line: `193`
- verified_source_text: `binfo.coding_history_size = (uint32_t) slen ;`

## Checks

- [x] Raw artifact line/row matches `input.json`.
- [x] Reported location invalidity is independently confirmed.
- [x] IR instruction and debug metadata are located.
- [x] Recovered line is checked against the source tree.
- [x] If inline is claimed, caller/callee attribution is separated.
- [x] If evidence is insufficient, `unrecoverable` is justified rather than guessed.

## Evidence Notes

### Artifact Verification

All referenced artifacts exist and are accessible:
- `all_cases.csv` row 14161 (case_uid `015560`): matches input.json
- Snippet files (`015560.source.txt`, `015560.ir.txt`, `015560.row.txt`): present and consistent
- LLVM IR file: contains the store instruction at line 130122 with `!dbg !87358`

### Reported Location Invalidity

**Confirmed but only in the wrong file.** cclyzer++ reported `src/common.c:193:30`. In that file, line 193 is an empty line (part of the `case 'd':` formatting block in `log_putchar`), so column 30 is indeed out of range.

### Debug Metadata Trace

The debug metadata chain is fully consistent:

```
!87358 = !DILocation(line: 193, column: 30, scope: !87203, inlinedAt: !87205)
!87203 = distinct !DILexicalBlock(scope: !87199, file: !3908, line: 189, column: 3)
!87202 = !DILocalVariable(name: "slen", scope: !87203, file: !3908, line: 189, ...)
!87199 = distinct !DILexicalBlock(scope: !87200, file: !3908, line: 180, column: 8)
!87201 = distinct !DILexicalBlock(scope: !87165, file: !3908, line: 179, column: 6)
!87165 = distinct !DISubprogram(name: "merge_broadcast_info", file: !3908, line: 105, ...)
!87205 = distinct !DILocation(line: 265, column: 31, scope: !87158)   // inlinedAt site
!87158 = distinct !DILexicalBlock(scope: !87069, file: !3908, line: 265, column: 6)
!87069 = distinct !DISubprogram(name: "sfe_apply_metadata_changes", file: !3908, line: 234, ...)
!3908 = !DIFile(filename: "Target/libsndfile/programs/common.c",
                directory: "/home/jimi/PaperExperiment/CompilerOptimization", ...)
```

### Correct Location

The DIFile `!3908` specifies `programs/common.c` (not `src/common.c`). The fully resolved path is:
`/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/programs/common.c`

At line 193 of this file:
```c
binfo.coding_history_size = (uint32_t) slen ;
```

Column 30 points to the character `o` in `coding_history_size` — a valid source location within the struct member name being assigned to.

### Inlining Context

- **Inlined function**: `merge_broadcast_info` (defined at `programs/common.c:105`)
- **Call site**: `programs/common.c:265` — `if (info->has_bext_fields && merge_broadcast_info(infile, outfile, sfinfo.format, info))`
- **Inlined code**: `programs/common.c:193` — `binfo.coding_history_size = (uint32_t) slen ;`
- Both caller and callee are in the same file (`programs/common.c`), so no cross-file inlining ambiguity exists.

### Root Cause: File-Path Disambiguation Failure

cclyzer++'s source-map inventory contains 6069 entries for `src/common.c` but **zero** entries for `programs/common.c`. The tool mapped the debug reference to the only `common.c` it knew about (`src/common.c`), where line 193 happens to be empty, producing the `ColumnOutOfRange` classification.

The debug metadata itself is **correct** — both the file path and the line/column are accurate. This is a tool false positive caused by incomplete source-file discovery.

### Phi-Merge Context Assessment

The store instruction resides in basic block `%204` (one of three predecessors of block `%211`, which contains a phi node `%215 = phi i8* [...]`). The `phi_incoming_count=3` reflects the CFG merge at block `%211`. However, the debug location of this store instruction was NOT drifted by phi-node merging — it correctly points to the source assignment. The `Wanted-PhiMergeLocationDrift` flag is a consequence of the tool's phi-instr analysis pipeline, not evidence of actual debug-info corruption.

## Paper Use

- include_in_main_table: `true` — compelling example of tool false positive from file-path disambiguation failure
- include_as_failure_boundary: `false`
- caveats: `The debug metadata is correct; the location invalidity is entirely a cclyzer++ source-map resolution artifact. Use this case to discuss the importance of robust file-path resolution in static analysis tools, especially for projects with same-basename source files in different directories.`
