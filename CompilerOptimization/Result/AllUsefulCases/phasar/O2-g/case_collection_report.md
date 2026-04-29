# Phasar O2-g Useful Cases Collection Report

## Scope

- tool: `phasar`
- universe: `O2-g`
- mode: `ifds-uninit`
- selected reports: `8`
- parser source: re-parsed `psr-report.txt`; did not trust stale `target_linecheck.csv` blindly.

## Priority Counts

| target | parsed uses | P0 | P1 | P2 | valid/non-useful | status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| curl | 145 | 0 | 0 | 0 | 145 | ok |
| lepton | 935 | 0 | 0 | 257 | 678 | ok |
| libsndfile | 565 | 3 | 0 | 0 | 562 | ok |
| masscan | 599 | 3 | 0 | 1 | 595 | ok |
| redis | 26170 | 258 | 0 | 12 | 25900 | ok |
| tengine | 672 | 0 | 0 | 0 | 672 | ok |
| zfp | 786 | 90 | 0 | 0 | 696 | ok |
| zopfli | 71 | 0 | 0 | 0 | 71 | ok |

## Priority Reasons

| reason | count |
| --- | ---: |
| ExternalOrUnresolvedSource | 257 |
| ExternalSourceLineOutOfRange | 13 |
| LineOutOfRange | 208 |
| SourceLineEmptyOrNonCode | 22 |
| SourceTextMismatch | 124 |

## Output Files

- `tool_cases.csv`: useful P0/P1/P2 cases only.
- `tool_runs.csv`: selected report/run manifest.
- `native_output_profile.md`: Phasar output format notes.
- `collection_manifest.json`: parser statistics and input reports.
