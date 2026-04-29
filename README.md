# CompilerOptimization

This repository contains experiment artifacts for a systems-security study on
how optimized debug LLVM bitcode changes what IR-level analyzers can observe.

The core setting is:

- target conference direction: ASPLOS-style systems/security paper;
- bitcode focus: `clang -O2 -g` optimized LLVM IR with debug information;
- main question: how optimization passes such as inline, mem2reg, SROA, GVN,
  DCE, and CFG simplification affect static-analysis and verification evidence;
- main tools in this repository: Phasar, SeaHorn, dg, cclyzer++, and yapall.

## Result Summary

The current useful-case summary is:

| repo | Phasar uninit | SeaHorn | dg | cclyzer++ | yapall |
| --- | ---: | ---: | ---: | ---: | ---: |
| flatbuffers | - | `0_P0` | `65_P0` | `39_P0` | - |
| lepton | `257_P2` | `0_P0` | `124_P0 + 152_P1` | - | `81_P0` |
| curl | `null` | - | - | - | - |
| libsndfile | `3_P0` | `42_P0` | `10_P0 + 14_P1` | `83_P0` | `96_P0` |
| masscan | `3_P0 + 1_P2` | `0_P0` | `7_P0 + 266_P1` | - | `115_P0` |
| redis | `258_P0 + 12_P2` | `0_P0` | `55_P0 + 122_P1` | - | - |
| tengine | `null` | `11_P0` | `9_P0 + 64_P1` | `35_P0` | `3_P0` |
| zfp | `90_P0` | `3_P0` | `12_P0` | - | - |
| zopfli | `null` | `0_L0` | `13_P0` | `14_P0` | `3_P0` |
| total | `354_P0` | `56_P0` | `295_P0` | `171_P0` | `298_P0` |

Interpretation:

- `P0`: strongest objective evidence, usually invalid source/debug location or
  high-confidence useful case.
- `P1`: strong candidate requiring semantic/manual inspection.
- `P2`: weak, degraded, unresolved, or appendix-scale evidence.
- `null` means the run did not produce a useful normalized result for that cell.
- `-` means not selected, unavailable, or intentionally excluded from the final
  useful-case matrix.

The detailed evidence lives under
`CompilerOptimization/Result/AllUsefulCases/`.

## Repository Map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Workspace rules: research scope, evidence labels, compile universes, and editing constraints. |
| `Paper/`, `paper.md`, `experiment.md` | Paper notes and experiment narrative. |
| `CompilerOptimization/TARGETS_MANIFEST.md` | Target project names, upstream URLs, and commits when available. |
| `CompilerOptimization/Target/` | Local target source checkouts. These are intentionally not vendored in this Git repository. |
| `CompilerOptimization/CompilerResult/` | Selected compiler artifacts and rebuild scripts for important targets. |
| `CompilerOptimization/Result/` | Analyzer outputs, normalized summaries, useful-case reports, and collection scripts. |
| `CompilerOptimization/Result/AllUsefulCases/` | Final curated useful-case matrix evidence. Start here for results. |
| `CompilerOptimization/Tools/` | Local analyzer wrappers, Dockerfiles, build notes, and tool patches. |
| `GITHUB_ARCHIVE_POLICY.md` | What is tracked in GitHub, what is stored externally, and why. |

## Key Evidence Files

Useful-case reports:

- `CompilerOptimization/Result/AllUsefulCases/useful_cases_matrix_plan.md`
- `CompilerOptimization/Result/AllUsefulCases/phasar/O2-g/case_collection_report.md`
- `CompilerOptimization/Result/AllUsefulCases/seahorn/O2-g/case_collection_report.md`
- `CompilerOptimization/Result/AllUsefulCases/dg/O2-g/case_collection_report.md`
- `CompilerOptimization/Result/AllUsefulCases/cclyzer++/O2-g/case_collection_report.md`
- `CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/case_collection_report.md`

Per-tool manifests:

- `CompilerOptimization/Result/AllUsefulCases/*/O2-g/collection_manifest.json`
- `CompilerOptimization/Result/AllUsefulCases/*/O2-g/tool_runs.csv`
- `CompilerOptimization/Result/AllUsefulCases/*/result.txt`

Large rebuilt tables:

- `CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/tool_cases.csv`
- `CompilerOptimization/Result/AllUsefulCases/dg/O2-g/tool_cases.csv`

The two files above are intentionally omitted from normal Git tracking because
they are multi-GB generated CSVs. Their rebuild instructions are tracked:

- `CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/REBUILD_tool_cases.md`
- `CompilerOptimization/Result/AllUsefulCases/dg/O2-g/REBUILD_tool_cases.md`

## Rebuild Commands

The final useful-case tables are normalized from existing analyzer runs. These
commands do not rerun the analyzers; they rebuild the standardized CSVs and
reports from preserved raw run artifacts.

```bash
cd /home/jimi/PaperExperiment

bash CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/scripts/rebuild_tool_cases.sh
bash CompilerOptimization/Result/AllUsefulCases/dg/O2-g/scripts/rebuild_tool_cases.sh
```

For compiler artifacts, see the target-specific rebuild scripts under:

- `CompilerOptimization/CompilerResult/flatbuffers/`
- `CompilerOptimization/CompilerResult/lepton/`
- `CompilerOptimization/CompilerResult/libsndfile/`
- `CompilerOptimization/CompilerResult/masscan/`
- `CompilerOptimization/CompilerResult/redis/`
- `CompilerOptimization/CompilerResult/tengine/`
- `CompilerOptimization/CompilerResult/zfp/`
- `CompilerOptimization/CompilerResult/zopfli/`

## Compile Universes

The paper's main compile universes are:

- `O0`: `clang -O0 -g`
- `O2`: `clang -O2 -g`
- `O2-noinline`: `clang -O2 -g -fno-inline`

Do not treat CMake `RelWithDebInfo` as equivalent to the paper `O2` universe
unless the actual compile commands or logs confirm the flags.

## Large Files And LFS

This repository uses Git LFS for selected large evidence files. After cloning:

```bash
git lfs install
git lfs pull
```

Some raw artifacts and multi-GB generated CSVs are intentionally not committed
to normal Git. They should be preserved in external snapshots with checksums.
See `GITHUB_ARCHIVE_POLICY.md` for the archive boundary.

## Notes For Readers

- Counts in the summary table are evidence counts, not automatically unique
  vulnerabilities.
- The strongest cases are labeled `P0`, but paper claims should still cite the
  corresponding report, manifest, raw artifact path, and source/IR snippets.
- Analyzer failures, timeouts, translation failures, and missing evidence are
  part of the result, not just noise.
- The repository is organized to make the experiment auditable first, and
  compact second.
