# 实验的完整思路与执行步骤 (LLM-Agent Semantic Recovery Framework)

我们的目标不再仅仅是“测量”工具的失效，而是要在一个完整的**Neuro-Symbolic（神经符号结合）**框架下，让 LLM Agent 介入并解决“-O2 优化导致的静态语义坍塌”问题。

整个实验分为两个主要阶段：**基线测量（找病因）**与**Agent 介入修复（治病）**。

---

## 阶段一：构建“语义坍塌”靶场 (The "Semantic Collapse" Baseline)

这一步我们要拿到 **O0 能报（True Positive）、O2 漏报（False Negative）** 的真实漏洞样例，作为 Agent 的试验台。

### 1. 目标靶机选择

* **Target**: 真实世界的复杂系统，优先选择目前工作区中已有的 `curl 7.68.0`, `redis`, `leveldb` 等。
* **Ground Truth (The Bug)**: 在靶机中挑选一个明确已知的 CWE (例如内存越界、Use-After-Free) 或关键的 Source-to-Sink 污点流。

### 2. 构建三重编译宇宙 (Compilation Universes)

我们需要使用统一的 LLVM/Clang 编译链，直接执行 `clang`/`clang++` 的优化选项，提取含有不同优化烈度的全程序 IR（Link-Time Optimization Bitcode, `*.bc`）：

1. **`clang -O0 -g`（基线对照组）**: 作为结构相对完整、能被静态工具顺利追踪的参照标准。
2. **`clang -O2 -g`（主实验组）**: 本文核心研究对象，即带调试信息的优化 LLVM bitcode。
3. **`clang -O2 -g -fno-inline`（因果隔离组）**: 控制变量，用于观察禁用 inline 后 IR 静态分析结果是否恢复。

#### 编译配置强约束（直接使用 clang 优化选项）

> **核心原则**：主实验只研究 `clang -O2 -g` 生成的 `.bc` 对 IR 静态扫描工具的影响。不要默认追加 `-DNDEBUG`，也不要把 CMake `RelWithDebInfo` 的默认语义写入主实验定义。
>
> **理由**：
>
> 1. `clang -O0 -g` 不触发主要优化，适合作为 IR 结构基线。
> 2. `clang -O2 -g` 同时触发 Inline、Mem2Reg、SROA、GVN、DCE 等优化，并保留 DWARF 调试信息，正是本文要研究的 optimized debug bitcode。
> 3. `-DNDEBUG` 会改变源码级宏语义，尤其会移除 `assert()`，它属于额外变量；除非单独设计 production-release 对照实验，否则主实验不加入。
> 4. DWARF 调试信息在 `-O2 -g` 下的行号漂移（`DW_TAG_inlined_subroutine` 指向被内联函数原始定义处而非调用处），正是我们要捕捉的"时空错乱 (Trace-loss)"特征。

三个编译宇宙的完整定义如下：

| 宇宙                  | 实际编译 Flags                  | 用途                                                               |
| --------------------- | ------------------------------- | ------------------------------------------------------------------ |
| **O0**          | `clang -O0 -g`                       | 基线对照组：IR 结构相对完整，便于静态工具追踪                              |
| **O2**          | `clang -O2 -g`                       | **主实验组**：Inline/Mem2Reg/SROA 等优化触发，行号漂移在此发生 |
| **O2-noinline** | `clang -O2 -g -fno-inline`           | 因果隔离组：仅禁用 Inline，观察 IR 工具结果是否恢复                        |

对应的 clang 命令模板：

```bash
# O0 基线对照组
clang-14 -O0 -g -emit-llvm -c <input.c> -o <target>_O0_g.bc

# O2 主实验组
clang-14 -O2 -g -emit-llvm -c <input.c> -o <target>_O2_g.bc

# O2-noinline 因果隔离组
clang-14 -O2 -g -fno-inline -emit-llvm -c <input.c> -o <target>_O2_g_noinline.bc
```

> **禁止事项**：主实验不得隐式加入 `-DNDEBUG`；不得把任何构建系统的默认 build type 直接等同于本文的 O2 宇宙。若目标项目必须通过 CMake 构建，也要显式检查最终 `compile_commands.json` 或 bitcode 生成命令，确认实际 flags 是 `-O2 -g`。

### 3. 基准测试与提取靶点 (Baseline Measurement)

