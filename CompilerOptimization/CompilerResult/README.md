# Compiler Results

This directory contains compiled bitcode, LLVM IR, native binaries, build work
directories, and detailed compiler logs.

The GitHub repository intentionally tracks the full contents of these selected
target result trees:

- `flatbuffers`
- `lepton`
- `curl`
- `libsndfile`
- `masscan`
- `redis`
- `tengine`
- `zfp`
- `zopfli`

The GitHub repository intentionally excludes these target result trees:

- `cJSON` / `cjson`
- `duckdb`
- `flite`
- `grpc`
- `leveldb`
- `libco`
- `libexpat` / `Expat`
- `miniz`
- `opencv`
- `rapidjson`
- `rethinkdb`
- `tiny-AES-c`
- `zlib`

Several tracked target trees contain files larger than normal GitHub Git file
limits, so pushing them to GitHub requires Git LFS or an external artifact
strategy.
