你现在要在当前工作区内，对一个现成的 LLVM14 `-O2 -g` 程序级 `.bc` 做一次 IKOS 单目标深度审计。目标不是只跑通，而是围绕这一个 `.bc` 系统性挖掘“行号不一致 case”，并把全部命令、日志、过程、结果和证据完整留存。

只允许分析这一个 `.bc`。不要扩展到其他 repo、其他 `.bc`、或整个矩阵。

一、先填写本次唯一目标

1. `{{BC_PATH}}`
   `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc`
2. `{{OUT_DIR}}`
   `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/ikos/LLVM14-O2-g/run_20260425`

建议：

1. `{{BC_PATH}}` 使用 clang/LLVM14 生成的程序级 `.bc`，且优先包含 `main`
2. `{{OUT_DIR}}` 使用：
   `/home/jimi/PaperExperiment/CompilerOptimization/Result/<repo_name>/ikos/LLVM14-O2-g/<bc_stem>/run_<YYYYmmdd_HHMMSS>`



二、硬性约束

1. 只允许使用 LLVM14 环境
2. 只允许使用 patched 镜像 `ikos:3.5-llvm14-o2g`
3. 如果镜像不存在，用：
   `/home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos/build_ikos_o2g_image.sh`
4. 本任务只允许使用 `ikos` 和 `ikos-report`
5. 不要使用 `ikos-scan`
6. 不要混入 LLVM13 或其他非 LLVM14 输入
7. 所有输出都只写入 `{{OUT_DIR}}`

三、执行顺序

1. 先做环境与输入检查
2. 选择最强可运行 domain
3. 对 `{{BC_PATH}}` 跑一次主深扫，生成 `output.db` 和 `report.json`
4. 基于同一个 `output.db` 导出 `report.csv`
5. 审计 `report.json`、`report.csv`、`output.db`、原始 `.ll`、IKOS 预处理后的 `.pp.ll`
6. 对可疑结果做定点复核
7. 在 `{{OUT_DIR}}` 中写完完整归档与总结

四、开始前必须检查

先阅读并使用这些本地资料：

1. `/home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos/document.md`
2. `/home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos/ikos_help.txt`
3. `/home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos/build_ikos_o2g_image.md`

进入容器后至少记录：

1. `ikos --version`
2. `ikos --help`
3. `ikos-report --help`
4. `clang-14 --version`
5. `llvm-config --version`
6. `which ikos`
7. `which ikos-report`
8. `which clang-14`
9. `which llvm-config`

另外必须确认：

1. `{{BC_PATH}}` 存在
2. `{{BC_PATH}}` 可反汇编
3. `{{BC_PATH}}` 是否包含 `main`
4. `ikos-report` 是否可用

五、domain 与 analyses

优先按下面顺序选择最强可运行 domain：

1. `var-pack-apron-pkgrid-polyhedra-lin-cong`
2. `var-pack-apron-polka-polyhedra`
3. `var-pack-apron-ppl-polyhedra`
4. `var-pack-dbm-congruence`
5. `gauge-interval-congruence`
6. `interval-congruence`
7. `interval`

要求：

1. 主扫描优先用最强可运行项
2. 如果 timeout、OOM、tool failure、translation failure，必须保留失败证据并降级
3. 对已经锁定的疑似 case，至少再用一个更稳健的 fallback domain 复核一次

默认 analyses 使用：

`boa,dbz,nullity,prover,upa,uva,sio,uio,shc,poa,pcmp,sound,fca,dca,dfa`

六、深度扫描模式

对 `{{BC_PATH}}` 先做一次“主深扫”，参数原则如下：

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

1. 产出完整 `output.db`
2. 产出可机读的 `report.json`
3. 固定基于同一个 `output.db` 导出 `report.csv`
4. 保留 IKOS 前处理后的中间文件
5. 为后续行号审计保留证据

七、主扫描命令

不要为了生成 `csv` 再重跑一遍完整 `ikos` 分析。固定流程是：

1. 一次 `ikos` 主扫描
2. 一次 `ikos-report` 报告导出

主扫描模板：

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

报告导出模板：

```bash
ikos-report "$OUT/output.db" \
  -f csv \
  --status-filter='*' \
  --report-verbosity 4 \
  --report-file "$OUT/report.csv"
```

