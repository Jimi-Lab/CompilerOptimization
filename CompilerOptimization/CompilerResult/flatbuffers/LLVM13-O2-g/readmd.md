# flatbuffers LLVM13-O2-g build record

## Build target
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers`
- Official doc used: `/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers/README.md`
- Official build flow used: CMake configure + build, targeting `flatc`
- Docker image: `smackers/smack:latest-full`
- LLVM toolchain: `clang-13`, `clang++-13`, `llvm-link-13`, `llvm-dis-13`
- Required flags: `-O2 -g`

## Commands actually executed
From `log/commands.log`:

```bash
rm -rf /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/build
cmake -S /home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers -B /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/build -G "Unix Makefiles" -DCMAKE_C_COMPILER=clang-13 -DCMAKE_CXX_COMPILER=clang++-13 -DCMAKE_C_FLAGS="-O2 -g" -DCMAKE_CXX_FLAGS="-O2 -g" -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/build --target flatc -j$(nproc)
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/build/compile_commands.json /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/artifacts/compile_commands.json
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/build/flatc /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/artifacts/flatc_O2_g
```

## Program-level BC generation logic
- Reference output layout was taken from `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g`
- To avoid library-only BC, the process selected compile database entries for `CMakeFiles/flatc.dir/`
- Those entries correspond to the full `flatc` executable target, including `src/flatc_main.cpp`
- Each compile command was replayed with LLVM13 and forced `-O2 -g -emit-llvm -c`
- Generated object BC files were linked with `llvm-link-13` into one program-level BC

## Dependency completion strategy
- Included all compile units from the official `flatc` target rather than only the library subset
- This captures FlatBuffers compiler sources and bundled grpc generator sources already wired into the executable target
- No extra project-local source files were missing from the official `flatc` compile database set
- The final BC still contains external undefined symbols from the C++ runtime / libc layer, which is expected for program-level analysis BC and does not indicate missing FlatBuffers project sources

## Outputs
- Binary: `artifacts/flatc_O2_g`
- Program BC: `artifacts/flatbuffers_flatc_O2_g.bc`
- LLVM IR: `artifacts/flatbuffers_flatc_O2_g.ll`
- BC list: `artifacts/bc_files_flatc.list`
- Compile DB: `artifacts/compile_commands.json`
- Flag audit: `artifacts/bc_flag_audit.csv`

## Validation
- `main` symbol check: `status/success.marker` reports `main_symbol=present`
- `flatc_main.cpp` is included through the official executable target selection
- Flag audit shows every replayed compile unit has `-O2=1`, `-g=1`, `-O3=0`
- Undefined symbol count: `159`

## Undefined symbol interpretation
- Undefined symbols listed in `log/undefined_symbols.log` are dominated by standard library / runtime references such as `std::string`, iostreams, allocation, and libc++/libstdc++ support
- These are link-time/runtime externals, not evidence that FlatBuffers project source dependencies were omitted
- No missing FlatBuffers-internal object file was detected in this LLVM13 program-level BC build

## Logs and status
- Build log: `log/project.log`
- BC rebuild log: `log/bc_build.log`
- Link/disassembly log: `log/llvm_link.log`
- Symbol log: `log/llvm_nm.log`
- Undefined symbols: `log/undefined_symbols.log`
- Commands: `log/commands.log`
- Success marker: `status/success.marker`
