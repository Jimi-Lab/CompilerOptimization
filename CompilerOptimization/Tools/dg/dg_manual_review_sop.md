# DG 人工判别 SOP

本 SOP 用于规范化人工审阅 DG 在 `clang-14 -O2 -g` 全程序 LLVM bitcode 上产生的源码行号结果。

它服务于 `paper.md` 与 `experiment.md` 中的实验目标：

- 识别优化后静态分析带来的源码位置漂移
- 识别多文件歧义
- 识别无法映射回源码的位置

## 1. 适用范围

本 SOP 适用于包含如下结果文件的 DG 输出目录：

- `commands.log`
- `log/`
- `dot/`
- `summary/steps.csv`
- `summary/failures.csv`
- `summary/line_hits.csv`
- `summary/line_hits_enriched.csv`
- `summary/warnings.csv`
- `report.md`

典型目录示例：

- `CompilerOptimization/Result/zopfli/dg/dg-LLVM14-O2-g/high_precision_20260403_041913`

## 2. 核心原则

DG 不会直接打印源码正文。DG 通过 `--c-lines` 输出 `line:column`，然后我们需要借助 LLVM debug metadata 将其解释为源码位置，并进一步补充真实源码片段供人工复核。

因此，人工审查对象不能只是原始 `log/*.stdout.log`，而必须同时结合：

1. `log/*.lines.stdout.log` 中的 DG 原始输出
2. `summary/line_hits.csv` 中的源码文件映射结果
3. `summary/line_hits_enriched.csv` 中的真实源码片段

## 3. 必须使用的输入文件

对每一条候选记录，至少同时查看以下三层：

1. **DG 原始文本输出**
   - `log/*.lines.stdout.log`
2. **映射后的源码文件候选**
   - `summary/line_hits.csv`
3. **补全后的真实源码片段**
   - `summary/line_hits_enriched.csv`

必要时还要查看：

- `summary/warnings.csv`
- `log/*.lines.stderr.log`
- `work/*.ll`（当你需要手工证明 debug metadata 链路时）

## 4. 审查单元

一个审查单元就是 `line_hits_enriched.csv` 中的一行。

每行至少包含这些关键信息：

- `step`
- `analysis_kind`
- `analysis_mode`
- `line`
- `column`
- `candidate_count`
- `normalized_source_file`
- `confidence`
- `dg_text`
- `code_snippet`

## 5. 标签体系

使用以下标签来判定 DG 的源码位置质量。

### 5.1 `L0-Unmappable`

满足以下任一条件时使用：

- `line == 0` 或 `column == 0`，并且明显表示缺失位置
- `source_count == 0`
- `source_exists == 0`
- `snippet_available == 0`

含义：

- DG 给出了一个结果，但这个结果无法可靠映射回真实源码位置。

典型证据：

- `0:0`
- `source_files` 为空

建议在论文中解释为：

- trace-loss
- 无法映射的调试位置
- 位置映射上的语义坍塌

### 5.2 `L1-Ambiguous`

满足以下条件时使用：

- `candidate_count > 1`

含义：

- 同一个 DG `line:column` 映射到了多个源码文件，因此该报告无法唯一指向开发者该修改的源码位置。

若能进一步看出成因，建议补充子标签：

- `Inline-Ambiguity`
- `Header-Expansion-Ambiguity`
- `Multi-CU-Ambiguity`

### 5.3 `L2-Drift-Suspected`

满足以下条件时使用：

- `candidate_count == 1`
- 源码文件存在
- 源码行存在
- 但该报告行的语句类型与当前 DG 分析模式预期关注的语义对象不匹配

含义：

- DG 给出了唯一位置，但这个位置很可能发生了归因漂移，或在语义上会误导开发者。

这是“看起来有定位，但定位错了/偏了”的主标签。

### 5.4 `L3-Matched`

满足以下条件时使用：

- `candidate_count == 1`
- 源码文件存在
- 源码行存在
- 该源码行的语句类型与局部上下文和分析模式一致

含义：

- 这条 DG 源码位置是可信且可操作的。

### 5.5 `L4-Unknown`

满足以下条件时使用：

- 当前证据不足，无法判入 `L0/L1/L2/L3`

## 6. 按分析模式审查的规则

不要孤立地看“这一行代码像不像有问题”。必须结合 DG 当前分析模式的语义目标来判断。

### 6.1 PTA 审查规则

PTA 合理命中的源码通常涉及：

- 指针定义
- 取地址（`&`）
- 解引用
- 指针赋值
- 堆分配（`malloc`、`calloc`、`realloc`、`free`）
- 数组访问
- 结构体字段访问

如果 DG 报到的是下面这些行，优先标为 `L2-Drift-Suspected`：

- 纯控制流（`if`、`for`、`while`），没有任何指针/对象操作
- 无关的 `return` 语句
- 注释、空行、纯宏包装行
- 被 inline 的 helper 定义行，而真正对象操作发生在 caller

### 6.2 DDA 审查规则

DDA 合理命中的源码通常涉及：

- 赋值
- 值更新
- C/C++ 里的读写行为
- 字段写入
- 带副作用的函数调用

如果 DG 报到的是下面这些行，优先标为 `L2-Drift-Suspected`：

