# 顶会系统安全论文写作思路：从“发现问题”到“LLM Neuro-Symbolic 神经符号修复”

这篇论文的叙事逻辑已经完成了从“Measurement (纯测量评估)”向“System / Solution (系统级创新解决)”的华丽升级。以下是每一章节的核心目的与写作逻辑。

---

## 1. Introduction (引言)
*   **The Status Quo (现状)**: 静态安全分析依赖中间表示 (IR)，默认编译器如实传递了代码的语义结构（如函数边界、变量别名）。
*   **The Unseen Threat (未见之威胁)**: 但编译器 `-O2` (Inline, Mem2Reg, SROA) 实际上是以“破坏结构”为代价来换取性能。
*   **The Problem (核心问题)**: 这种由于优化导致的“语义坍塌 (Semantic Collapse)”，严重破坏了静态代码分析赖以生存的数据流图，导致原本能扫出来的漏洞在 `clang -O2 -g` 生成的优化 IR 下消失了 (False Negatives)，或者引发路径爆炸 (False Positives)。
*   **The Challenge (修复挑战)**: 传统的编译器 Debug 信息表 (DWARF) 在 `-O2` 下早已支离破碎，无法用于修复跨函数的复杂污点流。
*   **Our Solution (我们的星辰大海)**: 提出 \textbf{NeuroMap}，首个由 LLM Agent 驱动的优化感知静态分析框架。利用 LLM 跨越大跨度空间的模糊语义对齐能力，找回丢失的节点，引导传统算法重归正轨。
*   **Key Contributions (贡献)**。

## 2. Motivation / Background (动机与背景)
*   **背景知识**: 简述什么是 Taint Analysis（污点分析），为什么它依赖 Call Graph 和 Memory Alias。
*   **The Motivating Example (黄金案例)**: 拿咱们在 `curl` (或 `leveldb`) 中找到的真实断联 CVE 作为贯穿全文的故事主线。
    *   展示这段 C 语言源码。
    *   展示它在 `-O0` 下清晰的 Call graph 和污点通路（SVF抓住了没问题）。
    *   展示它在 `-O2` 下，因为 `Inline + Phi-Node merging`，变成了一团面条代码，导致 SVF 直接 False Negative。
    *   **灵魂发问**: DWARF 烂了，常规手段寄了，谁能来一眼看穿这段烂成面条的 IR 对应的是源码哪个业务意图呢？引出 LLM。

## 3. Methodology & Design: The NeuroMap Framework (核心方法论与架构设计)
这是论文的“Muscle (肌肉)”，详细讲解 LLM Agent 是怎么跟传统符号引擎 (Symbolic Engine, 即 SVF/Phasar) 贴身肉搏的。
*   **Phase 0: The IR Differential Tool Matrix (IR 差分工具矩阵)**: 论文只使用 IR 层静态分析/验证工具作为主实验对象，例如 SVF、Phasar、IKOS、KLEE、SeaHorn、SMACK。核心不是比较源码工具和 IR 工具，而是在同一 IR 工具上比较 `clang -O0 -g`、`clang -O2 -g`、`clang -O2 -g -fno-inline` 三个 bitcode 宇宙的结果差异。
*   **Phase 1: IR Evidence Extraction (IR 证据提取)**: 从各 IR 工具报告中提取 Source/Sink、告警类型、路径、调用边、行号、超时/失败状态，以及 `.bc/.ll` 中对应的优化痕迹。
*   **Phase 2: Cross-Optimization Fuzzy Alignment (跨优化级别模糊对齐)**: 描述 Agent 如何利用 `-O0 -g` 中较完整的 IR 结构作为参照，将高层安全意图和路径锚定到 `-O2 -g` 中被 Inline、Mem2Reg、SROA 打散的虚拟寄存器（如 `%45 = phi...`）里。
*   **Phase 3: Agent-Guided Analysis (代理引导的底层图遍历)**: Neuro-Symbolic 的最高光时刻。底层静态引擎遍历图走到“断桥”时，触发回调 (Callback)，Agent 基于第二步的锚点，强行向底层引擎下达“焊死别名 (Assert Alias)”指令，重铸污点流。

## 4. Evaluation / Experiment (实验评估)
分为三个层面来秀肌肉。
*   **RQ1: The Scale of Semantic Collapse (病有多深)**: 用 `clang -O0 -g`、`clang -O2 -g`、`clang -O2 -g -fno-inline` 三个 bitcode 宇宙，在四大 Target (curl, redis, grpc, leveldb) 上量化证明在没有 Agent 介入时，O2 让多少 True Positives 变成了瞎子 (FNs)。证明问题足够大。
*   **RQ2: Recovery Efficacy (药有多灵)**: 引入 Agent 后，原来在 O2 中瞎眼的 100 个 CVE 中，Agent 成功续命 / 抢救回来了多少个？（Recall 提升了多少）。
*   **RQ3: Precision Maintenance (副作用控制)**: 证明在 Neuro-Symbolic 限定框架下，Agent 没引发大面积的过度近似幻觉，没有引起疯狂的 False Positives 上升（Precision 稳住）。

## 5. Case Studies (案例分析)
*   从 `curl` 和 `leveldb` 中挑两个最精彩的、连 DWARF 人类专家都看不懂的重度优化灾难。详细展示：在没有 Agent 时断在哪里，Agent 根据什么奇妙的特征强行推断出了这两个虚拟寄存器是同一污点，最后成功报出。

## 6. Discussion & Future Work (讨论与展望)
*   **对 IR/二进制级安全分析的启示**: 讨论只依赖未优化或低优化 IR 得出的结论，无法代表 `clang -O2 -g` bitcode 上静态工具真实面对的语义形态。系统需要优化感知的差分证据与恢复机制。
*   讨论 LLM 上下文窗口限制对大型 IR 的影响。
