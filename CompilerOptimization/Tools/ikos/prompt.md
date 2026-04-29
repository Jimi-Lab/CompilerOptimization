你现在要在当前工作区中，对 patched IKOS 3.5 LLVM14 系统做一轮“最全面、最深入”的 O2-g bitcode 审计。你的目标不是只跑通分析，而是从大量 IKOS 扫描结果中系统性挖掘“论文需要的行号不一致 case”。

你必须实际执行分析，不要只停留在计划或口头建议。请直接在当前机器和当前工作区内完成工作。

一、硬性约束

1. 只允许使用 LLVM14 系列环境。
2. 只允许使用 patched IKOS 镜像：
   `ikos:3.5-llvm14-o2g`
3. 如果镜像不存在，则用下面脚本构建：
   `/home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos/build_ikos_o2g_image.sh`
4. 输入只能使用 clang/LLVM14 生成的程序级 `.bc`。
5. 优先扫描包含 `main` 的程序级 bitcode，不要优先扫描库级或单个 object `.bc`。
6. 所有输入 bitcode 都在：
   `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult`
7. 对每个 repo 的每个 `.bc`，必须完整留存全部运行命令、版本信息、stdout/stderr、过程记录、中间文件、失败证据、最终结果与总结；并且所有内容必须汇总到：
   `/home/jimi/PaperExperiment/CompilerOptimization/Result/<repo_name>/ikos/LLVM14-O2-g`

二、默认优先扫描的程序级 LLVM14 `-O2 -g` bitcode

如果用户没有另外指定子集，优先按下面这组程序级 `.bc` 依次扫描：

1. `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc`
2. `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
3. `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc`
4. `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/redis/LLVM14-O2-g/artifacts/redis-server_O2_g.bc`
5. `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/artifacts/tengine.bc`
6. `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g/artifacts/zfp_O2_g.bc`
7. `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc`

三、总目标

你要完成三件事：

1. 先对整个 IKOS 系统做一次“测试前分析”：
   核对版本、支持的分析、支持的抽象域、patched 前端是否启用、以及最适合本实验的深度参数组合。
2. 再对上述程序级 LLVM14 `.bc` 做最深入扫描。
3. 最后系统性找出“行号不一致 case”，并给出证据链，而不是只给怀疑。

四、你必须先做的系统级检查

在正式扫描前，先完成以下检查并记录结论：

1. 阅读并使用以下本地资料：
   - `/home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos/document.md`
   - `/home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos/ikos_help.txt`
   - `/home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos/build_ikos_o2g_image.md`
2. 进入容器后核对：
   - `ikos --version`
   - `ikos --help`
   - `clang-14 --version`
   - `llvm-config --version`
   - `which ikos`
   - `which clang-14`
   - `which llvm-config`
3. 明确记录：
   - IKOS 是否真的是 3.5
   - 容器内是否真的是 LLVM 14
   - `ikos --help` 中可用的 analyses 列表
   - `ikos --help` 中可用的 domains 列表
4. 在所有可用 domain 中，选择“最强但可运行”的 domain，并给出选择理由。

五、domain 选择策略

不要想当然固定一个 domain。先检查容器内真实支持情况，然后按下面优先级选择最强可用项：

1. `var-pack-apron-pkgrid-polyhedra-lin-cong`
2. `var-pack-apron-polka-polyhedra`
3. `var-pack-apron-ppl-polyhedra`
4. `var-pack-dbm-congruence`
5. `gauge-interval-congruence`
6. `interval-congruence`
7. `interval`

要求：

1. 主扫描优先用“最强可用 domain”。
2. 如果主扫描超时、OOM、或无法完成，则保留失败证据，并降一级 domain 继续。
3. 对已经发现的疑似“行号不一致 case”，至少再用一个较稳健的 fallback domain 复核一次，确认该 case 不是单纯 domain 偶然现象。

六、analyses 选择策略

使用尽可能全面的 IKOS checks。默认不要只用内置默认分析集。

优先使用这组 analyses：

`boa,dbz,nullity,prover,upa,uva,sio,uio,shc,poa,pcmp,sound,fca,dca,dfa`

说明：

1. 这是覆盖面更完整的安全相关分析组合。
2. `dbg` 和 `watch` 不是本次论文找 case 的主力分析，除非你确认它们能提供额外证据，否则不要把时间浪费在无关噪音上。

七、深度扫描模式

对每个程序级 `.bc`，先做一次“主深扫”，参数原则如下：

1. `--proc inter`
2. `--globals-init all`
3. `--opt aggressive`
4. `--inline-all`
5. `--partitioning return`
6. `--widening-strategy widen`
7. `--widening-delay 2`
8. `--widening-period 1`
9. `--narrowing-strategy narrow`
10. `--narrowing-iterations 2`
11. 保持 pointer analysis、liveness、widening hints、fixpoint cache 默认开启
12. `--status-filter='*'`
13. `--report-verbosity 4`
14. `--display-times full`
15. `--display-summary full`
16. `--save-temps`
17. `--generate-dot`

主深扫的主要目标是：

1. 产出完整 output db
2. 产出可机读的 report
3. 保留 IKOS 前处理后的中间文件
4. 为后续行号审计保留证据

八、建议的主扫描命令模板

你可以按下面模板执行，但允许你根据容器实际能力小幅调整：

```bash
ikos "$BC" \
  -o "$OUT/output.db" \
  -a boa,dbz,nullity,prover,upa,uva,sio,uio,shc,poa,pcmp,sound,fca,dca,dfa \
  -d "$DOMAIN" \
  -e main \
  --globals-init all \
  --proc inter \
  --opt aggressive \
  --inline-all \
  --partitioning return \
  --widening-strategy widen \
  --widening-delay 2 \
  --widening-period 1 \
  --narrowing-strategy narrow \
  --narrowing-iterations 2 \
  --save-temps \
  --temp-dir "$OUT/temp" \
  --generate-dot \
  --generate-dot-dir "$OUT/dot" \
  --display-times full \
  --display-summary full \
  --status-filter='*' \
  --report-verbosity 4 \
  -f json \
  --report-file "$OUT/report.json"