1. 针对 IR 分析器（SVF、Phasar、IKOS、KLEE、SeaHorn、SMACK 等），分别喂入 `clang -O0 -g`、`clang -O2 -g` 和 `clang -O2 -g -fno-inline` 的 `.bc` 文件。
2. **捕获靶点**：记录 IR 工具在 `-O0 -g` 下可见、在 `-O2 -g` 下消失/漂移/爆炸的路径或告警，并抓取由于 `inline` + `Mem2Reg` (SSA Phi-nodes 合并) 导致链路中断的确切位置。
3. 使用 `-O2 -g -fno-inline` 作为因果隔离组，判断 inline 是否是主要触发因素。

---

## 阶段二：LLM Agent (NeuroMap) 语义锚定与修复

这是本文的核心创新实验：证明 LLM 可以跨越优化鸿沟。

### 1. 意图提取与模糊对齐 (Intent Extraction & Fuzzy Alignment)

* **输入**：LLM Agent 同时读取该漏洞的 **未优化 C/C++ 源码** 和令人眼花缭乱的 **`-O2` LLVM IR 文本 (.ll)**。
* **动作**：Agent 需要利用上下文理解能力，识别出源码中的敏感变量是如何被编译器“揉碎”并重命名为虚拟寄存器（如 `%23 = phi i32 ...`）的。
* **输出**：生成一个**“跨层语义锚点表” (Cross-layer Semantic Anchors)**。它标记了 IR 中哪些被合并或折叠的节点在业务逻辑上是属于同一条污点流的。

### 2. 引导下层引擎重新连通 (Agent-Guided Analysis)

* 将传统静态分析工具（SVF/Phasar）与 Agent 进行联动（Neuro-Symbolic 融合）。
* 当传统的图遍历算法在 `-O2` IR 的巨大合并图中迷失，遇到无法消除的别名或指向时：
  * 工具向 Agent 请求“指路”。
  * Agent 下发预先计算好的语义锚点，或者动态告诉引擎：“强制将结点 A 和结点 B 认定为同一污点（续延断流）”，或者“剪掉这条不可能的路径（压制 FP）”。
* **最终验证**：观察加入了 Agent 之后，原本在 `-O2` 下迷失的 SVF，是否重新成功报出了该漏洞。

### 3. 量化收益 (Metrics)

* 记录在包含多个真实 CVE 的数据集上，Agent 将 **False Negatives (漏报) 降低了多少 %**，同时将因为状态爆炸导致的 **False Positives (误报) 限定在什么范围**。

---

## 阶段三：人工挖掘与筛选“黄金案例” (Hunting for Motivating Examples)

在进入大批量测试前，我们需要通过人工撒网，在真实 Target 中捞出最典型的“被 `-O2` 优化变瞎”的静态分析误报/漏报作为论文的 Motivating Example。

### 1. 打猎目标与约束

* **编译基准**：全程使用 `clang -O2 -g` 处理目标项目并生成 `.bc`，提取带调试信息的优化 IR。`clang -O0 -g` 仅用于基线对照，`clang -O2 -g -fno-inline` 用于 inline 因果隔离。
* **工具筛选**：只使用 IR 层面的静态分析/验证工具（如 `SVF`, `Phasar`, `IKOS`, `KLEE`, `SeaHorn`, `SMACK`）。源码层、前端层、规则匹配层工具不进入主实验矩阵。
* **核心动作**：使用工具最全、最深度的 Feature 套件（如开启全量 checkers / deep pointer analysis）跑一遍 Repo，只找那些**“一眼看过去反常识、违背人类基本逻辑”**的明显 False Positives (FP)。
* **行号漂移捕捉策略**：IKOS/SVF/SMACK 等 IR 工具报告中的行号来自 DWARF `-g` 调试信息。在 `clang -O2 -g` 下，DWARF 的 `DW_TAG_inlined_subroutine` 会记录 Inline 展开的原始位置，但工具输出的行号往往指向被内联函数的**原始定义处**而非调用处。因此，凡是"报告行号与源码真实上下文对不上"的 case，即为 Inline 导致的"时空错乱"高度疑似受害者，应优先标记并提取。

### 2. 识别“优化致傻”的四大特征定律 (FP Signatures)

为了快速从成千上万的 Warning 中锁定与 LLVM 优化相关的受害者，我们需过滤出满足以下特征的严重报错。在此之前，我们先通过下表直观对比 `-O2` 下各类优化对静态分析的直接破坏：

