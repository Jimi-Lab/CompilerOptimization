# yapall 与 cclyzer++ P0 现象诊断

## 结论

`yapall` 和 `cclyzer++` 的 P0 数量看起来很大，主要原因不是出现了同等数量的独立漏洞或独立论文 case，而是两个工具都输出了非常细粒度的 IR/fact/issue rows。同一个无效源码位置会被许多 relation rows、use-site rows、callgraph edges、points-to facts 或 pointer-analysis issue rows 反复引用，从而把 raw P0 row count 放大。

这不是单纯的“工具坏了”，也不是单纯的“统计错了”。更准确的判断是：

- P0 证据本身是有效的：它们满足 `useful_cases_matrix_plan.md` 中机器可检查的 invalid-location 条件。
- raw row 数不能当成独立 case 数：论文正文应使用去重后的 unique locations 和代表性 examples。
- 这些 P0 反映的是 `clang -O2 -g` 优化 IR 中 debug/source mapping 退化后，IR 层工具在恢复源码位置时看到的客观异常。
- `LineZero` 应表述为 `no valid source line` / `source-line loss` / `line attribution collapsed to 0`，不要笼统写成每一条都是 wrong-line mismatch。

## 总体规模

| tool | raw P0 rows | tool-local unique locations | unique files | 主要 P0 reason |
| --- | ---: | ---: | ---: | --- |
| `yapall` | 69526 | 298 | 298 | `LineZero` |
| `cclyzer++` | 27932 | 171 | 131 | `LineZero`, `ColumnOutOfRange`, `LineOutOfRange` |

两个工具合并后，按 `(reported_file, reported_line, reported_column, priority_reason)` 去重，共有 385 个 cross-tool unique P0 locations。其中 84 个 unique locations 同时被 `yapall` 和 `cclyzer++` 命中，主要是 `LineZero`。这说明一部分 P0 是跨工具共同观察到的 debug/source-location 退化现象。

## yapall P0 分析

### P0 类型

`yapall` 当前所有 P0 都是：

- `priority_reason`: `LineZero`
- `location_validity`: `line_zero`
- `case_kind`: `LocationInvalid`
- `mode`: `subset:k0:default`
- `classification`: `Wanted-LineColumnMissing`
- `mapping_status`: `source_line_missing`

按 target 统计：

| target | P0 rows | unique locations |
| --- | ---: | ---: |
| `lepton` | 28424 | 81 |
| `masscan` | 24537 | 115 |
| `libsndfile` | 16435 | 96 |
| `tengine` | 103 | 3 |
| `zopfli` | 27 | 3 |

按 source region：

| source_region | rows |
| --- | ---: |
| `project_source` | 56209 |
| `project_header` | 13317 |

### 为什么 raw rows 很大

`yapall` 的 P0 是 pointer-analysis issue rows。一个 line-zero location 可以对应很多不同的 operand/allocation/use-site 组合。

P0 issue kind 分布：

| issue kind | rows |
| --- | ---: |
| `invalid_store` | 34822 |
| `points_to_top` | 23071 |
| `invalid_load` | 8765 |
| `invalid_memcpy_dst` | 2133 |
| `invalid_call` | 491 |
| `invalid_memcpy_src` | 244 |

重复放大很明显：

| metric | rows per unique location |
| --- | ---: |
| min | 1 |
| median | 26 |
| p90 | 558 |
| p99 | 2977 |
| max | 8327 |

最大重复 location 是：

```text
lepton
/home/jimi/PaperExperiment/CompilerOptimization/Target/lepton/src/vp8/model/model.cc:0
rows: 8327
reason: LineZero
```

这不是 8327 个独立源码 bug，而是同一个无效 source line 被大量 yapall issue rows 重复引用。

### 如何解释 yapall P0

`yapall` P0 适合支持：

- O2-g IR 中有大量 debug/source line 丢失到 `line=0` 的现象；
- pointer-analysis issue rows 可以定位到 project source/header 文件名，但源码行号无效；
- 同一无效位置会在多个 pointer facts/use-sites 上被重复放大。

不应表述为：

- `yapall` 找到了 69526 个独立漏洞；
- `yapall` 有 69526 个独立 paper cases；
- 每个 `LineZero` 都已经证明“错到了另一个具体非零源码行”。

## cclyzer++ P0 分析

### P0 类型

`cclyzer++` 的 P0 有三类：

| reason | rows | unique locations | 解释 |
| --- | ---: | ---: | --- |
| `LineZero` | 27869 | 130 | source line 为 0，表示没有有效源码行 |
| `ColumnOutOfRange` | 56 | 35 | reported column 超过实际源码行长度 |
| `LineOutOfRange` | 7 | 6 | reported line 超过实际文件总行数 |

按 target 统计：

