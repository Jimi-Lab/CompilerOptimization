# zopfli LLVM13-O2-g build record

## Build target
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zopfli`
- Official doc used: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zopfli/README`
- Official flow used: direct compile of `src/zopfli/*.c` into a single binary, as described in the README
- Docker image: `smackers/smack:latest-full`
- LLVM toolchain: `clang-13`, `clang++-13`, `llvm-link-13`, `llvm-dis-13`
- Required flags: `-O2 -g`

## Transparent issues encountered
- No build-stopping bug, missing dependency, or rerun-requiring path error occurred in this task.
- I did **not** use the repository `Makefile` as the primary build method because it force-injects `-O3` via `override CFLAGS := ... -O3 ...`, which conflicts with your hard requirement.
- Instead, I followed the README's direct compile instruction and replaced `gcc` with `clang-13` while preserving the documented warning/math flags.

## Commands actually executed
From `log/commands.log` and `log/build.log`:

```bash
cp -a /home/jimi/PaperExperiment/CompilerOptimization/Target/zopfli/. /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/work/zopfli-src/
clang-13 src/zopfli/*.c -O2 -g -W -Wall -Wextra -Wno-unused-function -ansi -pedantic -lm -o /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/artifacts/zopfli_O2_g
```

## Program-level BC generation logic
- The README defines the executable as all `src/zopfli/*.c` compiled into one binary.
- To match that program-level structure exactly, this LLVM13 flow compiled every `src/zopfli/*.c` file into `.bc`, then linked them together.
- This includes:
  - `zopfli_bin.c` (program entrypoint with `main`)
  - `zopfli_lib.c`
  - all supporting compression implementation files
- No `zopflipng` sources were included because the README instruction for `zopfli` is specifically the `src/zopfli/*.c` binary.

## Dependency completion strategy
- Included all source files under `src/zopfli/*.c`, not just `zopfli_bin.c`.
- This fixes the common mistake of producing only a front-end or only the library part.
- No extra project-local dependencies outside `src/zopfli/*.c` are required for the README-defined `zopfli` executable.

## Outputs
- Binary: `artifacts/zopfli_O2_g`
- Program BC: `artifacts/zopfli_O2_g.bc`
- LLVM IR: `artifacts/zopfli_O2_g.ll`
- BC list: `artifacts/bc_files_zopfli_program.list`
- Flag audit: `artifacts/bc_flag_audit.csv`

## Validation
- `main` symbol check: `status/success.marker` reports `main_symbol=present`
- Flag audit shows all replayed compile units have `-O2=1`, `-g=1`, `-O3=0`
- Undefined symbol count: `21`

## Undefined symbol interpretation
- Undefined symbols in `log/undefined_symbols.log` are standard C runtime / math / stdio externals such as `malloc`, `free`, `fopen`, `fread`, `fprintf`, `log`, `qsort`.
- These are expected for program-level analysis BC and do not indicate missing zopfli project sources.

## Logs and status
- Build log: `log/build.log`
- BC build log: `log/bc_build.log`
- Link/disassembly log: `log/bc_link.log`
- Symbol log: `log/llvm_nm.log`
- Undefined symbols: `log/undefined_symbols.log`
- Commands: `log/commands.log`
- Success marker: `status/success.marker`
