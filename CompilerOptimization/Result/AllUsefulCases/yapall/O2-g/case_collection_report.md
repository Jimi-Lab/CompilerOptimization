# yapall O2-g Case Collection Report

## Scope
- tool: yapall
- universe: LLVM14-O2-g / O2-g only
- run selection file: /home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/result.txt
- selected targets: lepton, libsndfile, masscan, tengine, zfp, zopfli
- selected run directories: 6
- analyzer rerun: no; collected from existing ValueCases
- output directory: /home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/O2-g

## Allowed Run Directories
- /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/yapall/LLVM14-O2-g/run_20260427_yapall_docker_smoke
- /home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked
- /home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/yapall/LLVM14-O2-g/run_20260506_yapall_docker_masscan_linked_rescan
- /home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/yapall/LLVM14-O2-g/run_20260427_yapall_docker_tengine_linked
- /home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/yapall/LLVM14-O2-g/run_20260427_yapall_docker_lepton_linked
- /home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0

## Row Counts
- raw ValueCases rows read: 2527059
- included tool_cases rows: 1941393
- excluded rows: 585666

## Priority Counts
- P2: 1110521
- P1: 761238
- P0: 69634

## Priority Reasons
- UnlocatableOperand: 902700
- InlineAttributionDrift: 452866
- ExternalOrUnresolvedCandidate: 206093
- WrongFunctionAttribution: 202378
- NoDebugLoc: 76534
- LineZero: 69634
- ColumnPointsToWrongToken: 29460
- ToolOutputInsufficient: 1728

## Location Validity
- unknown: 904428
- valid: 863119
- line_zero: 82320
- no_debug_loc: 76534
- column_out_of_range: 14992

## Source Regions
- llvm_ir_only: 980962
- project_source: 530495
- project_header: 223843
- system_header: 205004
- system_source: 1089

## Per-target Priority Counts
- lepton: P0=28424, P1=409084, P2=374889
- libsndfile: P0=16435, P1=223444, P2=585755
- masscan: P0=24537, P1=119179, P2=149457
- tengine: P0=103, P1=9020, P2=152
- zfp: P0=108, P1=272, P2=252
- zopfli: P0=27, P1=239, P2=16

## Excluded Rows
- Useless-CodeConsistent: 585666

## Selected ValueCases Inputs
- /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/yapall/LLVM14-O2-g/run_20260427_yapall_docker_smoke/ValueCases/zopfli_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/ValueCases/libsndfile_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/yapall/LLVM14-O2-g/run_20260506_yapall_docker_masscan_linked_rescan/ValueCases/masscan_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/yapall/LLVM14-O2-g/run_20260427_yapall_docker_tengine_linked/ValueCases/tengine_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/yapall/LLVM14-O2-g/run_20260427_yapall_docker_lepton_linked/ValueCases/lepton_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/zfp/yapall/LLVM14-O2-g/run_20260426_yapall_zfp_k0/ValueCases/zfp_yapall_value_cases.csv

## Interpretation Notes
- No auxiliary discovered runs are included; all run-level and case-level evidence is restricted to result.txt.
- P0 rows are objective invalid source-location evidence, not independent paper case counts.
- P1 rows are strong candidates that still need semantic/manual inspection.
- P2 rows are weak, external, unresolved, or output-insufficient evidence retained for appendix-scale context.