| target | P0 rows | unique locations | reasons |
| --- | ---: | ---: | --- |
| `flatbuffers` | 16975 | 39 | `LineZero=33`, `LineOutOfRange=6` |
| `libsndfile` | 7742 | 83 | `LineZero=80`, `ColumnOutOfRange=3` |
| `tengine` | 411 | 35 | `LineZero=3`, `ColumnOutOfRange=32` |
| `zopfli` | 2804 | 14 | `LineZero=14` |

按 source region：

| source_region | rows |
| --- | ---: |
| `project_header` | 15051 |
| `project_source` | 12881 |

### 为什么 raw rows 很大

`cclyzer++` 的原生输出不是 source-level warning，而是 Datalog relation facts。P0 rows 大量来自 relation-level facts：

| relation/mode | rows |
| --- | ---: |
| `subset.callgraph.callgraph_edge` | 24850 |
| `phi_instr` | 2450 |
| `subset.var_points_to` | 616 |
| `subset_lift.allocation_by_instr_ctx` | 16 |

phenomenon 来源：

| phenomenon | rows |
| --- | ---: |
| `Wanted-LineColumnMissing` | 26027 |
| `Wanted-PhiMergeLocationDrift` | 1440 |
| `Wanted-AliasCollapseWithBadLocation` | 449 |
| `Wanted-AllocationSiteDrift` | 16 |

重复放大也很明显：

| metric | rows per unique location |
| --- | ---: |
| min | 1 |
| median | 20 |
| p90 | 353 |
| p99 | 1967 |
| max | 3909 |

最大重复 location 是：

```text
flatbuffers
/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers/include/flatbuffers/table.h:0
rows: 3909
reason: LineZero
```

这说明同一个 line-zero header location 被大量 callgraph/points-to/phi facts 复用。

### cclyzer++ 的强证据子集

`LineOutOfRange` 和 `ColumnOutOfRange` 比 `LineZero` 更适合作为论文正文 examples，因为它们能直接展示：

- 行号超过文件总行数；
- 列号超过实际源码行长度；
- 本地文件存在，因此不是 source-file-missing 或 remap 未解析造成的弱证据。

强 P0 子集：

- `LineOutOfRange`: 7 rows / 6 unique locations，全部来自 flatbuffers project header。
- `ColumnOutOfRange`: 56 rows / 35 unique locations，主要来自 libsndfile 和 tengine project source。

`LineZero` 仍是客观 invalid-line 证据，但更适合表述为 source-line loss，而不是每条都表述为具体 line mismatch。

## 工具问题还是统计问题

### 不是普通意义上的漏洞数量

`P0` 在本矩阵里表示“可直接进入论文证据的高置信 invalid-location evidence”，不是“工具报告的真实漏洞”。因此：

```text
yapall P0=69526
cclyzer++ P0=27932
```

不能写成两个工具分别找到了 69526 和 27932 个独立 bug。

### 也不是简单统计错误

这些 rows 确实来自本地 artifact：

- 有 run directory；
- 有 raw artifact；
- 有 ValueCases 或 relation evidence；
- 位置有效性检查通过；
- P0 reason 与 `useful_cases_matrix_plan.md` 中的机器可检查规则一致。

因此它们不是凭空产生的错误统计，而是“row-level evidence count”。

### 更准确的解释

这是三层因素叠加：

1. `clang -O2 -g` 优化 IR 使部分 debug/source location 退化，表现为 `line=0`、越界 line、越界 column。
2. IR 层工具输出的是 relation/fact/use-site/issue 粒度，不是去重后的 source-level diagnostics。
3. collector 当前保留 raw rows 以便审计，因此同一个 bad source location 会被很多 fact rows 放大。

所以正确表述应是：

```text
两个工具都观察到大量 row-level invalid source-location evidence。
去重后，yapall 有 298 个 P0 unique locations，cclyzer++ 有 171 个 P0 unique locations；
跨工具合并后共有 385 个 unique locations，其中 84 个被两个工具共同命中。
这些 evidence 支持 O2-g debug/source mapping 退化与 IR fact 级放大效应，
不应解释为等量独立漏洞或等量独立论文 case。
```

## 论文使用建议

1. 正文不要报告 raw P0 rows 作为独立 case 数；可以作为 row-level evidence 规模。
2. 正文主表建议同时报告 `raw rows` 和 `unique locations`。
3. 论文 examples 优先从 `cclyzer++` 的 `ColumnOutOfRange` / `LineOutOfRange` 中选，因为它们最直观。
4. `LineZero` 可以作为大规模 source-line loss 现象使用，但要谨慎措辞。
5. 对 `LineZero` 中 IR anchor 有非零 `ir_line` 的子集，可以进一步人工挑选为更强的 source/IR attribution drift examples。
6. 对每个 target 选 1-2 个 unique location 代表即可，避免让 row-level duplicates 主导叙事。
