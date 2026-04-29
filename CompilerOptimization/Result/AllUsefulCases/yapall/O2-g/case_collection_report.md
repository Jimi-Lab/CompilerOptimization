# yapall O2-g Case 收集报告

## 范围
- 工具：yapall
- 编译宇宙：仅 LLVM14-O2-g / O2-g
- run 选择文件：/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/result.txt
- 已选择 targets：lepton, libsndfile, masscan, tengine, zopfli
- 已选择 run 目录数：5
- 是否重跑 analyzer：否；从已有 ValueCases 中收集
- 输出目录：/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/O2-g

## 允许纳入的 Run 目录
- /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/yapall/LLVM14-O2-g/run_20260427_yapall_docker_smoke
- /home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked
- /home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/yapall/LLVM14-O2-g/run_20260427_yapall_docker_masscan_linked
- /home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/yapall/LLVM14-O2-g/run_20260427_yapall_docker_tengine_linked
- /home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/yapall/LLVM14-O2-g/run_20260427_yapall_docker_lepton_linked

## 行数统计
- 读取的原始 ValueCases 行数：2526425
- 纳入 tool_cases 的行数：1940761
- 排除的行数：585664

## 优先级统计
- P2: 1110269
- P1: 760966
- P0: 69526

## 优先级原因
- UnlocatableOperand: 902450
- InlineAttributionDrift: 452594
- ExternalOrUnresolvedCandidate: 206093
- WrongFunctionAttribution: 202378
- NoDebugLoc: 76534
- LineZero: 69526
- ColumnPointsToWrongToken: 29460
- ToolOutputInsufficient: 1726

## 位置有效性
- unknown: 904176
- valid: 862847
- line_zero: 82212
- no_debug_loc: 76534
- column_out_of_range: 14992

## 源码区域
- llvm_ir_only: 980710
- project_source: 530115
- project_header: 223843
- system_header: 205004
- system_source: 1089

## 按 Target 统计优先级
- lepton: P0=28424, P1=409084, P2=374889
- libsndfile: P0=16435, P1=223444, P2=585755
- masscan: P0=24537, P1=119179, P2=149457
- tengine: P0=103, P1=9020, P2=152
- zopfli: P0=27, P1=239, P2=16

## 排除的行
- Useless-CodeConsistent: 585664

## 已选择的 ValueCases 输入
- /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/yapall/LLVM14-O2-g/run_20260427_yapall_docker_smoke/ValueCases/zopfli_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/yapall/LLVM14-O2-g/run_20260427_yapall_docker_sndfile_convert_linked/ValueCases/libsndfile_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/masscan/yapall/LLVM14-O2-g/run_20260427_yapall_docker_masscan_linked/ValueCases/masscan_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/tengine/yapall/LLVM14-O2-g/run_20260427_yapall_docker_tengine_linked/ValueCases/tengine_yapall_value_cases.csv
- /home/jimi/PaperExperiment/CompilerOptimization/Result/lepton/yapall/LLVM14-O2-g/run_20260427_yapall_docker_lepton_linked/ValueCases/lepton_yapall_value_cases.csv

## 解释说明
- 未纳入任何辅助 discovery 得到的 run；所有 run-level 和 case-level 证据均严格限制在 result.txt 中。
- P0 行表示客观无效的源码位置证据，不等同于论文中互相独立的 case 数量。
- P1 行是强候选证据，仍需要语义检查或人工检查。
- P2 行是弱证据、外部证据、未解析证据或输出不足证据，保留用于附录级上下文。