| 优化阶段 / Pass                                            | `-O2` 频次 | 触发条件 / 核心动作 (The "Grinder")                                                                           | 对静态分析的直接破坏 (Semantic Collapse)                                                                                                                      | 对应论文特征标签               |
| :--------------------------------------------------------- | :----------- | :------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------- |
| **Inlining** `<br>`(内联)                          | ✅ 极高      | 目标函数较小、带有 `static` / `inline` 属性、或优化成本模型计算认为收益高于阈值。                         | **调用边消失**：跨过程分析 (IPA) 降级为过程内分析；DWARF 行号错乱导致归因漂移；上下文敏感度 (Context-Sensitivity) 彻底被破坏。                          | 时空错乱 (Trace-loss)          |
| **Mem2Reg** `<br>`(内存转寄存器)                   | ✅ 必然      | 局部变量仅被 `load`/`store` 访问且没有被取地址 (`&`)，将其从栈内存 (`alloca`) 提升为 SSA 虚拟寄存器。 | **别名与状态爆炸**：引入海量 `Phi-node` 合并多条控制流的变量。分析引擎无法区分具体来源，只能过度近似化 (Over-approximation)，导致误报爆炸。           | 万物归一 (Phi-Node Disaster)   |
| **SROA** `<br>`(聚合体标量替换)                    | ✅ 必然      | 结构体 (`struct`) 或小数组在局部且字段/元素被独立访问，将其彻底打碎为独立的标量变量。                       | **结构边界与字段敏感度消失**：工具顺着打碎的单一标量分析内存偏移量时，丢失父辈结构体概念，极易爆出无厘头的越界或类型错配警告 (FP)。                     | 无厘头受害者 (Struct Mismatch) |
| **CFG Simplification** `<br>`(含 Jump Threading)   | ✅ 必然      | 存在空基本块、条件跳转两分支目标相同、或可通过上下文推断出分支走向必然性。合并/删除基本块。                   | **控制流/依赖链断裂**：原本阻断污点的 `if()` 清洗逻辑往往被折叠或消除，导致静态分析器直接“穿墙”连上 Sink点，产出不可达路径误报 (FP)。               | 神仙连线 (Broken Trust)        |
| **GVN / CSE** `<br>`(全局值编号/公用子表达式消除)  | ✅ 必然      | 代码中存在多处计算结果相同的表达式，将其合并，多处引用指向同一个虚拟寄存器。                                  | **数据流强制交汇**：本没有业务联系的两个独立变量，因为“值相等”被合并成一个 IR 节点。导致污点通路发生毫无逻辑的交叉感染 (FP/FN)。                      | 万物归一 (Shared State)        |
| **DCE / ADCE / DSE** `<br>`(各种死代码/死存储消除) | ✅ 必然      | 结果未使用、基于当前推断不可达的分支、或者被后续覆盖的无效内存写入。                                          | **漏洞节点直接蒸发**：如果漏洞触发了编译器的未定义行为 (UB) 假设，或者 Sink 点返回值未被使用，相关代码块会被整块抹除 (FN)。                             | 靶点消失 (Vanishing Node)      |
| **InstCombine** `<br>`(指令合并消除)               | ✅ 必然      | 局部的代数化简，例如将多次指针偏移 (`GetElementPtr`) 合并为一次，或位运算折叠。                             | **指针运算语义模糊化**：原本清晰的数组索引或由于宏展开带来的多级偏移，变成一个算术常量偏移，增加抽象解释 (IKOS) 重构区间域的难度。                      | 边界判定失效                   |
| **Tail-call Elim** `<br>`(尾调用消除)              | ⚠️ 常见    | 函数在 `return` 前的最后一步是调用另一个函数，且调用约定 (ABI) 允许复用当前栈帧。                           | **调用栈回溯断裂**：`call` 指令被优化为类似 `goto` 的直接跳转 (`br`/`jmp`)。依赖 Call-Return 匹配的下推自动机 (如 IFDS/Phasar) 会出现栈不匹配。 | 时空错乱 (Stack Mismatch)      |
| **LICM** `<br>`(循环不变量外提)                    | ⚠️ 常见    | 循环内部的某些计算在每次迭代中结果均不变，将其强行提拉到循环体外 (Preheader)。                                | **循环上下文剥离**：原本在循环内控制生命周期的指针被拉出后，分析引擎在判定生命周期 (如 Use-After-Free) 时容易产生范围误判。                             | 状态溢出                       |
| **Loop Unrolling** `<br>`(循环展开)                | ⚠️ 视成本  | 循环次数明确且较小，或为了增加并行度，将循环体复制多份拉平。                                                  | **CFG 急剧膨胀**：引发静态分析工具在遍历时的状态爆炸 (State Explosion) 甚至超时 (Timeout/Too-Complex)，强制提前终止分析。                               | 分析引擎崩溃 (Timeout)         |

