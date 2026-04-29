# flatbuffers LLVM14-O2-g (official flatc target)

## Build policy
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/flatbuffers`
- Build flow: official CMake target `flatc`
- Toolchain: `clang-14` / `clang++-14`
- Flags: `-O2 -g` only

## Compile outputs
- Whole-program BC for `flatc`: `artifacts/flatbuffers_flatc_O2_g.bc`
- Disassembly: `artifacts/flatbuffers_flatc_O2_g.ll`
- Recompiled object BC list: `artifacts/bc_files_flatc.list`
- Build command database: `artifacts/compile_commands.json`

## Logs and status
- Compile log: `log/project.log`
- Command trace: `log/commands.log`
- Link/disassembly log: `log/llvm_link.log`
- Symbol log (`main` check): `log/llvm_nm.log`
- Success marker: `status/success.marker`

## SeaHorn smoke
- Latest smoke pointer: `result/latest_smoke.txt`
- Latest smoke report: `result/run_20260320_172745_smoke/report.md`
- Current smoke outcome: `inspect-bitcode` succeeded; `sea horn --track=reg` crashed with `std::bad_alloc` on this BC.
