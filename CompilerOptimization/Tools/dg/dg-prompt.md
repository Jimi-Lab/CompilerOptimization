



# DG Program-Level BC Scan Prompt (Reusable)

“请你使用dg-llvm14:latest docker针对/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc进行扫描，该bc为程序级bc，是-O2 -g编译生成的。将完整的扫描过程和扫描结果都记录到 /home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/dg/dg-LLVM14-O2-g 文件夹下，将运行的每一条命令都记录！！”


## 强制要求（必须遵守）
1. 不要有任何欺瞒和隐瞒。
2. 所有测试过程和结果必须保存到 `OUT_DIR`。
3. 每一条真实执行命令都要记录到 `commands.log`，一条不能漏。
4. 主报告扫描不要用 `-q`（仅在明确标注为 diagnostic 的检查中允许）。
5. 文本输出统一加 `--c-lines`。
6. 图输出统一加 `--dot`；PTA 图输出额外加 `--ir`。
7. 必须输出并保留：
   - `commands.log`
   - 原始 `stdout/stderr` 日志
   - `.dot` 图文件
   - `summary/steps.csv`
   - `summary/failures.csv`
   - `summary/line_hits.csv`
   - `summary/warnings.csv`
   - `report.md`
8. 失败、超时、崩溃、unsupported 必须如实标注，不能包装成通过。

## 扫描矩阵

### PTA
- `llvm-pta-dump --c-lines -pta fi <bc>`
- `llvm-pta-dump --c-lines --ir --dot -pta fi <bc>`
- `llvm-pta-dump --c-lines -pta fs --pta-field-sensitive 64 <bc>`
- `llvm-pta-dump --c-lines --ir --dot -pta fs --pta-field-sensitive 64 <bc>`
- `llvm-pta-dump --c-lines -pta inv --pta-field-sensitive 64 <bc>`
- `llvm-pta-dump --c-lines --ir --dot -pta inv --pta-field-sensitive 64 <bc>`

### DDA (memory SSA)
- `llvm-dda-dump --c-lines -dda ssa -pta fi <bc>`
- `llvm-dda-dump --c-lines --dot -dda ssa -pta fi <bc>`
- `llvm-dda-dump --c-lines -dda ssa -pta fs --pta-field-sensitive 64 <bc>`
- `llvm-dda-dump --c-lines --dot -dda ssa -pta fs --pta-field-sensitive 64 <bc>`
- `llvm-dda-dump --c-lines -dda ssa -pta inv --pta-field-sensitive 64 <bc>`
- `llvm-dda-dump --c-lines --dot -dda ssa -pta inv --pta-field-sensitive 64 <bc>`

### CDA (non-ICFG)
- `llvm-cda-dump --c-lines -cda standard <bc>`
- `llvm-cda-dump --c-lines --dot -cda standard <bc>`
- `llvm-cda-dump --c-lines -cda ntscd <bc>`
- `llvm-cda-dump --c-lines --dot -cda ntscd <bc>`
- `llvm-cda-dump --c-lines -cda ntscd2 <bc>`
- `llvm-cda-dump --c-lines --dot -cda ntscd2 <bc>`
- `llvm-cda-dump --c-lines -cda dod <bc>`
- `llvm-cda-dump --c-lines --dot -cda dod <bc>`
- `llvm-cda-dump --c-lines -cda dod+ntscd <bc>`
- `llvm-cda-dump --c-lines --dot -cda dod+ntscd <bc>`
- `llvm-cda-dump --c-lines -cda ntscd-ranganath <bc>`
- `llvm-cda-dump --c-lines --dot -cda ntscd-ranganath <bc>`
- `llvm-cda-dump --c-lines -cda dod-ranganath <bc>`
- `llvm-cda-dump --c-lines --dot -cda dod-ranganath <bc>`

### CDA (ICFG, truthful handling)
- `standard --cda-icfg` 在 DG 中应视为 unsupported（必须明确记录）
- `ntscd --cda-icfg --use-pta`：
  - 允许 diagnostic：`-q`、`--ir`
  - 文本/`--c-lines`/`--dot` 如不支持，必须明确报错记录，不能宣称成功

## 超时策略（建议默认）
- PTA fi / DDA fi：`900s`
- PTA fs/inv、DDA fs/inv：`1200s`
- CDA 常规模式：`300s`
- 若 CDA 超时补测：
  - 先 `1800s`，若仍超时再 `3600s`
  - `dod-ranganath` 直接 `7200s`

## 报告要求
- `report.md` 必须包含：
  - 成功项（completed / completed_with_warnings）
  - 失败项（failed）
  - 超时项（timeout）
  - unsupported 项
  - 关键 warning（例如 `UNHANDLED`, `loosing precision`, `IntToPtr`, `landingpad/invoke/resume`）
  - 最终结论：`PASS` / `PARTIAL PASS` / `FAIL`

## 结果真实性约束
- 不允许跳过失败项。
- 不允许只展示成功命令。
- 不允许把 diagnostic-only 结果当成 full support。
- 无法完成时必须说明具体卡点、最后成功到哪一步、剩余未完成项。
