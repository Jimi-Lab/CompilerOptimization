# yapall 原生输出画像

## Run 选择边界
- run 选择文件：/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/result.txt
- 本画像和下游 CSV 只纳入该文件列出的五个 run 目录

## 使用的原生输入
- ValueCases/*_yapall_value_cases.csv
- ValueCases/raw_issues.csv，以及每行引用的原始 log 路径
- ValueCases/ll_provenance.csv，通过每行复制出的列使用
- report/final_report.md、commands/commands.log、status/run_status.tsv 作为 run 证据

## 原生分类统计
- unlocatable_operand: 902450
- InlineAttributionDrift: 624327
- Useless-CodeConsistent: 585664
- WrongFunctionAttribution: 209060
- Wanted-LineColumnMissing: 97204
- missing_debug_location: 76534
- ColumnPointsToWrongToken: 29460
- tool_output_insufficient: 1726

## 规范化策略
- 原始 yapall issue 行是 IR 层 pointer-analysis 报告，不是 source-level 已确认漏洞。
- 当本地源码文件可用时，重新计算 source file/line/column 的有效性。
- 报告位置在头文件中并不会自动成为 P0；必须存在客观无效证据。
- 除非存在客观的 project location 无效证据，否则 tool-output-insufficient 行保留为 P2。
