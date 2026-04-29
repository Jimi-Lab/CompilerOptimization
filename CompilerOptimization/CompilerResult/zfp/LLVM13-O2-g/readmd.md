# zfp LLVM13-O2-g build record

## Build target
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp`
- Official doc used: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/README.md`
- Official flow used: CMake out-of-tree build (`mkdir build`, `cd build`, `cmake ..`, `cmake --build . --config Release`)
- Docker image: `smackers/smack:latest-full`
- LLVM toolchain: `clang-13`, `clang++-13`, `llvm-link-13`, `llvm-dis-13`
- Required flags: `-O2 -g`

## Transparent issues encountered
- No build-stopping bug or rerun-requiring path mistake occurred in this task.
- Environment limitations reported by CMake:
  - OpenMP not found
  - `libm` check without `-lm` failed, but fallback test with `-lm` succeeded (`HAVE_LIBM_MATH`)
- These did not block the build.

## Commands actually executed
From `log/commands.log`:

```bash
rm -rf /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM13-O2-g/build
cmake -S /home/jimi/PaperExperiment/CompilerOptimization/Target/zfp -B /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM13-O2-g/build -G "Unix Makefiles" -DCMAKE_C_COMPILER=clang-13 -DCMAKE_CXX_COMPILER=clang++-13 -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS_RELEASE="-O2 -g" -DCMAKE_CXX_FLAGS_RELEASE="-O2 -g" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_UTILITIES=ON
cmake --build /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM13-O2-g/build -j10
```

## Program-level BC generation logic
- Existing LLVM14 result under `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zfp/LLVM14-O2-g` was used only as reference.
- To avoid library-only BC, this LLVM13 flow selected compile database entries for both:
  - `CMakeFiles/zfp.dir/` (core library implementation)
  - `CMakeFiles/zfpcmd.dir/` (command-line executable target, output name `zfp`)
- This includes the `utils/zfp.c` entrypoint and the linked library implementation in one program-level BC.
- All selected compile commands were replayed with forced `-O2 -g -emit-llvm -c`, then linked with `llvm-link-13`.

## Dependency completion strategy
- Included the full `zfp` library target and the `zfpcmd` executable target.
- This matches the official executable relationship in `utils/CMakeLists.txt`, where `zfpcmd` links against `zfp` and optionally `m`.
- External `libm` functions remain undefined in the BC as runtime externals; this is expected for analysis BC and does not indicate missing project sources.

## Outputs
- Binary: `artifacts/zfp_O2_g`
- Program BC: `artifacts/zfp_O2_g.bc`
- LLVM IR: `artifacts/zfp_O2_g.ll`
- BC list: `artifacts/bc_files_zfp_program.list`
- Compile DB: `artifacts/compile_commands.json`
- Flag audit: `artifacts/bc_flag_audit.csv`

## Validation
- `main` symbol check: `status/success.marker` reports `main_symbol=present`
- Flag audit shows all replayed compile units have `-O2=1`, `-g=1`, `-O3=0`
- Undefined symbol count: `23`

## Undefined symbol interpretation
- Undefined symbols in `log/undefined_symbols.log` are runtime/math/stdio externals such as `sqrt`, `log10`, `frexp`, `ldexp`, `fopen`, `fread`, `fprintf`.
- These are expected for program-level analysis BC and do not indicate missing zfp source dependencies.

## Logs and status
- Build log: `log/build.log`
- BC build log: `log/bc_build.log`
- Link/disassembly log: `log/bc_link.log`
- Symbol log: `log/llvm_nm_program.log`
- Undefined symbols: `log/undefined_symbols.log`
- Commands: `log/commands.log`
- Success marker: `status/success.marker`
