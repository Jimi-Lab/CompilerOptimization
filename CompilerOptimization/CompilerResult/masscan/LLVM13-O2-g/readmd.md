# masscan LLVM13-O2-g build record

## Build target
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/masscan`
- Official doc used: `/home/jimi/PaperExperiment/CompilerOptimization/Target/masscan/README.md`
- Official build flow used: README `make` flow with `clang`
- Docker image: `smackers/smack:latest-full`
- LLVM toolchain: `clang-13`, `clang++-13`, `llvm-link-13`, `llvm-dis-13`
- Required flags: `-O2 -g`

## Transparent issues encountered
- No build-stopping compatibility bug, missing environment package, or rerun-requiring script failure occurred in this task.
- The native build emitted warnings from `src/massip-addr.c`:
  - `excess elements in union initializer`
  - `unused variable 'ip'`
- These warnings did not stop the build and are preserved in `log/build.log`.

## Commands actually executed
From `log/commands.log`:

```bash
rm -rf /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM13-O2-g/work/masscan-src
mkdir -p /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM13-O2-g/work/masscan-src
cp -a /home/jimi/PaperExperiment/CompilerOptimization/Target/masscan/. /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM13-O2-g/work/masscan-src/
chmod -R u+w /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM13-O2-g/work/masscan-src
make -C /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM13-O2-g/work/masscan-src clean
make -C /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM13-O2-g/work/masscan-src CC=clang-13 CFLAGS="-g -ggdb -Wall -O2" -j8
```

## Program-level BC generation logic
- Existing LLVM14 result under `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g` was used only as reference.
- masscan does not use CMake compile databases in its official flow; the README and Makefile use plain `make` over `src/*.c`.
- The Makefile builds the executable from every `src/*.c` file into `tmp/*.o`, then links them into `bin/masscan`.
- To mirror that program-level structure, this LLVM13 flow recompiles every `src/*.c` into `.bc` and then links them all together.
- `src/main-conf.c` was replayed with `-DGIT="<git describe>"` to preserve the Makefile's special `GIT` define behavior.

## Dependency completion strategy
- Included all project source files from `src/*.c`, not just a subset.
- No extra project-local library target exists outside that source set in the official Makefile path.
- External runtime needs from Linux (`-lm -lrt -ldl -lpthread`) are not embedded as project source BC; they remain external symbols, which is expected for program-level analysis BC.

## Outputs
- Binary: `artifacts/masscan_O2_g`
- Program BC: `artifacts/masscan_O2_g.bc`
- LLVM IR: `artifacts/masscan_O2_g.ll`
- BC list: `artifacts/bc_files_masscan_program.list`
- Flag audit: `artifacts/bc_flag_audit.csv`

## Validation
- `main` symbol check: `status/success.marker` reports `main_symbol=present`
- Flag audit shows replayed compile units have `-O2=1`, `-g=1`, `-O3=0`
- Undefined symbol count: `93`

## Undefined symbol interpretation
- Undefined symbols listed in `log/undefined_symbols.log` are libc/libm/pthread/dlopen/runtime APIs such as `pthread_create`, `sqrt`, `clock_gettime`, `dlopen`, `socket`, `send`, `recv`.
- These are expected runtime externals from the official Linux link path, not evidence of missing masscan project sources.

## Logs and status
- Build log: `log/build.log`
- BC build log: `log/bc_build.log`
- Commands: `log/commands.log`
- Symbol log: `log/llvm_nm.log`
- Undefined symbols: `log/undefined_symbols.log`
- Success marker: `status/success.marker`
