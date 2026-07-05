# SMACK Static Scan Final Report

## 1. 输入信息
- BC 路径: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- 输出目录(请求): `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/smack/smack-O2-g`
- 输出目录(实际): `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/smack/smack-O2-g`
- Docker 镜像: `smackers/smack:latest-full`
- 关键版本:
  - clang-13: `Ubuntu clang version 13.0.1-2ubuntu2.2`
  - llvm-link-13 / llvm-dis-13: `Ubuntu LLVM version 13.0.1`
  - SMACK: `2.8.0`
  - boogie: `/home/user/.dotnet/tools/boogie`
  - corral: `/home/user/.dotnet/tools/corral`
  - z3: `/usr/bin/z3`

## 2. 扫描矩阵（计划）
- A1: `--check assertions --integer-encoding unbounded-integer --unroll 10 --verifier boogie --time-limit 1800`
- A2: `--check memory-safety --integer-encoding unbounded-integer --unroll 10 --verifier boogie --time-limit 1800`
- A3: `--check integer-overflow --integer-encoding unbounded-integer --unroll 10 --verifier boogie --time-limit 1800`
- A4: `--check memory-safety --integer-encoding unbounded-integer --unroll 16 --verifier boogie --time-limit 1800`
- A5: `--check assertions --integer-encoding bit-vector --unroll 10 --verifier boogie --time-limit 1800`
- A6: `--check memory-safety --integer-encoding bit-vector --unroll 10 --verifier boogie --time-limit 1800`
- A7: `--check integer-overflow --integer-encoding bit-vector --unroll 10 --verifier boogie --time-limit 1800`
- A8: `--check memory-safety --integer-encoding unbounded-integer --unroll 10 --verifier svcomp --time-limit 1800`
- 执行状态: 未执行（按要求在 translate 失败后停止）。

## 3. 结果总览
- verified: 0
- error: 0
- timeout: 0
- tool/backend failure: 0
- unsupported / translation failure: 1

## 4. Bug 候选列表
- 无。未出现 `SMACK found an error: ...`。

## 5. 非 bug 失败列表
- `translate_only`: `unsupported / translation failure`
  - 日志: `log/stdout/translate_only.out`, `log/stderr/translate_only.err`
  - 关键报错:
    - `Traceback (most recent call last):`
    - `Exception: llvm2bpl: ... Assertion 'PointeeType && "Must specify element type"' failed.`
    - `Running pass 'Merge GEPs for arrays indexing' ...`
  - 分类依据: 这是 `llvm2bpl` 翻译阶段崩溃，不是程序 bug。
- approximation warnings: 未检测到 `overapproximating` / `approximating llvm.lifetime` / `can lead to false alarms` 警告行。

## 6. 最终结论
- **FAIL**
- 说明: 翻译阶段失败，验证矩阵无法执行，不能对 assertions / memory-safety / integer-overflow 给出有效 verified/error 结论。

## 进度边界与未完成项
- 最后成功到: 环境检查 + BC 完整性检查。
- 失败步骤: translate-only。
- 失败原因: `llvm2bpl` 断言崩溃（翻译失败）。
- 未完成: A1-A8 扫描矩阵全部未启动。

## 产物状态
- 已生成: `artifacts/smack.init.bc`
- 未生成: `artifacts/smack.final.ll`, `artifacts/smack.bpl`（由于 translate 失败）
