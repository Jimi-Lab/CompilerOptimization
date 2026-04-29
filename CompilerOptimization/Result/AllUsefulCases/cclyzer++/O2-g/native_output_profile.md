# cclyzer++ 原生输出 Profile

cclyzer++ 不输出 source-level bug report。它的原生输出是每个 run 的 `relations/*.csv.gz` 中的一组 Datalog relation facts。此次纳入的四个 run 已经包含从这些 raw relations 生成的 `ValueCases/`：relation inventory、IR/debug indexes、fact-to-source maps、classification TSVs、casebook entries，以及 `ValueCases/all_cases.csv`。

本 collector 只读取已完成的 `ValueCases/all_cases.csv` 文件，并保留指向 raw relation row 的证据字段：`relation_name`、`relation_row_number`、`relation_row_hash`，以及 IR snippet、source snippet、输入 `.bc`、生成的 `.ll` 和原始 evidence files。

从原生 case 分析中保留的主要 phenomenon labels：

| key | count |
| --- | ---: |
| `Wanted-AliasCollapseWithBadLocation` | 5444 |
| `Wanted-AllocationSiteDrift` | 2111 |
| `Wanted-CodeMismatch` | 3699 |
| `Wanted-LineColumnMissing` | 119574 |
| `Wanted-PhiMergeLocationDrift` | 18069 |

输入 ValueCases 中观察到的 mapping statuses：

| key | count |
| --- | ---: |
| `LineOutOfRange` | 8018 |
| `NoDebugLoc` | 122812 |
| `SourceFileMissing` | 10380 |
| `ColumnOutOfRange` | 213 |
| `SourceExistsCodeMismatch` | 7474 |