- 只有声明，没有实际使用
- 只有分支条件，没有相关数据更新
- 真实 def-use 行在相邻几行，但 DG 报在纯控制行上
- 被 inline 的 callee 定义行，而不是 caller 的副作用位置

### 6.3 CDA 审查规则

CDA 合理命中的源码通常涉及：

- `if`
- `switch`
- `for`
- `while`
- `do`
- 条件早返回
- 三元控制表达式

如果 DG 报到的是下面这些行，优先标为 `L2-Drift-Suspected`：

- 纯赋值行
- 没有分支语义的分配调用行
- 普通算术语句
- 被 inline 的 helper 主体，而真实控制决策在 caller

## 7. 多文件歧义规则

### 7.1 最低判定规则

只要 `source_count > 1`，就先标为 `L1-Ambiguous`。

这是默认规则。

### 7.2 进一步解释

在标成 `L1-Ambiguous` 后，再人工判断歧义来源是否是：

- 同一个 `line:column` 同时出现在多个 `.c/.cc/.cpp` 文件里
- 同时出现在 `.h` 与 `.c/.cpp` 中
- 明显是 callee 被 inline 到 caller 之后产生的双重归因
- 宏展开或模板展开导致的位置复用

建议在备注里写成类似：

- `inline candidate: caller/callee both present`
- `header expansion candidate`
- `same coordinate reused across compilation units`

## 8. 逐步人工审查流程

对 `line_hits_enriched.csv` 中的每一条候选记录，按以下顺序检查。

### 第一步：先判断是否可映射

检查：

- `line`
- `column`
- `candidate_count`
- `source_exists`
- `snippet_available`

判定：

- 若是 `0:0`，或没有源码文件/源码片段 -> `L0-Unmappable`
- 若 `candidate_count > 1` -> `L1-Ambiguous`
- 否则继续下一步

### 第二步：读 DG 原始文本

检查：

- `dg_text`

例如：

- `62:12 -> 110:10`
- `0:0 -> 225:7`
- `<- 129:15`

先搞清楚 DG 正在表达的是：

- 依赖边
- points-to 目标
- 控制依赖边

### 第三步：读真实源码片段

检查：

- `normalized_source_file`
- `code_snippet`

问自己三个问题：

- 这一行是否包含当前分析模式应该命中的程序动作？
- 这个动作是发生在这一行本身，还是只发生在相邻行？
- 这一行是否只是头文件/helper/inline 后的位置壳，而真实逻辑在别处？

### 第四步：结合模式语义判断

使用第 6 节中的 PTA / DDA / CDA 规则。

判定：

- 语义匹配 -> `L3-Matched`
- 语义不匹配，但仍像是优化造成的附近漂移 -> `L2-Drift-Suspected`

### 第五步：记录优化证据

若你能看出优化痕迹，在备注中记录一条短原因：

- `inline`
- `phi/SSA merge`
- `header expansion`
- `location drift`
- `unmappable line 0`

## 9. Casebook 最小证据字段

对每条复核记录，至少保存以下字段：

- `step`
- `analysis_kind`
- `analysis_mode`
- `normalized_source_file`
- `line`
- `column`
- `candidate_count`
- `confidence`
- `dg_text`
- `code_snippet`
- `final_label`
- `root_cause_guess`
- `review_note`

## 10. 最小决策表

| 条件                               | 标签                   | 含义             |
| ---------------------------------- | ---------------------- | ---------------- |
| `0:0` 或没有源码/片段            | `L0-Unmappable`      | 无法直接使用     |
| `source_count > 1`               | `L1-Ambiguous`       | 无法唯一归因     |
| 单文件、行存在、但语句与模式不匹配 | `L2-Drift-Suspected` | 高度怀疑位置漂移 |
| 单文件、行存在、且语句与模式匹配   | `L3-Matched`         | 可信的源码位置   |
| 证据不足                           | `L4-Unknown`         | 暂无法判断       |

## 11. 如何服务论文写作

对论文最重要的三类 bucket 是：

1. `L0-Unmappable`
   - 最强证据：优化后的 IR 已经让源码可恢复性断裂
2. `L1-Ambiguous`
   - 说明优化保留了部分位置痕迹，但破坏了唯一归因
3. `L2-Drift-Suspected`
   - 说明工具虽然还在报源码行，但这个源码行在语义上已经开始误导开发者

`L3-Matched` 不应被丢弃，它是控制组，说明不是所有优化后位置都失真。

## 12. 实操注意事项

- 不要把 `diagnostic-only` 的 DG 输出当成 full support。
- 不要把 `L1` 和 `L2` 混在一起：歧义和漂移是两种不同失败模式。
- 不要默认“单文件命中”就一定正确。
- 不要把 `0:0` 当成开发者可直接修 bug 的位置。
- 建议优先人工审查 `high`，再审 `medium`，最后审 `low`。

## 13. 人工复核模板

建议使用如下模板记录：

```text
[DG Case ID]
Result Dir:
Step:
Analysis Kind/Mode:
Source File:
Line:Column:
Candidate Count:
Confidence:

DG Text:
Code Snippet:

Statement-Type Match: yes / no / unclear
Inline/Header Ambiguity: yes / no / unclear

Final Label: L0-Unmappable / L1-Ambiguous / L2-Drift-Suspected / L3-Matched / L4-Unknown
Root Cause Guess: line0 / inline / header-expansion / SSA-merge / other
Review Note:
```
