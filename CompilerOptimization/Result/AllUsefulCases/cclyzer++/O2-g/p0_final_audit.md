# cclyzer++ P0 Final Audit

## Scope
- tool: `cclyzer++`
- universe: `LLVM14-O2-g` / `O2-g`
- source CSV: `/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/cclyzer++/O2-g/tool_cases.csv`
- unique locations CSV: `/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/cclyzer++/O2-g/p0_unique_locations.csv`

## P0 Counts
- P0 rows: 127974
- P0 unique locations: 381
- P0 unique files: 333

## P0 Rows By Reason
| key | count |
| --- | ---: |
| `LineZero` | 127901 |
| `LineOutOfRange` | 7 |
| `ColumnOutOfRange` | 66 |

## P0 Unique Locations By Reason
| key | count |
| --- | ---: |
| `LineZero` | 332 |
| `LineOutOfRange` | 6 |
| `ColumnOutOfRange` | 43 |

## P0 Rows By Target
| key | count |
| --- | ---: |
| `flatbuffers` | 16975 |
| `libsndfile` | 7742 |
| `tengine` | 411 |
| `zopfli` | 2804 |
| `lepton` | 40025 |
| `masscan` | 13375 |
| `zfp` | 46642 |

## P0 Unique Locations By Target
| key | count |
| --- | ---: |
| `flatbuffers` | 39 |
| `libsndfile` | 83 |
| `tengine` | 35 |
| `zopfli` | 14 |
| `lepton` | 71 |
| `masscan` | 97 |
| `zfp` | 42 |

## Validation
| key | count |
| --- | ---: |
| `ok` | 381 |

## Interpretation Notes
- P0 rows are relation-level evidence rows, not independent paper cases.
- Unique locations deduplicate by `(reported_file, reported_line, reported_column, priority_reason)`.
- `LineZero` supports no valid source line / source-location loss; only rows with additional nonzero recovered IR line should be phrased as direct line mismatch.
- `ColumnOutOfRange` and `LineOutOfRange` are direct objective line/column invalidity evidence.
