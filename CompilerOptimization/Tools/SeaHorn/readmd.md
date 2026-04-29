# SeaHorn 使用总结（面向本项目）

## 1) 环境与工具链要求（关键）

1. 必须使用 Docker 镜像：`seahorn/seahorn-llvm14:nightly`（本地镜像 ID: `340a5c5ccfbb`）。
2. 该镜像是 LLVM14 生态，常用工具为：
   - `clang-14`
   - `clang++-14`
   - `llvm-link-14`
   - `llvm-dis-14`
3. 注意：镜像内没有无后缀命令（如 `clang`、`llvm-link`），必须显式使用 `*-14`。
4. 已验证：若输入是 LLVM16 生成的 bitcode，会报 opaque pointer 兼容错误，不能直接用于 LLVM14 SeaHorn。

---

## 2) 与当前项目流程的对应关系

目标路径：`CompilerOptimization/Target/*`

结果路径：`CompilerOptimization/Result/<project>/seahorn/seahorn-O2-g/`

已约束并执行过的编译策略：
- 编译参数必须仅 `-O2 -g`
- 不允许 `-DNDEBUG`
- 不使用 `RelWithDebInfo`
- 仅做“编译 + whole-program bc 链接”；扫描可后续单独执行

---

## 3) SeaHorn 模式总览（按用途分组）

SeaHorn 顶层命令较多，很多是流水线别名。对本项目最相关的是：

### A. 前处理/构建流水线组件（不是最终扫描结果）

- `clang`, `pp`, `ms`, `opt`, `fe`, `lfe`, `clang-pp`
- `unroll`, `cut-loops`, `rmtf`, `wmem`, `linkrt`

### B. CHC 验证主线（静态验证）

- `horn`（核心）
- `pf`（`fe|horn --solve`）
- `smt`, `clp`, `horn-clp`, `boogie`

### C. 更像“静态扫描报点”的命令（优先）

- `inspect-bitcode` / `inspect`：程序结构画像、CFG、DSA统计
- `smc-checks` / `smc`：Simple Memory Checks（可直接输出 File/Line/Column）
- `ndc-inst` / `ndc`：空指针检查插桩
- `crab-inst` / `crab`：抽象解释不变式
- `term`：终止性分析

### D. 当前不关注（偏符号执行/反例执行）

- `--bmc` 路线、`cex`、`exe-cex`、`bpf` 等

---

## 4) 针对“尽可能多 case + 行号一致性分析”的推荐策略

核心目标是拿到大量可定位 case（文件、行号、列号、源码上下文），而非只看 `sat/unsat`。

推荐分层执行：

1. `inspect-bitcode`：先做规模画像（函数数、块数、内存图统计）
2. `smc-checks --print-smc-stats`：主力产出可疑点（最直接给行号）
3. 同一项目跑两套 SMC（扩大覆盖）：
   - `--sea-dsa-type-aware` 开
   - `--sea-dsa-type-aware` 关
4. 提高阈值扩大检查范围：
   - `--smc-check-threshold` 远高于默认值（默认 100，建议 50000 到 200000）
5. `smc-checks -o <smc.bc>` 后再跑 `horn --solve`，分层：
   - `--track=reg`
   - `--track=ptr`
   - `--track=mem --dsa sea-cs`（最重）
6. `ndc-inst`（空指针插桩）+ `horn` 作为补充

结论：

若目标是“报告 case 数量最大化并用于行号一致性研究”，`smc-checks --print-smc-stats` 是第一优先级，`horn` 是补充验证层。

---

## 5) 推荐命令模板（对单个 whole-program bc）

假设输入：

`/work/PaperExperiment/CompilerOptimization/Result/<project>/seahorn/seahorn-O2-g/artifacts/<project>_O2_g.bc`

### 5.1 程序画像

```bash
sea inspect-bitcode --profiler "<project>_O2_g.bc"
```

### 5.2 主力报点（SMC）

```bash
sea smc-checks --print-smc-stats --smc-check-threshold=200000 "<project>_O2_g.bc"
sea smc-checks --print-smc-stats --smc-check-threshold=200000 --sea-dsa-type-aware "<project>_O2_g.bc"
```

### 5.3 生成插桩 bc

```bash
sea smc-checks --smc-check-threshold=200000 "<project>_O2_g.bc" -o "<project>_O2_g.smc.bc"
```

### 5.4 在插桩后 bc 上进行 CHC 求解（静态验证，不走符号执行）

```bash
sea horn "<project>_O2_g.smc.bc" --solve --step=large --track=reg --cpu 3600 --mem 24000
sea horn "<project>_O2_g.smc.bc" --solve --step=large --track=ptr --cpu 5400 --mem 32000
sea horn "<project>_O2_g.smc.bc" --solve --step=small --track=mem --dsa sea-cs --cpu 7200 --mem 48000
```

---

## 6) 日志与结果整理建议（用于后续行号一致性分析）

建议统一保存到：

`CompilerOptimization/Result/<project>/seahorn/seahorn-O2-g/log/`

推荐日志文件名：

- `sea.inspect.profiler.log`
- `sea.smc.stats.typeoff.log`
- `sea.smc.stats.typeon.log`
- `sea.smc.instrument.log`
- `sea.horn.smc.reg.log`
- `sea.horn.smc.ptr.log`
- `sea.horn.smc.mem.log`

`smc-checks` 重点提取字段：

- `File`
- `Line`
- `Column`
- `Bitcode`

再映射到源码后统计：

- `match`
- `mismatch`
- `line_oob`
- `missing_file`

---

## 7) sat/unsat/unknown 解释（避免误读）

- `sat`：存在可达错误路径（可认为发现问题）
- `unsat`：在当前建模与配置下未发现错误
- `unknown/timeout`：资源不足或模型过重，不能当作“无问题”

---

## 8) 当前状态结论（本仓库）

- SeaHorn 编译流程已切换到 LLVM14（`clang-14` / `llvm-link-14`）。
- 已有 8 个系统级 whole-program bc 可用于后续 SeaHorn 扫描。
- 若要最大化 case 数量，应优先批量运行 `smc-checks --print-smc-stats` 双配置，再补 `horn` 三档验证。
