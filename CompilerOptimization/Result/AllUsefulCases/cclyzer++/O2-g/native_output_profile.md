# cclyzer++ 原生输出 Profile

cclyzer++ 不输出 source-level bug report。它的原生输出是每个 run 的 `relations/*.csv.gz` 中的一组 Datalog relation facts。此次纳入的 run 都使用这些 raw relations 生成或复用 `ValueCases/`：relation inventory、IR/debug indexes、fact-to-source maps、classification TSVs、casebook entries，以及 `ValueCases/all_cases.csv`。

本 collector 不读取 `extract/` 摘要。它读取已完成的 `ValueCases/all_cases.csv` 文件，并保留指向 raw relation row 的证据字段：`relation_name`、`relation_row_number`、`relation_row_hash`，以及 IR snippet、source snippet、输入 `.bc`、生成的 `.ll`、`relations/` 和原始 evidence files。

从原生 case 分析中保留的主要 phenomenon labels：

| key | count |
| --- | ---: |
| `Wanted-AliasCollapseWithBadLocation` | 9420 |
| `Wanted-AllocationSiteDrift` | 3351 |
| `Wanted-CodeMismatch` | 7280 |
| `Wanted-LineColumnMissing` | 239939 |
| `Wanted-PhiMergeLocationDrift` | 30003 |

输入 ValueCases 中观察到的 mapping statuses：

| key | count |
| --- | ---: |
| `LineOutOfRange` | 8837 |
| `NoDebugLoc` | 247800 |
| `SourceFileMissing` | 21316 |
| `ColumnOutOfRange` | 327 |
| `SourceExistsCodeMismatch` | 11713 |
