# yapall P0 最终审计

## 范围
- 工具：yapall
- 编译宇宙：仅 LLVM14-O2-g / O2-g
- 来源 CSV：/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/tool_cases.csv
- unique locations CSV：/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/O2-g/p0_unique_locations.csv

## P0 统计
- P0 行数：69526
- P0 unique locations：298
- P0 unique files：298

## 按原因统计 P0 行
- LineZero: 69526

## 按原因统计 P0 Unique Locations
- LineZero: 298

## 按 Target 统计 P0 行
- lepton: 28424
- masscan: 24537
- libsndfile: 16435
- tengine: 103
- zopfli: 27

## 按 Target 统计 P0 Unique Locations
- masscan: 115
- libsndfile: 96
- lepton: 81
- zopfli: 3
- tengine: 3

## 验证结果
- ok: 298

## 解释说明
- P0 行是 relation/use-site 证据行，不等同于论文中互相独立的 case。
- Unique locations 按 reported_file、reported_line、reported_column 和 priority_reason 去重。
- LineZero 表示 debug/source mapping 将位置报告到 project file 的第 0 行。
