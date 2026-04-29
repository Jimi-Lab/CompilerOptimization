# Tengine LLVM13-O2-g build record

## Build target
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/Tengine`
- Official doc used: `/home/jimi/PaperExperiment/CompilerOptimization/Target/Tengine/README.md`
- Official flow used: CMake out-of-tree build from the project root
- Docker image: `smackers/smack:latest-full`
- LLVM toolchain: `clang-13`, `clang++-13`, `llvm-link-13`, `llvm-dis-13`
- Required flags: `-O2 -g`
- Program-level BC target chosen: `tm_classification`

## Transparent issues encountered
- First script version attempted `cmake --install` after building only `tengine-lite-static` and `tm_classification`.
- That failed because the install rules expect additional example binaries such as `tm_classification_int8`, which were not built in the limited target build.
- I removed the install step and reran. This is why the final successful flow copies the needed artifacts directly from the build tree instead of invoking install.
- CMake also reported environment limitations:
  - OpenMP not found
  - OpenCV not found, so OpenCV-based examples were not built
- These were warnings, not hidden failures.

## Commands actually executed in the final successful run
From `log/commands.log`:

```bash
rm -rf /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/install
mkdir -p /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src
cp -a /home/jimi/PaperExperiment/CompilerOptimization/Target/Tengine/. /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src/
chmod -R u+w /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src
cmake -S /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src -B /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src/build -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=clang-13 -DCMAKE_CXX_COMPILER=clang++-13 -DCMAKE_C_FLAGS="-O2 -g" -DCMAKE_CXX_FLAGS="-O2 -g" -DCMAKE_C_FLAGS_DEBUG="-O2 -g" -DCMAKE_CXX_FLAGS_DEBUG="-O2 -g" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_INSTALL_PREFIX=/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/install -DTENGINE_BUILD_EXAMPLES=ON -DTENGINE_BUILD_BENCHMARK=ON -DTENGINE_BUILD_TESTS=OFF -DTENGINE_BUILD_DEMO=OFF -DTENGINE_BUILD_CPP_API=OFF -DTENGINE_BUILD_CONVERT_TOOL=OFF -DTENGINE_BUILD_QUANT_TOOL=OFF
cmake --build /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src/build --target tengine-lite-static tm_classification -j8
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src/build/compile_commands.json /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/artifacts/compile_commands.json
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src/build/examples/tm_classification /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/artifacts/tm_classification_O2_g
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/work/Tengine-src/build/source/libtengine-lite-static.a /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/tengine/LLVM13-O2-g/artifacts/libtengine-lite-static_O2_g.a
```

## Program-level BC generation logic
- Existing LLVM14 Tengine result was used only as a structural reference.
- The LLVM14 export helper in the repository only exported a chosen executable target and could miss library dependency objects.
- To avoid that omission, this LLVM13 build selected compile database entries for both:
  - `CMakeFiles/tengine-lite-static.dir/`
  - `CMakeFiles/tm_classification.dir/`
- This ensures the final BC includes the Tengine library implementation and the example program entrypoint.
- All selected compile commands were replayed with forced `-O2 -g -emit-llvm -c`, then linked together with `llvm-link-13`.

## Dependency completion strategy
- Included the full `tengine-lite-static` target rather than only `tm_classification.c`.
- Included `examples/common/tengine_operations.c` and `examples/tm_classification.c` from the executable target.
- Did not include OpenCV-based example targets because CMake did not find OpenCV in the SMACK image and therefore did not configure those targets.

## Build warnings observed
- `source/api/c_api.c`: assigning `const char*` to `char*`
- `source/device/cpu/op/clip/clip_kernel_ref_int8.c`: constant conversion `255 -> -1` for `int8_t`
- `source/device/cpu/op/conv/x86/conv_hcl_x86.c`: function pointer used as boolean expression warning
- `source/operator/prototype/expand.c`: `fabs` used on integer expression
- `examples/tm_classification.c`: deprecated `add_context_device`

These warnings did not stop the build or BC export, and are recorded in `log/project.log` and `log/bc_build.log`.

## Outputs
- Binary: `artifacts/tm_classification_O2_g`
- Static library: `artifacts/libtengine-lite-static_O2_g.a`
- Program BC: `artifacts/tengine_tm_classification_O2_g.bc`
- LLVM IR: `artifacts/tengine_tm_classification_O2_g.ll`
- BC list: `artifacts/bc_files_tm_classification_program.list`
- Compile DB: `artifacts/compile_commands.json`
- Flag audit: `artifacts/bc_flag_audit.csv`

## Validation
- `main` symbol check: `status/success.marker` reports `main_symbol=present`
- Flag audit covers 384 replayed compile units and records `-O2=1`, `-g=1`, `-O3=0`
- Undefined symbol count: `105`

## Undefined symbol interpretation
- Undefined symbols in `log/undefined_symbols.log` are runtime/system/library externals such as `pthread_*`, `dlopen`, `sqrt`, `socket`, `getaddrinfo`, `fopen`, `read`, `write`.
- These are expected for program-level analysis BC and are not evidence that Tengine project-local source dependencies were omitted.

## Logs and status
- Build log: `log/project.log`
- BC build log: `log/bc_build.log`
- Link/disassembly log: `log/llvm_link.log`
- Symbol log: `log/llvm_nm.log`
- Undefined symbols: `log/undefined_symbols.log`
- Commands: `log/commands.log`
- Success marker: `status/success.marker`
