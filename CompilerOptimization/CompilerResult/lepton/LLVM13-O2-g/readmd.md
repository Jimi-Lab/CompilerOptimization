# lepton LLVM13-O2-g build record

## Build target
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/lepton`
- Official doc used: `/home/jimi/PaperExperiment/CompilerOptimization/Target/lepton/README.md`
- Official CMake flow requested by user and used here: `mkdir -p build`, `cd build`, `cmake ..`, `make -j8`
- Docker image: `smackers/smack:latest-full`
- LLVM toolchain: `clang-13`, `clang++-13`, `llvm-link-13`, `llvm-dis-13`
- Required flags: `-O2 -g`

## Important transparency notes
- Lepton's `CMakeLists.txt` injects `-DNDEBUG -O3 -g` only when `CMAKE_BUILD_TYPE` is empty.
- To avoid that incompatible default, this build explicitly set `-DCMAKE_BUILD_TYPE=Release` and overrode `CMAKE_C_FLAGS_RELEASE` and `CMAKE_CXX_FLAGS_RELEASE` to `-O2 -g`.
- During the native build, one warning appeared from bundled zlib: `shifting a negative signed value is undefined` in `dependencies/zlib/inflate.c:1507`. This did not stop the build.
- No configure failure, missing package failure, or compile stop happened in this run.

## Commands actually executed
From `log/commands.log`:

```bash
rm -rf /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/build
mkdir -p /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/build
cd /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/build && cmake /home/jimi/PaperExperiment/CompilerOptimization/Target/lepton -DCMAKE_C_COMPILER=clang-13 -DCMAKE_CXX_COMPILER=clang++-13 -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS_RELEASE='-O2 -g' -DCMAKE_CXX_FLAGS_RELEASE='-O2 -g' -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cd /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/build && make -j8
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/build/compile_commands.json /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/artifacts/compile_commands.json
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/build/lepton /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM13-O2-g/artifacts/lepton_O2_g
```

## Program-level BC generation logic
- Existing LLVM14 result under `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/lepton/LLVM14-O2-g` was used only as structure reference.
- The old LLVM14 BC generation selected only `CMakeFiles/lepton.dir/` compile units, which risks omitting bundled local dependency libraries.
- This LLVM13 build fixed that by selecting compile database entries for all of:
  - `CMakeFiles/lepton.dir/`
  - `CMakeFiles/localmd5.dir/`
  - `CMakeFiles/localzlib.dir/`
  - `CMakeFiles/localbrotli.dir/`
- Each selected compile command was replayed with forced `-O2 -g -emit-llvm -c`.
- The generated object BC files were linked into a single program-level BC for the `lepton` executable.

## Dependency completion strategy
- Included program sources from the official `lepton` executable target, including `src/lepton/main.cc`.
- Included bundled project-local dependency libraries linked by the executable in the non-system-dependency path:
  - `localmd5`
  - `localzlib`
  - `localbrotli`
- This was necessary because the executable links those local libraries in `CMakeLists.txt`, and omitting them would yield an incomplete program-level BC.
- External libc/libstdc++/pthread/syscall-level symbols remain undefined in the BC, which is expected for analysis BC and does not indicate missing Lepton project sources.

## Outputs
- Binary: `artifacts/lepton_O2_g`
- Program BC: `artifacts/lepton_O2_g.bc`
- LLVM IR: `artifacts/lepton_O2_g.ll`
- BC list: `artifacts/bc_files_lepton_program.list`
- Compile DB: `artifacts/compile_commands.json`
- Flag audit: `artifacts/bc_flag_audit.csv`

## Validation
- `main` symbol check: `status/success.marker` reports `main_symbol=present`
- `src/lepton/main.cc` is included in the replayed compile set.
- Flag audit shows every replayed compile unit has `-O2=1`, `-g=1`, `-O3=0`.
- Undefined symbol count: `118`

## Undefined symbol interpretation
- Undefined symbols listed in `log/undefined_symbols.log` include standard library and operating-system interfaces such as:
  - C++ runtime / libstdc++ (`std::thread`, strings, iostreams)
  - libc (`malloc`, `free`, `printf`, `fork`, `socket`, `read`, `write`)
  - pthread/syscall layer (`pthread_mutex_lock`, `syscall`)
- These are runtime externals, not evidence that Lepton's bundled project dependency sources were omitted.

## Logs and status
- Build log: `log/project.log`
- BC rebuild log: `log/bc_build.log`
- Link/disassembly log: `log/llvm_link.log`
- Symbol log: `log/llvm_nm.log`
- Undefined symbols: `log/undefined_symbols.log`
- Commands: `log/commands.log`
- Success marker: `status/success.marker`
