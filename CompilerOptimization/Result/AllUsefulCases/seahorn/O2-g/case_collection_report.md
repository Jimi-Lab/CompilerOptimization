# SeaHorn O2-g File/Line/Column/Bitcode Block Collection Report

## Scope

- tool: `seahorn`
- universe: `O2-g` / `LLVM14-O2-g`
- selected runs: `8`
- parser source: `summary/all_cases.csv`
- collected case kind: `undefined_read_block`
- rule: collect every block with `File/Line/Column/Bitcode`, preserve duplicates and original per-run order.

## Priority Counts

| key | count |
| --- | ---: |
| `P1` | 6135 |
| `P0` | 56 |
| `P2` | 3 |

## Priority Reasons

| key | count |
| --- | ---: |
| `ValidBitcodeSourceMappingNeedsSemanticReview` | 6135 |
| `LineZero` | 56 |
| `ExternalOrUnresolvedSource` | 3 |

## Target Summary

| target | all_cases rows | blocks | P0 | P1 | P2 | invalid locations | source regions |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| flatbuffers | 3755 | 3 | 0 | 0 | 3 | valid=3 | system_header=3 |
| lepton | 35709 | 2357 | 0 | 2357 | 0 | valid=2357 | project_header=1035, project_source=1322 |
| libsndfile | 1428 | 1262 | 42 | 1220 | 0 | line_zero=42, valid=1220 | project_header=677, project_source=585 |
| masscan | 263 | 196 | 0 | 196 | 0 | valid=196 | project_source=196 |
| redis | 373 | 350 | 0 | 350 | 0 | valid=350 | project_source=86, third_party_header=262, third_party_source=2 |
| tengine | 16126 | 1074 | 11 | 1063 | 0 | line_zero=11, valid=1063 | project_header=87, project_source=538, third_party_header=449 |
| zfp | 791 | 778 | 3 | 775 | 0 | line_zero=3, valid=775 | project_source=778 |
| zopfli | 5363 | 174 | 0 | 174 | 0 | valid=174 | project_source=174 |

## Location Validity

| key | count |
| --- | ---: |
| `valid` | 6138 |
| `line_zero` | 56 |

## Source Regions

| key | count |
| --- | ---: |
| `project_source` | 3679 |
| `project_header` | 1799 |
| `third_party_header` | 711 |
| `system_header` | 3 |
| `third_party_source` | 2 |

## Output Files

- `tool_cases.csv`: all collected SeaHorn blocks classified as P0/P1/P2.
- `tool_runs.csv`: selected run manifest from `result.txt`.
- `native_output_profile.md`: notes on SeaHorn native output and block mapping.
- `collection_manifest.json`: parser statistics and selected run list.
