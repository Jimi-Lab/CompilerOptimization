# 构建 `smackers/smack-llvm13-useable:latest` 的完整修复记录

> Note: Docker image repository names must be lowercase. The requested human-facing
> name `smackers/smack-LLVM13-useable` is therefore recorded and implemented as the
> valid Docker reference `smackers/smack-llvm13-useable:latest`.

## 1. 背景

当前实验需要大量使用 `clang-13 -O2 -g` 编译生成的 LLVM bitcode（`.bc`）作为 SMACK 输入。

原始镜像：

```text
smackers/smack:latest-full
```

在直接处理 cJSON 的 LLVM13 `-O2 -g` bitcode 时，`smack -t` 会在 LLVM 到 Boogie 的翻译阶段崩溃，典型错误如下：

```text
Instruction not handled.
UNREACHABLE executed at /home/user/smack/lib/smack/SmackInstGenerator.cpp:176!
Running pass 'SMACK generator pass'
```

失败输入：

```text
/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/cJSON/LLVM13-O2-g/run_20260420_180338/artifacts/cjson_test_O2_g.bc
```

这个 `.bc` 本身是合法的：

- `llvm-dis-13` 可以正常反汇编。
- `llvm-nm-13` 可以看到 `main`。
- 编译报告显示 LLVM13 `-O2 -g` bitcode 生成成功。

因此问题不是 bitcode 损坏，而是 SMACK 前端 `llvm2bpl` 对 LLVM13/O2 IR 的指令覆盖不足。

## 2. 两个镜像的对比

### `smackers/smack:latest-full`

这是原始基线镜像，用于此前的 SMACK 实验。

本机镜像信息：

```text
tag: smackers/smack:latest-full
image id: sha256:13600d14da35dc1d93ca2a7fc6d7ba82fc4fd4005f1097a215e17c66ae9d3ce7
created: 2026-03-19T19:15:31.345827072+08:00
```

它包含：

- SMACK 2.8.0
- `llvm2bpl`
- Boogie/Corral/Z3 等后端工具
- 可以处理 O0-g bitcode
- 但处理 cJSON LLVM13 `-O2 -g` bitcode 时会在 `freeze` 指令处崩溃

### `smackers/smack-llvm13-useable:latest`

这是本次新增的 patched 镜像。

本机镜像信息：

```text
tag: smackers/smack-llvm13-useable:latest
image id: sha256:166a5ea0757bc6c852bed7e3c3fd1ab45b34aebce870dac1573cf5ce4ec02994
created: 2026-04-23T21:26:42.366850319+08:00
base image: smackers/smack:latest-full
```

它与 `latest-full` 的核心区别：

- 继承 `latest-full` 的完整运行环境。
- 只覆盖 SMACK 源码中的 `SmackInstGenerator.cpp` 和 `SmackInstGenerator.h`。
- 在镜像内重新编译 `llvm2bpl`。
- 将重新编译后的 `llvm2bpl` 安装到 `/usr/local/bin/llvm2bpl`，优先于原始版本被 `smack` 调用。

## 3. 根因定位

原始 `-O2 -g` bitcode 中包含 LLVM13 在优化后常见的指令：

```llvm
%47 = freeze i8 %43
```

`freeze` 是 LLVM 用来消除 `undef/poison` 非确定性的指令。SMACK 当前源码中的 `SmackInstGenerator` 没有实现 `visitFreezeInst`，所以 LLVM visitor 会落到默认分支：

```cpp
void SmackInstGenerator::visitInstruction(llvm::Instruction &inst) {
  SDEBUG(errs() << "Instruction not handled: " << inst << "\n");
  llvm_unreachable("Instruction not handled.");
}
```

这就是 `Instruction not handled` 崩溃的直接原因。

## 4. 源码修复内容

修改文件：

```text
CompilerOptimization/Tools/SMACK/source/smack/include/smack/SmackInstGenerator.h
CompilerOptimization/Tools/SMACK/source/smack/lib/smack/SmackInstGenerator.cpp
CompilerOptimization/Tools/SMACK/source/smack/bin/versions
```

### 4.1 增加 `visitFreezeInst` 声明

在 `SmackInstGenerator.h` 中新增：

```cpp
void visitFreezeInst(llvm::FreezeInst &I);
```

### 4.2 增加 `freeze` 翻译逻辑

在 `SmackInstGenerator.cpp` 中新增：

```cpp
void SmackInstGenerator::visitFreezeInst(llvm::FreezeInst &I) {
  processInstruction(I);
  emit(Stmt::assign(rep->expr(&I), rep->expr(I.getOperand(0))));
}
```

