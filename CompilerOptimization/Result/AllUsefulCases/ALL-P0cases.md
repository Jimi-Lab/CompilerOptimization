# All P0 Cases Summary

本文件汇总当前 `AllUsefulCases` 中各 IR-level analyzer 在 `O2-g` / `LLVM14-O2-g` universe 下的 P0 证据规模。

说明：

- `P0` 是 paper-ready 高置信证据优先级，不是 analyzer bug 严重等级。
- 表中 `N_P0` 表示当前已归档的 P0 数量；带 `P1/P2` 的单元格保留强/弱候选数量。
- `0_P0` 表示该 repo/tool 已扫描但当前没有 P0。
- `null` 表示当前没有可纳入的有效结果或尚未统计。
- `OOM kill`、扫描失败、长时间未完成等状态按当前实验状态保留。

## Tool Coverage

| tool | 当前状态 |
| --- | --- |
| phasar | 扫 8 个 repo |
| seahorn/crab/clam | 扫 8 个 repo |
| smack | 扫 2 个 repo；源码已改好，仍在测试。此前主要卡在 `llvm2bpl` 报错 |
| dg | 扫 8 个 repo |
| ikos | 源码已改，仍在适配；当前一直报错误输入类型，输入为 `-O2 -g` |
| cclyzer++ | 扫 7 个 repo |
| yapall | 扫 6 个 repo |

## Repo-Level P0 Matrix

| repo | phasar | seahorn | dg | cclyzer++ | yapall |
| --- | --- | --- | --- | --- | --- |
| flatbuffers | bc 太大，扫描失败 | 0_P0 | 65_P0 | 39_P0 | OOM kill |
| lepton | 257_P2 | 0_P0 | 124_P0 + 152_P1 | 71_P0 | 81_P0 |
| libsndfile | 3_P0 | 42_P0 | 10_P0 + 14_P1 | 83_P0 | 96_P0 |
| masscan | 3_P0 + 1_P2 | 0_P0 | 7_P0 + 266_P1 | 97_P0 | 115_P0 |
| redis | 258_P0 + 12_P2 | 0_P0 | 55_P0 + 122_P1 | 30h 都没跑完 | OOM kill |
| tengine | null | 11_P0 | 9_P0 + 64_P1 | 35_P0 | 3_P0 |
| zfp | 90_P0 | 3_P0 | 12_P0 | 42_P0 | 4_P0 |
| zopfli | null | 0_P0 | 13_P0 | 14_P0 | 3_P0 |
| 汇总 | 354_P0 | 56_P0 | 295_P0 | 381_P0 | 302_P0 |

## Notes

- 当前汇总重点是已能形成 P0 证据的工具：`phasar`、`seahorn`、`dg`、`cclyzer++`、`yapall`。
- `smack` 和 `ikos` 暂未纳入 repo-level P0 matrix：`smack` 仍在修复/测试 `llvm2bpl` 相关问题；`ikos` 仍在适配 `-O2 -g` 输入类型问题。
- 对论文正文，建议使用 P0 作为主要 case pool；P1/P2 作为后续人工验证和附录讨论候选。
