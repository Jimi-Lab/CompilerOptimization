# yapall Native Output Profile

## Run Selection Boundary
- run selection file: /home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/result.txt
- only the run directories listed there are included in this profile and downstream CSVs

## Native Inputs Used
- ValueCases/*_yapall_value_cases.csv
- ValueCases/raw_issues.csv and raw log paths referenced by each row
- ValueCases/ll_provenance.csv via columns copied into each row
- report/final_report.md, commands/commands.log, status/run_status.tsv as run evidence

## Native Classification Counts
- unlocatable_operand: 902700
- InlineAttributionDrift: 624599
- Useless-CodeConsistent: 585666
- WrongFunctionAttribution: 209060
- Wanted-LineColumnMissing: 97312
- missing_debug_location: 76534
- ColumnPointsToWrongToken: 29460
- tool_output_insufficient: 1728

## Normalization Policy
- Raw yapall issue rows are IR-level pointer-analysis reports, not source-level confirmed vulnerabilities.
- Source file/line/column validity is recomputed against local source files when available.
- Header locations are not automatically P0; they require objective invalidity.
- Tool-output-insufficient rows are retained as P2 unless an objective project location invalidity is present.