含义：

- 对 SMACK 前端来说，把 `freeze x` 翻译为 `result := x`。
- 这让 `llvm2bpl` 不再因为未知指令崩溃。
- 这个处理是为了兼容 O2 IR 的前端翻译，不改变源码级实验目标。

### 4.3 将本地构建目标切到 LLVM 13

在 `bin/versions` 中将：

```text
LLVM_SHORT_VERSION="12"
LLVM_FULL_VERSION="12.0.1"
```

改为：

```text
LLVM_SHORT_VERSION="13"
LLVM_FULL_VERSION="13.0.1"
```

原因：

- 当前实验产物是 `LLVM13-O2-g`。
- 目标容器里存在 `/usr/bin/llvm-config-13`。
- 用 LLVM13 构建 `llvm2bpl` 与输入 bitcode 更一致。

## 5. 构建脚本

构建脚本路径：

```text
/home/jimi/PaperExperiment/CompilerOptimization/Tools/SMACK/build_smack_o2g_image.sh
```

脚本逻辑：

1. 以 `smackers/smack:latest-full` 为基础镜像。
2. 创建临时 Docker build context。
3. 复制 patched `SmackInstGenerator.cpp` 和 `SmackInstGenerator.h`。
4. 覆盖容器内 `/home/user/smack` 的对应源码文件。
5. 在容器内执行：

```bash
cmake --build /home/user/smack/build -j2 --target llvm2bpl
```

6. 将新编译的 `llvm2bpl` 复制到：

```text
/usr/local/bin/llvm2bpl
```

7. 输出镜像：

```text
smackers/smack-llvm13-useable:latest
```

构建命令：

```bash
CompilerOptimization/Tools/SMACK/build_smack_o2g_image.sh smackers/smack-llvm13-useable:latest
```

也可以通过环境变量替换基础镜像：

```bash
BASE_IMAGE=smackers/smack:latest-full \
CompilerOptimization/Tools/SMACK/build_smack_o2g_image.sh smackers/smack-llvm13-useable:latest
```

## 6. 验证过程

使用 patched 镜像直接验证原始 cJSON LLVM13 `-O2 -g` bitcode：

```bash
timeout -s KILL -k 10 180 \
docker run --rm --user 1000:1000 \
  -v /home/jimi/PaperExperiment:/work \
  -w /work \
  --entrypoint /bin/bash \
  smackers/smack-llvm13-useable:latest \
  -lc 'smack -t \
    --bc-file /tmp/cjson_o2_patched_image.init.bc \
    --ll-file /tmp/cjson_o2_patched_image.final.ll \
    --bpl-file /tmp/cjson_o2_patched_image.bpl \
    CompilerOptimization/CompilerResult/cJSON/LLVM13-O2-g/run_20260420_180338/artifacts/cjson_test_O2_g.bc'
```

验证结果：

```text
SMACK generated /tmp/cjson_o2_patched_image.bpl
```

说明：

- 原始 `latest-full` 会在 `Instruction not handled` 处失败。
- patched `smack-llvm13-useable:latest` 可以完成 `smack -t` 翻译并生成 Boogie 文件。

## 7. 后续批量实验使用方式

后续所有需要直接处理 LLVM13 `-O2 -g` bitcode 的 SMACK 扫描脚本，建议将镜像从：

```text
smackers/smack:latest-full
```

替换为：

```text
smackers/smack-llvm13-useable:latest
```

例如：

```bash
docker run --rm \
  -v /home/jimi/PaperExperiment:/work \
  -w /work \
  --entrypoint /bin/bash \
  smackers/smack-llvm13-useable:latest \
  -lc 'smack -t input_O2_g.bc'
```

## 8. 当前修复边界

这次修复解决的是 SMACK 在 LLVM13 `freeze` 指令上的前端崩溃。

它已经验证可以让 cJSON 的原始 LLVM13 `-O2 -g` bitcode 通过 `smack -t` 翻译阶段。

但需要注意：

- O2 IR 可能还包含其他项目特有的 LLVM 指令。
- 如果后续其他项目遇到新的 `Instruction not handled`，应继续在 `SmackInstGenerator` 中补对应 visitor。
- 当前修复主要保证“前端不因 `freeze` 崩溃”，不等价于保证所有 SMACK 后端验证任务都能在时间/内存限制内完成。

## 9. 建议记录方式

在后续实验报告中建议明确标注：

```text
SMACK image: smackers/smack-llvm13-useable:latest
Base image: smackers/smack:latest-full
Patch: add LLVM FreezeInst handling in SmackInstGenerator
Target input: LLVM13 -O2 -g bitcode
```