```

如果你需要一份更便于快速筛表格的结果，再补一轮：

```bash
ikos "$BC" \
  -o "$OUT/output.db" \
  -a boa,dbz,nullity,prover,upa,uva,sio,uio,shc,poa,pcmp,sound,fca,dca,dfa \
  -d "$DOMAIN" \
  -e main \
  --globals-init all \
  --proc inter \
  --opt aggressive \
  --inline-all \
  --partitioning return \
  --widening-strategy widen \
  --widening-delay 2 \
  --widening-period 1 \
  --narrowing-strategy narrow \
  --narrowing-iterations 2 \
  --save-temps \
  --temp-dir "$OUT/temp" \
  --generate-dot \
  --generate-dot-dir "$OUT/dot" \
  --display-times full \
  --display-summary full \
  --status-filter='*' \
  --report-verbosity 4 \
  -f csv \
  --report-file "$OUT/report.csv"
```

九、输出目录规范

不要把所有 repo 的结果混写到一个公共目录。必须按 repo 分开落盘。

对于输入路径：

`/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/<repo_name>/LLVM14-O2-g/artifacts/<bc_name>.bc`

对应输出根目录固定为：

`/home/jimi/PaperExperiment/CompilerOptimization/Result/<repo_name>/ikos/LLVM14-O2-g`

你必须先从输入 `.bc` 路径中准确提取 `repo_name`，不要手写猜测。

每个 `.bc` 单独一个目录，格式建议：

`<repo_out>/<bc_stem>/run_<YYYYmmdd_HHMMSS>/`

其中：

1. `<repo_out>` = `/home/jimi/PaperExperiment/CompilerOptimization/Result/<repo_name>/ikos/LLVM14-O2-g`
2. `<bc_stem>` = 对应 `.bc` 文件名去掉扩展名后的稳定名称
3. 同一个 `.bc` 的不同 rerun、不同 domain fallback、不同定点复核，都必须放在该 `.bc` 目录下的独立 `run_<timestamp>` 子目录中

每个 run 开始前，就要先创建目录并初始化留痕文件。不要跑完以后再补写。

每个 run 目录至少包含：

1. `command.txt`
2. `env.txt`
3. `process.md`
4. `run_summary.md`
5. `report.json`
6. `report.csv`（如果生成）
7. `output.db`
8. `stdout.log`
9. `stderr.log`
10. `temp/`
11. `dot/`
12. `source_audit/`
13. `mismatch_cases.md`
14. `mismatch_cases.csv`

强制要求如下：

1. `command.txt` 必须按时间顺序记录该 run 的所有命令，包含：
   - docker 启动命令
   - `ikos` 主扫描命令
   - fallback domain rerun 命令
   - 定点复核命令
   - 与 `llvm-dis`、`sqlite3`、`rg`、`sed` 等证据提取相关的辅助命令
2. `command.txt` 中每条命令都要附带：
   - 开始时间
   - 结束时间
   - 返回码
   - 命令用途说明
3. `env.txt` 必须记录：
   - `ikos --version`
   - `ikos --help` 中实际可用 analyses 与 domains 的结论
   - `clang-14 --version`
   - `llvm-config --version`
   - `which ikos`
   - `which clang-14`
   - `which llvm-config`
   - docker image 名称
4. `process.md` 必须记录该 run 的执行过程：
   - 为什么选择当前 domain
   - 是否发生 timeout、OOM、tool failure、translation failure
   - 为什么触发 rerun 或降级
   - 当前 run 解决了什么问题、留下了什么未解决问题
5. `stdout.log` 和 `stderr.log` 必须保留完整原始输出。即使失败也不能丢。
6. `temp/`、`dot/`、`output.db`、`report.json`、`report.csv` 只要生成出来，就必须全部留存。
7. 对于失败 run，也必须保留失败证据，不允许只保留最后一次成功 run。

除每个 run 目录外，每个 repo 的输出根目录还必须维护：

1. `repo_summary.md`
2. `repo_summary.csv`
3. `repo_inventory.md`

要求：

1. `repo_summary.md` 汇总该 repo 下所有 `.bc` 的测试结论、发现的可疑 case、失败类型和后续建议。
2. `repo_summary.csv` 以表格形式汇总所有 `.bc` 的状态、domain、主要结果、case 数量、关键输出目录。
3. `repo_inventory.md` 列出该 repo 下已经扫描过的全部 `.bc`、对应 run 目录、是否有 rerun、是否完成行号审计。

十、如何定义“行号不一致 case”

不要模糊判断。你必须用证据来判定。以下情况都算候选 case：

1. IKOS 最终 report 里的 `file:line[:column]` 与对应 LLVM IR 指令的 `!dbg` 行号不一致。
2. IKOS report 中的行号落在一个明显无关的源码行，而真正相关的源码操作在附近其他行。
3. 同一个逻辑问题在 IKOS 的不同输出层级中出现位置不一致，例如：
   - report.json
   - output.db 内部定位
   - 原始 `.ll`
   - 预处理后的 `.pp.ll` 或等价临时 IR
4. 同一个告警在不同 domain 或不同扫描配置下，逻辑上是同一问题，但定位到了不同源码行。
5. 定位到空行、注释行、宏展开后不合理行、或不应成为主定位点的包装行。

十一、你必须建立的证据链

对每个疑似 case，至少给出下面证据：

1. 原始 IKOS 报告条目
2. 对应 check 类型与 status
3. 目标源文件路径
4. 报告行号附近的源码片段，至少上下文各 5 行
5. 原始 LLVM IR 中对应指令及其 `!dbg`
6. IKOS 预处理后 LLVM IR 中对应指令及其 `!dbg`
7. 如有必要，AR 或 raw checks 侧证
8. 你对“为什么这是行号不一致”的解释
9. 你认为“更合理的真实行号”是多少
10. 置信度分级：`high` / `medium` / `low`

十二、建议的审计步骤

请按下面顺序工作，不要跳步：

1. 先确认每个目标 `.bc` 是否包含 `main`
2. 先跑一轮主深扫
3. 把 `report.json` / `report.csv` / `output.db` 全部收集起来
4. 优先筛选 `error`、`warning`、`unreachable`
5. 再按 source file 聚类
6. 对每个可疑结果去追：
   - 原始 `.bc` 反汇编后的 `.ll`
   - IKOS temp 中的 `.pp.bc` / `.pp.ll`
   - 相关源码
   - 必要时 `output.db` 内部表
7. 如果只靠最终 report 看不出来，就做“定点复核 rerun”

十三、定点复核 rerun

当你锁定可疑 case 后，可以额外做一轮更吵但更深入的定点复核。只对可疑 case 做，不要对所有大程序无脑开最大日志。

可用于定点复核的选项包括：

1. `--display-llvm`
2. `--display-ar`
3. `--display-checks all`
4. `--display-inv fail`
5. `--display-raw-checks`
6. `--trace-ar-stmts`

如果输出太大，可以：

1. 只针对一个目标 `.bc`
2. 只保留定点函数相关片段
3. 只提取可疑文件/函数的证据

十四、数据库审计要求

不要只看人类可读 report。还要审计 `output.db`。

至少做到：

1. 检查数据库 schema
2. 确认与 location、statement、check、file、function、call context 相关的表
3. 把最终 report 中的可疑条目和 DB 中的记录对应起来
4. 判断“错误发生在报告渲染阶段”还是“更早就已经在 IR/AR/DB 阶段定位偏了”

十五、最终输出要求

你最终必须给出两层输出，且都必须落在各自 repo 的固定结果路径下：

1. 每个 `.bc` 单独一套完整测试档案：
   - `command.txt`
   - `env.txt`
   - `process.md`
   - `run_summary.md`
   - `stdout.log`
   - `stderr.log`
   - `report.json`
   - `report.csv`（如果生成）
   - `output.db`
   - `temp/`
   - `dot/`
   - `source_audit/`
   - `mismatch_cases.md`
   - `mismatch_cases.csv`
2. 每个 repo 单独一份总汇总，固定写到：
   `/home/jimi/PaperExperiment/CompilerOptimization/Result/<repo_name>/ikos/LLVM14-O2-g`
   其中至少包含：
   - `repo_summary.md`
   - `repo_summary.csv`
   - `repo_inventory.md`

如果一次任务覆盖多个 repo，可以额外再生成跨 repo 总表；但这只是附加汇总，不能替代每个 repo 自己目录下的完整归档。

`repo_summary.csv` 或跨 repo 总表至少包含这些列：

1. `program`
2. `repo_name`
3. `bc_path`
4. `status`
5. `analysis/check`
6. `reported_file`
7. `reported_line`
8. `suspected_true_line`
9. `function`
10. `mismatch_type`
11. `confidence`
12. `evidence_dir`

十六、排序优先级

请优先报告以下 case：

1. 置信度高
2. 与论文主题最相关
3. 不是 trivial 的宏/注释误差
4. 能明确给出“报告行号”和“更合理真实行号”
5. 有完整证据链

十七、非常重要的执行原则

1. 不要只给建议，必须实际运行。
2. 不要只找一个 case，就停止。
3. 不要只看最终 report，而忽略 `output.db`、原始 `.ll`、预处理 `.ll`。
4. 不要混入 LLVM13 或其他非 LLVM14 输入。
5. 不要把没有 `main` 的库级 `.bc` 当成首要程序级测试对象。
6. 如果某个程序太大、太慢，允许降级 domain，但必须保留降级理由和失败证据。
7. 如果发现 flatbuffers 这类目标已经能形成高质量 case，优先把该 case 做深做透。

十八、回答风格

每完成一个目标程序，请给出：

1. 是否跑通
2. 使用的 domain
3. 主要统计结果
4. 是否发现可疑行号不一致
5. 证据是否充分
6. 是否建议继续深挖

最后，请给出一个总判断：

1. 哪些程序最可能产出论文可用 case
2. 哪些 case 最强
3. 哪些只是弱怀疑
4. 下一步最值得继续深挖哪一个目标程序