* **特征 1：时空错乱 (The Inline Trace-loss)**

  * *肉眼表现*：工具报错称某文件 `A.c` 的第 100 行发生了空指针引用。但你去检查 `A.c` 第 100 行，发现那里**根本没有指针**，甚至连报错的变量名在当前函数作用域里都搜不到。
  * *病理*：发生了深度 `Inline`。指针原本存在于子函数里，被强行缝进了父函数，而 DWARF 行号映射直接紊乱。
* **特征 2：“万物归一” (The SSA Phi-Node Disaster)**

  * *肉眼表现*：同一个指针变量被标记为所有事情的罪魁祸首——既发生了 Memory Leak，又引发了 Use-After-Free，还造成了 Double-Free。
  * *病理*：发生了严重的寄存器复用和控制流化简（Mem2Reg + GVN）。多个不同生命周期的指针被 LLVM 强制合并成了一个巨大的 SSA Phi-Node（如 `%20 = phi [%a, bb1], [%b, bb2]`）。分析工具无法区分它们，只能进行 Over-approximation（过度近似抽象），直接导致状态/警报爆炸。
* **特征 3：神仙连线 (The Broken Taint Bridge)**

  * *肉眼表现*：工具信誓旦旦地说 `User_input` 畅通无阻地流进了 `memcpy` 的大小参数。但人工源码审计发现，这两者之间明明有一道极严格的长度校验 `if()` 拦截或者存在数据清洗。
  * *病理*：清洗逻辑在被 Inline 后，编译器认为“该条件在某种高度特定的路径下恒真/恒假”，触发了死代码消除，或者由于复杂的结构体拆分，静态分析器丢失了 Control-flow Dependency，直接“穿墙”连上了危险汇点（FP）。
* **特征 4：无厘头受害者 (SROA Struct Mismatch)**

  * *肉眼表现*：报数组极大越界或字段内存错乱，但该行仅仅是进行了一个最基础的结构体赋值操作（`struct A = struct B`）。
  * *病理*：Scalar Replacement of Aggregates (SROA) 把结构体彻底打碎成了松散排列的离散数组或者独立变量。静态分析工具顺着打碎的 IR 分析内存偏移量时彻底丧失了结构体边界概念，进而爆出了越界警告。

### 3. 操作指引 SOP

1. **从干净的项目开始**：优先在代码质量高、原生真漏洞少的目标（如 `leveldb`）上进行测试。扫出来的告警极大概率是工具由于“读不懂 O2 IR”而自寻烦恼产生的 FP。
2. **人工证伪**：不要被极具欺骗性的控制流绕进去。如果在某处报错，按照上述特征直接去看这一行，如果在代码常识理解内绝对站不住脚，直接记录：这极可能是优化造成的幻觉网络。
3. **提取入库**：选定最离谱的 1-2 条记录确切的 Source/Sink 行号，这便是我们将送给 LLM Agent 修复的“靶点”。

---

## 阶段四：IR 工具视角的差分矩阵 (The IR Differential Tool Matrix)

为了证明“结果变化是由 `clang -O2 -g` 生成的优化 IR 引起的”，而非单一工具偶然行为，我们建立一个只包含 IR 层工具的差分矩阵。

核心思想不是比较“源码工具 vs IR 工具”，而是在同一源码快照、同一 clang 版本、同一 IR 工具族上，比较 `-O0 -g`、`-O2 -g`、`-O2 -g -fno-inline` 三个 bitcode 宇宙的告警、路径、调用边和失败模式。

### 1. IR 分析工具层（主实验对象）

**代表工具**：**SVF**, **Phasar**, **IKOS**, **KLEE**, **SeaHorn**, **SMACK**

