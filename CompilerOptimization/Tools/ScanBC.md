# BC 扫描工具汇总

目的：把仓库里**已经实际用于 `.bc` / whole-program `.bc` 扫描**的工具收拢到一页，后续复现时可以直接按对应 docker 起环境。

## 纳入标准

- 只收录仓库里已经实际跑过 BC 扫描的工具。
- 不收录不是 BC 输入的工具。

## 速查

| 场景                                   | 直接优先用的 docker                                                      |
| -------------------------------------- | ------------------------------------------------------------------------ |
| LLVM13 `-O2 -g` 的 BC 直接扫描       | `smackers/smack:latest-full-o2g`、`ikos:3.5-llvm14-o2g`              |
| LLVM14 whole-program BC 的批量静态扫描 | `seahorn/seahorn-llvm14:fixed`、`dg-llvm14:latest`、`phasar:nosan` |
| SVF / SABER 路线                       | `svftools/svf:latest`                                                  |
| KLEE 路线                              | `klee-dev`（仓库里目前只记录到容器名）                                 |

## 总表

> 说明：`仓库内未记录` 的意思是当前 repo 里没有找到可直接 `docker build` 的 Dockerfile，只能看到现成镜像名或容器名。

| 工具        | 当前建议 docker image                                                            | 仓库内 Dockerfile / 构建脚本                                                                                                                                                                          | 是否 patch              | patch / 兼容说明                                                                                                                                     | 实际使用证据                                                                                                                                                                                                                                                 |
| ----------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SMACK       | `smackers/smack:latest-full-o2g`                                               | [SMACK/Dockerfile.latest-full](SMACK/Dockerfile.latest-full) `<br>`[SMACK/build_smack_o2g_image.sh](SMACK/build_smack_o2g_image.sh) `<br>`[SMACK/build_smack_o2g_image.md](SMACK/build_smack_o2g_image.md) | 是                      | `latest-full-o2g` 基于 `latest-full`，补了 `freeze` 指令处理，并在镜像内重编 `llvm2bpl`；LLVM13 `-O2 -g` 的 cJSON BC 需要这个 patched 镜像 | [cJSON O2-g](../Result/cjson/smack/smack-O2-g/runs/run_20260423_134930/report/final_report.md) `<br>`[libsndfile O2-g](../Result/libsndfile/smack/smack-O2-g/report/final_report.md)                                                                             |
| IKOS        | `ikos:3.5-llvm14-o2g<br>``ikos:3.5-llvm14`（基线 / `ikos-scan`）             | [ikos/Dockerfile](ikos/Dockerfile) `<br>`[ikos/build_ikos_o2g_image.sh](ikos/build_ikos_o2g_image.sh) `<br>`[ikos/build_ikos_o2g_image.md](ikos/build_ikos_o2g_image.md)                                   | 是                      | `o2g` 镜像补了 `Scalarizer` 预处理和 `freeze` importer 兼容；常规 `ikos-scan` 记录主要还是基线镜像                                           | [curl ikos-scan](../Result/curl/ikos/O2_scan_with_ikos_scan/readme.md) `<br>`[leveldb ikos-scan](../Result/leveldb/ikos/O2_scan_with_ikos_scan/readme.md)                                                                                                        |
| SeaHorn     | `seahorn/seahorn-llvm14:fixed<br>``seahorn/seahorn-llvm14:nightly`（fallback） | [SeaHorn/Dockerfile.llvm14-fixed](SeaHorn/Dockerfile.llvm14-fixed) `<br>`[SeaHorn/readmd.md](SeaHorn/readmd.md)                                                                                           | 是                      | `fixed` 基于 `nightly`，修了 `crab` 参数兼容和 `sea term` 的 z3/runtime 兼容问题；当前项目脚本通常是 `preferred=fixed, fallback=nightly`   | [zopfli fixed fullscan](../Result/zopfli/seahorn/seahorn-O2-g/result/run_20260320_121720_fixed_fullscan/report/final_report.md) `<br>`[tengine fixed](../Result/tengine/seahorn/seahorn-O2-g/result/run_20260322_185943_fixed_fullmatrix/report/final_report.md) |
| DG          | `dg-llvm14:latest`                                                             | [dg/Dockerfile](dg/Dockerfile)                                                                                                                                                                           | 是                      | DG 源码在仓库里做过稳定性修复后重建镜像：补了 `freeze`、向量相关保护，以及 `llvm-cda-dump` 的诚实失败/防崩溃处理                                 | [tengine executor](../Result/tengine/dg/executor.md) `<br>`[tengine report](../Result/tengine/dg/dg-LLVM14-O2-g/high_precision_20260325_125828/report.md)                                                                                                        |
| PhASAR      | `phasar:nosan<br>``phasar:latest`（历史基线）                                  | [phasar/repo/phasar/Dockerfile.nosan](phasar/repo/phasar/Dockerfile.nosan) `<br>`[phasar/repo/phasar/Dockerfile](phasar/repo/phasar/Dockerfile)                                                           | 是（镜像变体）          | 当前批量 runner 已切到 `phasar:nosan`；原因是 `phasar:latest` 开启 sanitizers 后在部分 case 上会把内部 UB/空指针问题直接打成 fatal               | [run_all_targets_phasar_O2_g.sh](../Result/run_all_targets_phasar_O2_g.sh) `<br>`[leveldb O0 readme](../Result/leveldb/phasar/phasar_O0_DebInfo/readme.md)                                                                                                       |
| SVF / SABER | `svftools/svf:latest`                                                          | 仓库内未记录 SVF Dockerfile `<br>`仅有使用说明：[SVF/readme.md](SVF/readme.md)                                                                                                                         | 未见 repo 内 patch 记录 | 目前已记录的 leveldb 流程里，BC 构建和 SABER 扫描是分开的：构建阶段用 `pdschbrt/phasar:latest`，真正扫描阶段用 `svftools/svf:latest`             | [leveldb SVF](../Result/leveldb/SVF/readme.md)                                                                                                                                                                                                                  |
| KLEE        | `klee-dev`                                                                     | 仓库内未记录 Dockerfile `<br>`仅有使用说明：[klee/readme.md](klee/readme.md)                                                                                                                           | 未见 repo 内 patch 记录 | 已用于 `leveldb.bc` / `leveldb_linked.bc`；但如果后续要严格 docker 重建，还需要补齐真实 image tag 或 Dockerfile                                  | [leveldb KLEE](../Result/leveldb/klee/readme.md)                                                                                                                                                                                                                |

## 当前最适合直接复现的选择

- SMACK：优先 `smackers/smack:latest-full-o2g`，尤其是 LLVM13 `-O2 -g` 的 BC。
- IKOS：普通 `ikos-scan` 流程可先用 `ikos:3.5-llvm14`；直接扫 O2-g 兼容问题时优先 `ikos:3.5-llvm14-o2g`。
- SeaHorn：优先 `seahorn/seahorn-llvm14:fixed`。
- DG：优先 `dg-llvm14:latest`，并沿用 [tengine executor](../Result/tengine/dg/executor.md) 里的参数约束。
- PhASAR：优先 `phasar:nosan`。
- SVF / SABER：当前按 `svftools/svf:latest` 复现，但仓库里没有对应 Dockerfile。
- KLEE：当前只能按已有容器 `klee-dev` 复现，镜像来源信息还不完整。

## 未纳入本表

- `BinAbsInspector`：仓库里确实用过，但它是 binary / Pcode 路线，不是 BC 扫描，所以不放进这个表。
- `codeql`、`infer`、`joern`、`Cppcheck`、`Flawfinder`：不是 BC 扫描主线。