只有在 `ikos-report` 不可用或 `output.db` 无法导出时，才允许做 CSV fallback；并且必须在 `process.md` 中写明原因。

八、定点复核

锁定可疑 case 后，再按需做定点复核。不要对整个程序无脑开最大日志。

可选复核选项：

1. `--display-llvm`
2. `--display-ar`
3. `--display-checks all`
4. `--display-inv fail`
5. `--display-raw-checks`
6. `--trace-ar-stmts`

九、输出目录规范

本次任务只使用一个输出目录：

`{{OUT_DIR}}`

你必须在开始执行前创建该目录，并确保所有与本次 `{{BC_PATH}}` 相关的内容都只写到这里，不要分散到其他公共目录。

`{{OUT_DIR}}` 至少包含：

1. `command.txt`
2. `env.txt`
3. `process.md`
4. `run_summary.md`
5. `report.json`
6. `report.csv`
7. `output.db`
8. `stdout.log`
9. `stderr.log`
10. `temp/`
11. `dot/`
12. `source_audit/`
13. `mismatch_cases.md`
14. `mismatch_cases.csv`

强制要求如下：

1. `command.txt` 必须按时间顺序记录本次这个 `.bc` 的所有命令，包含：
   - docker 启动命令
   - `ikos` 主扫描命令
   - `ikos-report` 导出命令
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
   - `ikos-report --help` 是否可用
   - `clang-14 --version`
   - `llvm-config --version`
   - `which ikos`
   - `which ikos-report`
   - `which clang-14`
   - `which llvm-config`
   - docker image 名称
   - 本次使用的 `{{BC_PATH}}`
   - 本次使用的 `{{OUT_DIR}}`
4. `process.md` 必须记录执行过程：
   - 为什么选择当前 domain
   - 是否发生 timeout、OOM、tool failure、translation failure
   - 为什么触发 rerun 或降级
   - 当前 run 解决了什么问题、留下了什么未解决问题
5. `stdout.log` 和 `stderr.log` 必须保留完整原始输出。即使失败也不能丢
6. `temp/`、`dot/`、`output.db`、`report.json`、`report.csv` 只要生成出来，就必须全部留存
7. 如果主扫描失败，也必须保留失败证据，不允许只保留最后一次成功 run

十、如何判定“行号不一致 case”

以下都算候选：

1. `report` 中的 `file:line[:column]` 与对应 LLVM IR 指令的 `!dbg` 行号不一致
2. report 行号落在明显无关的源码行，但真实相关操作在附近其他行
3. 同一问题在 `report.json`、`output.db`、原始 `.ll`、预处理 `.pp.ll` 之间定位不一致
4. 同一逻辑问题在不同 domain 或不同配置下定位到不同源码行
5. 定位到空行、注释行、宏包装行或明显不合理的位置

十一、每个可疑 case 必须保留的证据

1. 原始 IKOS 报告条目
2. check 类型与 status
3. 目标源文件路径
4. 报告行号附近源码，至少上下文各 5 行
5. 原始 LLVM IR 对应指令及 `!dbg`
6. IKOS 预处理后 LLVM IR 对应指令及 `!dbg`
7. 必要时补充 AR / raw checks / `output.db` 侧证
8. 解释为什么这是行号不一致
9. 你认为更合理的真实行号
10. 置信度：`high` / `medium` / `low`

十二、建议的审计顺序

1. 确认 `main`
2. 跑主深扫
3. 从 `output.db` 导出 `report.csv`
4. 先筛 `error`、`warning`、`unreachable`
5. 按 source file 和 function 聚类
6. 追原始 `.ll`、预处理 `.pp.ll`、源码、`output.db`
7. 锁定可疑 case 后再做定点复核

十三、最终交付

你最终必须完成两件事：

1. 在 `{{OUT_DIR}}` 中留下完整可复现档案
2. 在最终回复中简洁说明：
   - 是否跑通
   - 最终使用的 domain
   - 是否发生 fallback
   - 主要 checks 统计
   - 是否发现论文可用的行号不一致 case
   - 最强 case 是什么
   - 证据是否充分
   - `{{OUT_DIR}}` 中最值得继续查看的关键文件

如果没有发现可信 case，也要明确写出“未发现高置信度 case”。
