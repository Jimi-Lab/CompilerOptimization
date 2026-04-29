# libsndfile LLVM13-O2-g build record

## Build target
- Source: `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile`
- Official doc used: `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/README.md`
- Official build flow requested and used: CMake out-of-tree build (`mkdir CMakeBuild`, `cd CMakeBuild`, `cmake ..`, build with native tools)
- Docker image: `smackers/smack:latest-full`
- LLVM toolchain: `clang-13`, `clang++-13`, `llvm-link-13`, `llvm-dis-13`
- Required flags: `-O2 -g`

## Transparent issues encountered during this task
- First attempt failed because I ran the official `cmake ..` flow from an output directory instead of a source-tree work copy. CMake then tried to use `CompilerResult/.../LLVM13-O2-g` as source and failed with: `does not appear to contain CMakeLists.txt`.
- Second attempt failed because the copied work tree contained read-only files and `rm -rf` could not clean it. I fixed this by adding `chmod -R u+w` before cleanup.
- Third attempt built successfully but my artifact copy path was wrong: I assumed `sndfile-convert` would be in `CMakeBuild/programs/`, while the actual target output is `CMakeBuild/sndfile-convert`. I fixed the script and reran.
- No silent workaround was used; all three issues are visible in `log/project.log` and the script history.

## Important environment limitations found during configuration
The SMACK Ubuntu 22.04 image does not provide several optional/recommended audio dependencies, so CMake disabled related features:

- Missing optional packages: `ALSA`, `Sndio`, `Speex`, `SQLite3`
- Missing recommended packages: `Ogg`, `Vorbis`, `FLAC`, `Opus`, `mp3lame`, `mpg123`

Consequence:
- `ENABLE_EXTERNAL_LIBS=OFF`
- `ENABLE_MPEG=OFF`
- `sndfile-play` still built, but without ALSA/Sndio-backed playback support
- Program-level BC does not include external codec implementations because the environment did not provide those libraries

This is not hidden; it is exactly what CMake reported in `log/project.log`.

## Commands actually executed
From `log/commands.log`:

```bash
chmod_existing_work_tree
rm -rf /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src
mkdir -p /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src
cp -a /home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/. /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src/
chmod -R u+w /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src
mkdir -p /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src/CMakeBuild
cd /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src/CMakeBuild && cmake .. -G 'Unix Makefiles' -DCMAKE_C_COMPILER=clang-13 -DCMAKE_CXX_COMPILER=clang++-13 -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS_RELEASE='-O2 -g' -DCMAKE_CXX_FLAGS_RELEASE='-O2 -g' -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_PROGRAMS=ON -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=OFF
cd /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src/CMakeBuild && cmake --build . -j8
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src/CMakeBuild/compile_commands.json /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/artifacts/compile_commands.json
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src/CMakeBuild/sndfile-convert /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/artifacts/sndfile-convert_O2_g
cp -f /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/work/libsndfile-src/CMakeBuild/libsndfile.a /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/artifacts/libsndfile_O2_g.a
```

## Program-level BC generation logic
- Existing LLVM14 outputs were used only as structural reference.
- Old LLVM14 flow already showed that a library-only BC is insufficient, so this LLVM13 flow explicitly selected:
  - all `CMakeFiles/sndfile.dir/` compile units (the library implementation)
  - all `CMakeFiles/sndfile-convert.dir/` compile units (the executable entrypoint)
- This means the final BC includes both the `sndfile` library implementation and the `sndfile-convert` program `main`.
- Each selected compile command was replayed with forced `-O2 -g -emit-llvm -c`, then linked using `llvm-link-13`.

## Dependency completion strategy
- Included the whole `sndfile` target, not only the front-end utility sources.
- Included `programs/common.c` and `programs/sndfile-convert.c` from the executable target.
- Did not add Ogg/Vorbis/FLAC/Opus/MPEG external libraries because CMake could not find them in the SMACK image; therefore the build itself disabled those features, and there was nothing project-local to add for those codecs in this environment.

## Outputs
- Binary: `artifacts/sndfile-convert_O2_g`
- Static library: `artifacts/libsndfile_O2_g.a`
- Program BC: `artifacts/libsndfile_sndfile_convert_O2_g.bc`
- LLVM IR: `artifacts/libsndfile_sndfile_convert_O2_g.ll`
- BC list: `artifacts/bc_files_sndfile_program.list`
- Compile DB: `artifacts/compile_commands.json`
- Flag audit: `artifacts/bc_flag_audit.csv`

## Validation
- `main` symbol check: `status/success.marker` reports `main_symbol=present`
- `sndfile-convert.c` is included in the replayed compile set.
- Flag audit shows every replayed compile unit has `-O2=1`, `-g=1`, `-O3=0`.
- Undefined symbol count: `55`

## Undefined symbol interpretation
- The undefined symbols in `log/undefined_symbols.log` are libc/libm/runtime externals such as `malloc`, `fopen`, `printf`, `fmod`, `strtod`, `write`.
- These are expected for a program-level analysis BC and do not mean libsndfile project sources were omitted.

## Logs and status
- Build log: `log/project.log`
- BC rebuild log: `log/bc_build.log`
- Link/disassembly log: `log/bc_link.log`
- Symbol log: `log/llvm_nm.log`
- Undefined symbols: `log/undefined_symbols.log`
- Commands: `log/commands.log`
- Success marker: `status/success.marker`
