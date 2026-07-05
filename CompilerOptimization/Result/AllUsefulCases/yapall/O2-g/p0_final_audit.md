# yapall P0 Final Audit

## Scope
- tool: yapall
- universe: LLVM14-O2-g / O2-g only
- source CSV: /home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/tool_cases.csv
- unique locations CSV: /home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/p0_unique_locations.csv

## P0 Counts
- P0 rows: 69634
- P0 unique locations: 302
- P0 unique files: 302

## P0 Rows By Reason
- LineZero: 69634

## P0 Unique Locations By Reason
- LineZero: 302

## P0 Rows By Target
- lepton: 28424
- masscan: 24537
- libsndfile: 16435
- zfp: 108
- tengine: 103
- zopfli: 27

## P0 Unique Locations By Target
- masscan: 115
- libsndfile: 96
- lepton: 81
- zfp: 4
- zopfli: 3
- tengine: 3

## Validation
- ok: 302

## Interpretation Notes
- P0 rows are relation/use-site evidence rows, not independent paper cases.
- Unique locations deduplicate by reported_file, reported_line, reported_column, and priority_reason.
- LineZero means the debug/source mapping reports line 0 in a project file.
