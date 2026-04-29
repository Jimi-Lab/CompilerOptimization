本次是 `-O2 -g / phasar-O2-g` 这轮扫描的状态清单与原因归类（基于当前真实日志）。

总览：

- 目标项目 18 个
- 成功 8 个：curl, tengine, lepton, libsndfile, masscan, redis, zfp, zopfli
- 失败 10 个
- 状态总表：`CompilerOptimization/Result/phasar_O2_g_project_status.csv`
- linecheck 汇总：`CompilerOptimization/Result/phasar_O2_g_linecheck_summary.csv`

一、编译/配置阶段失败（不是 PhASAR 本身）

- wasmedge：编译失败，缺 lld 头文件
  - 证据：`fatal error: 'lld/Common/Driver.h' file not found`
  - 日志：`CompilerOptimization/Result/wasmedge/phasar/phasar-O2-g/log/project.log`
- opencv：CMake 配置失败（尝试写源码目录 `.cache`，权限拒绝）
  - 证据：`file failed to create directory ... Target/opencv/.cache ... Permission denied`
  - 日志：`CompilerOptimization/Result/opencv/phasar/phasar-O2-g/log/project.log`
- leveldb：编译失败（C++ 标准/编译参数组合导致）
  - 证据：`no template named 'is_standard_layout_v'`
  - 日志：`CompilerOptimization/Result/leveldb/phasar/phasar-O2-g/log/project.log`
- libco：编译通过后链接示例目标失败
  - 证据：`clang: error: linker command failed`
  - 日志：`CompilerOptimization/Result/libco/phasar/phasar-O2-g/log/project.log`
- flite：Make dry-run 失败（项目需先配置）
  - 证据：`./configure: Permission denied`、`No rule to make target 'config.status'`
  - 日志：`CompilerOptimization/Result/flite/phasar/phasar-O2-g/log/project.log`
- rethinkdb：Make dry-run 失败（未配置）
  - 证据：`Run ./configure or edit ./config.mk`
  - 日志：`CompilerOptimization/Result/rethinkdb/phasar/phasar-O2-g/log/project.log`

二、Whole-program bitcode 链接阶段失败（预处理/流水线阶段）

- duckdb：`llvm-link` 被系统杀掉（SIGKILL，偏内存压力）
  - 日志：`CompilerOptimization/Result/duckdb/phasar/phasar-O2-g/log/llvm_link.log`
- rapidjson：`no bc files generated` 导致 `llvm-link` 失败
  - 日志：`CompilerOptimization/Result/rapidjson/phasar/phasar-O2-g/log/llvm_link.log`

三、PhASAR 扫描阶段失败（构建与链接已完成）

- flatbuffers：`ifds-uninit` 被杀（137，OOM/killed）
  - 状态：`oom_or_killed`
  - 日志：`CompilerOptimization/Result/flatbuffers/phasar/phasar-O2-g/log/summary.csv`
- grpc：已完成可写工作副本 + 子模块初始化 + `-O2 -g` 构建，但 `ifds-uninit` 在 timeout 与 no-timeout 两次运行中均失败（最终为 137，OOM/killed）
  - 状态：`oom_or_killed`
  - 日志：`CompilerOptimization/Result/grpc/phasar/phasar-O2-g/log/summary.csv`

四、流水线脚本问题修复后的最新结论

- masscan：已修复 make dry-run 日志路径问题，现已全流程成功（含 linecheck）
  - 状态标记：`CompilerOptimization/Result/masscan/phasar/phasar-O2-g/status/success.marker`
- redis：同样修复日志路径问题后，已能稳定跑到 PhASAR；本次通过 no-timeout 后台运行完成，`ifds-uninit` 成功（`exit_code=0`）
  - 最新报告：`CompilerOptimization/Result/redis/phasar/phasar-O2-g/runs/ifds-uninit/redis_O2_g-Wed-Mar-18-09:36:32-2026/psr-report.txt`
  - 状态标记：`CompilerOptimization/Result/redis/phasar/phasar-O2-g/status/success.marker`

五、无超时重跑后已成功的项目

- tengine：去掉 `ifds-uninit` 超时限制后成功（`exit_code=0`）
  - 日志：`CompilerOptimization/Result/tengine/phasar/phasar-O2-g/log/ifds-uninit.no_timeout.stdout.log`
- lepton：去掉 `ifds-uninit` 超时限制后成功（`exit_code=0`）
  - 日志：`CompilerOptimization/Result/lepton/phasar/phasar-O2-g/log/ifds-uninit.no_timeout.stdout.log`