* **物理位置**：直接运行在 LLVM bitcode / LLVM IR / IR 派生验证表示之上。
* **可见内容**：它们面对的是被 Inline 拉平的函数、被 Mem2Reg 合并成 Phi-node 的变量、被 SROA 肢解的结构体、以及被 CFG Simplification 重写的控制流。
* **在实验中的核心作用**：
  * 作为**核心实验组**，重现 `clang -O2 -g` bitcode 上的分析灾难。
  * 验证在遭受“时空错乱”、“万物归一”等结构破坏后，指针分析、IFDS/IDE、抽象解释、符号执行、Horn 验证、Boogie 验证链分别如何发生**链路断层（漏报 FN）**或**过度抽象爆炸（误报 FP）**。
  * 通过多 IR 工具的一致性，证明问题来自优化 IR 语义形态，而非某一个工具的孤立 bug。

### 2. 神经符号修复验证层（Neuro-Symbolic Agent）

**代表组件**：**NeuroMap (LLM Agent 驱动的安全断点回连框架)**

* **操作流**：
  1. Agent 接收 `-O0 -g` IR 中较完整的路径、调用边、变量定义/使用关系作为参照。
  2. Agent 解析 `-O2 -g` `.bc/.ll` 中的优化后代码片段。
  3. 通过跨优化级别的模糊特征匹配，Agent 向下层分析引擎下发“强制连桥 (Assert Alias)”或“强行剪枝 (Prune Branch)”指令。
* **在实验中的核心作用**：验证加入大模型的辅助后，工具矩阵中因 `-O2` 导致的漏报和误报在多大程度上得到了消除，从而确立本论文在“优化感知分析 (Optimization-Aware Analysis)”领域的开创性地位。

---

## 执行总结：一套差分验证的快速循环

当你人工审阅出一条“反常识”的告警后，你需要闭环执行以下三个操作才能将其正式提拔为论文的靶点：

1. **看 IR 基线**：用 `clang -O0 -g` 的 `.bc/.ll` 与 IR 工具报告确认路径、调用边或告警在低优化 IR 中的形态。
2. **看 O2 灾变**：切到 `clang -O2 -g`，用同一 IR 工具重跑。如果在 `-O0 -g` 正常，在 `-O2 -g` 才变异出来（或消失），立刻捕获。因为这是 O2 优化改变了 IR 可见性。
3. **看 noinline 对照**：切到 `clang -O2 -g -fno-inline`，观察该 case 是否恢复。若恢复，优先归因 inline。
4. **上大模型**：利用 NeuroMap 提示词和 `-O0 -g` IR 参照，看看能否通过大模型干预 IR 工具，成功把它挽救回来。

---

## 人工判别静态扫描报告：完整注意事项与实操标准

这一部分是你“人工证伪/证真”的统一标准。目标不是证明工具“有报错”，而是判断：

1) 报错是否真实；2) 报错是否被错误归因；3) 是否与 `-O2`/inline 相关。

### A. 一条告警的标准审查流程（必须按顺序）

1. **定位原始告警**

   - 记录：工具名、规则ID/CWE、文件、行号、函数名、调用链摘要。
   - 若日志有重复条目，先去重，保留“最完整调用路径”的那条。
2. **行号与位置一致性检查（第一道门）**

   - 打开告警行，检查该行语句类型是否与漏洞类型匹配。
   - 典型异常：
     - 报“空指针解引用”，但该行根本没有指针解引用。
     - 报“越界访问”，但该行是普通赋值/注释/声明。
   - 结论：若类型与语句形态明显不一致，先标记为“**归因漂移可疑**”。
3. **最小可达路径检查（第二道门）**

   - 沿调用链回溯到最近的定义点（source）和使用点（sink）。
   - 检查是否有明确 guard：`if (ptr)`, 长度检查, 状态检查, 错误返回。
   - 若 guard 在所有可达路径上都成立，告警倾向误报。
4. **编译语义检查（第三道门，论文核心）**

   - 对比 `clang -O0 -g` vs `clang -O2 -g`（必要时 `clang -O2 -g -fno-inline`）：
     - `-O0 -g` 无告警，`-O2 -g` 出现告警：可能是优化引发误报。
     - `-O0 -g` 有路径，`-O2 -g` 路径断裂：可能是优化引发漏报。
   - 若 `-O2 -g -fno-inline` 可恢复，优先归因 inline。
