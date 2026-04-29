# libsndfile LLVM14-O2-g build record

## Build policy
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile`
- Build flow reference: `README.md` CMake section (`mkdir CMakeBuild`, `cmake ..`, `cmake --build .`)
- Environment: `seahorn/seahorn-llvm14:fixed`
- Compiler: `clang-14` / `clang++-14`
- Required flags: `-O2 -g`

## Main outputs
- Build directory: `CMakeBuild/`
- Compile DB: `artifacts/compile_commands.json`
- Flag verification: `artifacts/compile_flag_check.txt`
- Built artifacts list: `artifacts/build_outputs.list`

## Logs and status
- Commands: `log/commands.log`
- Build log: `log/project.log`
- Success marker: `status/success.marker`
