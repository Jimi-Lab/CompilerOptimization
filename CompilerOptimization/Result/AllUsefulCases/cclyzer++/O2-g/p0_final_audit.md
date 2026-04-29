# cclyzer++ O2-g P0 最终审核

审核日期: `2026-04-29`.

## 结论

当前 `P0` rows 是有效的客观 invalid-location 证据，但它们并不都是彼此独立的论文 case，也不应全部描述为 "line-number mismatch" cases。

建议按以下方式解释：

- `LineOutOfRange` 和 `ColumnOutOfRange`: 最强、最适合论文正文使用的 location-invalid cases。
- `LineZero`: 有效的 invalid-line 证据，但通常支持的是 "no valid source line / debug line lost"，而不是错到了另一个非零行。
- Raw row counts 是 cclyzer++ relation-row 级别的计数；论文举例应使用去重后的代表性 source locations。

## 计数

| reason | rows | unique locations | audit verdict |
| --- | ---: | ---: | --- |
| `LineZero` | 27869 | 130 | 客观 line 0 证据；需要谨慎选择 |
| `ColumnOutOfRange` | 56 | 35 | 强 paper-ready 证据 |
| `LineOutOfRange` | 7 | 6 | 强 paper-ready 证据 |

P0 rows 总数: `27932`.

按 `(reported_file, reported_line, reported_column, priority_reason)` 去重后的 P0 unique locations: `171`.

## 批量检查结果

所有检查均通过：

- P0 `reported_file` 均能在本地找到。
- `LineZero` rows 均满足 `reported_line=0`。
- `LineOutOfRange` rows 均超过本地文件总行数。
- `ColumnOutOfRange` rows 均超过本地源码行长度。

## LineZero 细节

对于 `LineZero` rows：

- `ir_line=0`: `27115`
- 空 `ir_line`: `318`
- 非零 recovered `ir_line`: `436`

只有非零 recovered `ir_line` 子集，适合表述为 relation-level line 与 recovered IR debug line 之间的直接行号不一致。更大的 `ir_line=0` 子集，更适合表述为 source-line loss 或 no valid source location。

## 最强论文子集

建议第一批论文 examples 从以下子集中选择：

1. `LineOutOfRange`: 6 个 unique locations，全部在 flatbuffers project headers 中。
2. `ColumnOutOfRange`: 35 个 unique locations，主要在 libsndfile 和 tengine project source 中。
3. `LineZero` with nonzero `ir_line`: 436 rows；使用前应再选择去重后的代表性 source locations。

不要把 `P0=27932` 表述为独立 case 数。应将它表述为 raw cclyzer++ fact rows，并同时报告去重后的 locations。

## 各 Repo 的 P0 数量与来源

下表同时报告 raw relation rows 和按 `(reported_file, reported_line, reported_column, priority_reason)` 去重后的 unique locations。论文正文建议优先使用 unique locations，并从 `LineOutOfRange` / `ColumnOutOfRange` 中选代表。

| repo | P0 rows | unique locations | unique files | P0 reasons |
| --- | ---: | ---: | ---: | --- |
| `flatbuffers` | 16975 | 39 | 34 | `LineZero=16968`, `LineOutOfRange=7` |
| `libsndfile` | 7742 | 83 | 80 | `LineZero=7739`, `ColumnOutOfRange=3` |
| `tengine` | 411 | 35 | 3 | `LineZero=358`, `ColumnOutOfRange=53` |
| `zopfli` | 2804 | 14 | 14 | `LineZero=2804` |

### flatbuffers

- P0 rows: `16975`
- unique locations: `39`
- source region: `project_header=14470`, `project_source=2505`
- relation 来源: `subset.callgraph.callgraph_edge=16160`, `phi_instr=451`, `subset.var_points_to=358`, `subset_lift.allocation_by_instr_ctx=6`
- phenomenon 来源: `Wanted-LineColumnMissing=16341`, `Wanted-PhiMergeLocationDrift=335`, `Wanted-AliasCollapseWithBadLocation=293`, `Wanted-AllocationSiteDrift=6`
- 主要文件来源: `include/flatbuffers/*`, `src/idl_parser.cpp`, `src/idl_namer.h`, `src/namer.h`

代表性 P0 locations:

- `/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers/src/namer.h:36:10` -> `LineOutOfRange`
- `/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers/src/idl_namer.h:56:12` -> `LineOutOfRange`
- `/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers/src/idl_parser.cpp:0` -> `LineZero`

### libsndfile

- P0 rows: `7742`
- unique locations: `83`
- source region: `project_source=7252`, `project_header=490`
- relation 来源: `subset.callgraph.callgraph_edge=5874`, `phi_instr=1694`, `subset.var_points_to=168`, `subset_lift.allocation_by_instr_ctx=6`
- phenomenon 来源: `Wanted-LineColumnMissing=6703`, `Wanted-PhiMergeLocationDrift=926`, `Wanted-AliasCollapseWithBadLocation=107`, `Wanted-AllocationSiteDrift=6`
- 主要文件来源: `src/common.c` 以及 libsndfile `src/` 下多个 codec/container 源文件

代表性 P0 locations:

- `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.c:389:48` -> `ColumnOutOfRange`
- `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.c:193:30` -> `ColumnOutOfRange`
- `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.c:0` -> `LineZero`

### tengine

- P0 rows: `411`
- unique locations: `35`
- source region: `project_source=394`, `project_header=17`
- relation 来源: `subset.callgraph.callgraph_edge=323`, `phi_instr=60`, `subset.var_points_to=24`, `subset_lift.allocation_by_instr_ctx=4`
- phenomenon 来源: `Wanted-LineColumnMissing=338`, `Wanted-PhiMergeLocationDrift=49`, `Wanted-AliasCollapseWithBadLocation=20`, `Wanted-AllocationSiteDrift=4`
- 主要文件来源: `tests/common/tengine_operations.c`, `tests/common/common.h`, `examples/tm_classification.c`

代表性 P0 locations:

- `/home/jimi/PaperExperiment/CompilerOptimization/Target/Tengine/tests/common/tengine_operations.c:54:27` -> `ColumnOutOfRange`
- `/home/jimi/PaperExperiment/CompilerOptimization/Target/Tengine/tests/common/tengine_operations.c:75:45` -> `ColumnOutOfRange`
- `/home/jimi/PaperExperiment/CompilerOptimization/Target/Tengine/examples/tm_classification.c:0` -> `LineZero`

### zopfli

- P0 rows: `2804`
- unique locations: `14`
- source region: `project_source=2730`, `project_header=74`
- relation 来源: `subset.callgraph.callgraph_edge=2493`, `phi_instr=245`, `subset.var_points_to=66`
- phenomenon 来源: `Wanted-LineColumnMissing=2645`, `Wanted-PhiMergeLocationDrift=130`, `Wanted-AliasCollapseWithBadLocation=29`
- 主要文件来源: `src/zopfli/*.c` 和 `src/zopfli/symbols.h`

代表性 P0 locations:

- `/home/jimi/PaperExperiment/CompilerOptimization/Target/zopfli/src/zopfli/deflate.c:0` -> `LineZero`
- `/home/jimi/PaperExperiment/CompilerOptimization/Target/zopfli/src/zopfli/lz77.c:0` -> `LineZero`
- `/home/jimi/PaperExperiment/CompilerOptimization/Target/zopfli/src/zopfli/cache.c:0` -> `LineZero`