5. **IR 工具交叉检查**

   - 多个 IR 工具在 `-O2 -g` 上出现同类漂移/消失/超时：增强优化归因可信度。
   - 只有单一工具异常，而其他 IR 工具均稳定：优先标记为工具特异性问题，暂不作为主 case。
6. **最终标签**

   - `TP`：真实漏洞；
   - `FP-TypeMismatch`：漏洞类型与代码语句不匹配；
   - `FP-PathInfeasible`：告警路径不可达；
   - `FP-LocationDrift`：行号/函数归因漂移；
   - `FN-O2`：`-O2` 下漏报；
   - `Unknown`：证据不足，暂挂。

### B. 你必须重点盯的“高危误报信号”

1. **行号漂移**：报错落在头文件构造函数/析构函数上，但真实风险点在调用处。
2. **类型-语句错配**：报空指针，代码行无指针；报越界，代码行无索引/指针算术。
3. **路径矛盾**：同一条路径中同时出现 `n==0` 与“进入 `for (i<n)` 循环体”。
4. **过度保守建模**：大量 “`operator new` 可能返回 NULL`” 一刀切告警。
5. **分析提前终止**：`-Wanalyzer-too-complex` 后续同函数的风险结论可信度下降。
6. **重复爆炸**：同一源点被多个相邻行重复报同类问题，常见于同一个抽象状态坍塌。

### C. 判别时必须避免的误区

1. **不要只看一行**：必须看最小上下文（至少函数级）。
2. **不要把“可疑”直接当“误报”**：必须有 guard/路径证据支撑。
3. **不要忽略编译选项**：没有 `-O0/-O2` 差分，不要写“优化导致”。
4. **不要忽略 C/C++ 语义差异**：
   - C++ `new`（非 `nothrow`）与 C `malloc` 的失败语义不同；
   - 这会直接影响空指针告警解释。
5. **不要忽略宏/模板内联**：告警位置可能在模板展开处，不等于真实根因点。

### D. 每条 case 必留证据（最小证据包）

对每个候选 case，至少保存以下信息：

1. 告警原文（含 CWE、规则、行号、调用链片段）；
2. 源码片段（告警行上下各 10–20 行）；
3. `clang -O0 -g`、`clang -O2 -g` 与 `clang -O2 -g -fno-inline` 的对比结果；
4. 其他 IR 工具是否支持同类差分现象；
5. 最终标签与一句话归因（例如：`FP-LocationDrift + inline`）。

### E. 人工复核记录模板（建议直接复制）

```text
[Case ID]
Tool:
Rule/CWE:
File:Line:
Claimed Bug Type:

1) 位置一致性：匹配 / 不匹配（理由）
2) 路径可达性：可达 / 不可达（关键 guard）
3) O0 vs O2：一致 / O2新增 / O2消失
4) O2-noinline：恢复 / 不恢复 / 未测
5) IR交叉工具：支持 / 不支持 / 未测

Final Label: TP / FP-TypeMismatch / FP-PathInfeasible / FP-LocationDrift / FN-O2 / Unknown
Root Cause Guess: inline / SSA merge / location mapping / analyzer complexity / other
```

### F. 何时可以判定“这是论文可用黄金 case”

满足以下至少 4 条即可入选：

1. 告警可稳定复现；
2. 人工审计能清晰证明“报错不合理”或“漏报明显”；
3. `-O0` 与 `-O2` 存在明确差分；
4. 至少两个 IR 工具或同一 IR 工具的不同模式能支持该差分现象；
5. 可归因到 inline/SSA/路径折叠中的至少一个机制。

---

## 阶段五：3 个编译宇宙 + 多种 IR 工具的批量扫描矩阵（主实验）

这一阶段把你前面所有策略收敛为可规模化执行的主实验框架：

### 1. 固定 3 个编译宇宙（必须统一）

1. **O0**：`clang -O0 -g`，结构语义基线。
2. **O2**：`clang -O2 -g`，本文主实验对象，Inline/Mem2Reg/SROA 等优化触发，同时保留 DWARF 调试信息。
3. **O2-noinline**：`clang -O2 -g -fno-inline`，inline 因果隔离组。

> 说明：三组都必须使用同一源码快照、同一编译器版本（clang-14）、同一构建/链接流程，仅改变 clang 优化开关。主实验不加入 `-DNDEBUG`。
>
> **为什么必须直接约束 clang flags**：
>
> 1. 本文研究问题是 `clang -O2 -g` 生成的 `.bc` 对 IR 工具的影响；`-DNDEBUG` 会改变宏展开和控制流，不属于主变量。
> 2. 若目标项目必须通过 CMake 构建，必须检查实际编译命令，确保 O2 宇宙实际为 `-O2 -g`。
> 3. DWARF 调试信息（`-g`）在 `-O2` 下的行号漂移（报告行号指向被内联函数定义处而非调用处），正是我们要捕捉的"时空错乱"特征。

完整 CMake 命令模板：

```bash
# O0 基线对照组
clang-14 -O0 -g -emit-llvm -c <input.c> -o <target>_O0_g.bc

# O2 主实验组
clang-14 -O2 -g -emit-llvm -c <input.c> -o <target>_O2_g.bc

# O2-noinline 因果隔离组
clang-14 -O2 -g -fno-inline -emit-llvm -c <input.c> -o <target>_O2_g_noinline.bc
```

### 2. 多 IR 工具分层（建议至少 5 个）

#### A. 核心组（必须）

- **SVF**：指针/值流图（VFG）
- **Phasar**：IFDS/IDE 跨过程数据流
- **IKOS**：抽象解释（区间/数值域）

#### B. 扩展组（强烈建议）

- **KLEE**：基于 LLVM bitcode 的符号执行（路径可达性变化）
- **SeaHorn**：基于 Horn clauses 的程序验证（可证明性差异）

#### C. 补充组（按资源选配）

- **SMACK**：LLVM IR 到 Boogie 的验证链
- **Crab-llvm**：LLVM 抽象解释框架
- **dg (LLVM Dependence Graph)**：依赖图/程序切片

### 3. 批量扫描输出（每个工具都要产出）

每个工具在 3 个编译宇宙下都输出统一格式结果（建议 CSV/JSON），至少包含：

1. `tool` / `target` / `universe`
2. `warning_id` / `cwe` / `file` / `line`
3. `bug_type` / `source` / `sink`（若有）
4. `path_length` / `call_edges`（若有）
5. `status`（reported / timeout / too-complex / unknown）

### 4. 主指标（论文核心图表）

1. **FN delta**：`O0 -> O2` 漏报变化。
2. **FP delta**：`O0 -> O2` 误报变化。
3. **Inline sensitivity**：`O2` 与 `O2 -fno-inline` 的恢复率差异。
4. **Analysis degradation**：`too-complex` / timeout 比例变化。
5. **Call graph collapse ratio**：调用边丢失比例（SVF/Phasar/KLEE 路径统计重点）。

### 5. 判因规则（统一）

当一个 case 同时满足以下条件时，可归因为 inline 主导：

1. `-O0` 可见，`-O2` 消失或扭曲；
2. `-O2 -fno-inline` 恢复（全部或部分）；
3. 对应调用边/中继节点在 IR 图中出现折叠或消失；
4. 其他 IR 工具或同一工具的 `-O0 -g` 参照支持原始路径存在。

### 6. 推荐执行优先级（省时版）

1. 先跑 `SVF + Phasar + IKOS` 于 `leveldb`（快速得到第一批差分）。
2. 在同一 target 上补 `KLEE` 或 `SeaHorn`（增加方法多样性）。
3. 复用流水线扩展到 `curl`，提炼 5–10 个黄金 case。

### 7. 最终交付物（必须落盘）

1. `raw_logs/`：各工具原始日志。
2. `normalized_reports/`：统一字段的标准化结果。
3. `diff_reports/`：`O0 vs O2`、`O2 vs O2-noinline` 差分结果。
4. `casebook/`：人工复核通过的黄金 case（含证据包）。

> 核心目标不是“谁报得多”，而是量化“同一漏洞在不同编译语义宇宙中的可见性变化”，并将变化机制归因到 inline/SSA/图折叠。

---

## 阶段六：IR 工具全景表（本文主实验工具）

这一节统一回答：本文只使用哪些 IR 层面的工具来研究 `clang -O2 -g` 生成的 `.bc` 对静态扫描/验证结果的影响。源码层、前端层、规则匹配层、SCA/供应链、平台治理类工具不进入主实验矩阵。

### 1. 总体原则

1. **只纳入直接消费 LLVM bitcode/LLVM IR 或 IR 派生验证表示的工具**。
2. **所有工具都在同一组三宇宙上运行**：`clang -O0 -g`、`clang -O2 -g`、`clang -O2 -g -fno-inline`。
3. **主变量只有优化级别与 inline 控制**。主实验不加入 `-DNDEBUG`。
4. **论文证据来自 IR 工具内部差分与 IR 工具之间的交叉一致性**，而不是源码工具对照。

### 2. IR 工具矩阵

| 工具 | 主要语义层 | 输入 | 关注指标 | 论文角色 |
| ---- | ---------- | ---- | -------- | -------- |
| SVF | LLVM IR 指针/值流图 | `.bc`/`.ll` | VFG 连通性、别名、调用边 | 核心主战场 |
| Phasar | LLVM IR IFDS/IDE 数据流 | `.bc` | source-sink 路径、调用上下文、行号漂移 | 核心主战场 |
| IKOS | LLVM IR 抽象解释 | `.bc` | 数值域、内存安全告警、超时/unknown | 核心主战场 |
| KLEE | LLVM bitcode 符号执行 | `.bc` | 路径可达性、约束变化、路径爆炸 | 扩展验证 |
| SeaHorn | LLVM IR Horn-clause 验证 | `.bc`/`.ll` | 可证明性、反例、unknown | 扩展验证 |
| SMACK | LLVM IR 到 Boogie 验证链 | `.bc` | translation、Boogie/Corral 结果、错误轨迹 | 扩展验证 |

### 3. 论文中的推荐使用方式

1. **主证据链（必须）**：`SVF + Phasar + IKOS`，在 `O0/O2/O2-fno-inline` 三宇宙做差分。
2. **补强证据（建议）**：`KLEE/SeaHorn/SMACK` 至少选 1-2 个，证明不是单一算法特例。
3. **统一结论口径**：`-O0 -g` 负责提供低优化 IR 参照，`-O2 -g` 负责暴露优化后 IR 工具退化，`-O2 -g -fno-inline` 负责 inline 因果隔离。

### 4. 已执行的 O2 产物扫描（用于论文 case）

基于当前环境可复现链路，已使用 **PhASAR（LLVM IR）** 对 O2 产物进行扫描并完成跨宇宙统计（O0 / O2 / O2-noinline）：

> 注意：以下是已有历史实验路径。目录名中若包含 `RelWithDebInfo`，正式纳入论文前必须回查对应 `compile_commands.json`、构建日志或 bitcode 生成命令，确认实际主实验 flags 是否为 `clang -O2 -g`，而不是隐式加入了额外宏定义。

1. 原始 casebook：
   - `CompilerOptimization/Result/leveldb/phasar/phasar_O0_DebInfo/runs/ifds-uninit_nosan/leveldb_O0_DebInfo-Wed-Mar-11-06:56:33-2026/casebook_inline_candidates.csv`
   - `CompilerOptimization/Result/leveldb/phasar/phasar_O2_RelWithDebInfo/runs/ifds-uninit/leveldb_O2_RelWithDebInfo-Mon-Mar--9-14:43:49-2026/casebook_inline_candidates.csv`
   - `CompilerOptimization/Result/leveldb/phasar/phasar_O2_noinline_RelWithDebInfo/runs/ifds-uninit/leveldb_O2_noinline_RelWithDebInfo-Wed-Mar-11-07:18:26-2026/casebook_inline_candidates.csv`
2. 汇总结果（新增）：
   - `CompilerOptimization/Result/leveldb/phasar/paper_case_scan_summary.json`
3. 论文优先 case 列表（新增）：
   - `CompilerOptimization/Result/leveldb/phasar/phasar_O2_RelWithDebInfo/runs/ifds-uninit/leveldb_O2_RelWithDebInfo-Mon-Mar--9-14:43:49-2026/paper_focus_cases_top20.csv`
4. 本轮补跑（新增，直接扫描 O2 产物）：
   - `CompilerOptimization/Result/leveldb/phasar/phasar_O2_RelWithDebInfo/runs/ifds-uninit_audit_rerun/leveldb_O2_RelWithDebInfo-Thu-Mar-12-05:50:08-2026/psr-report.txt`
   - `Total uses of uninitialized variables: 3479`

当前结论：

- O2 是唯一出现大量 `inline_depth>0` 与 `drift` 的宇宙（`drift=1548/2713`）。
- O0 与 O2-noinline 在报告级几乎全部 `inline_depth=0`，可作为因果对照基线。
