# GitHub Archive Policy

This repository should preserve the paper skeleton, reproducibility metadata,
curated evidence, and local scripts. It should not be the only backup of the
full experiment workspace.

The local `CompilerOptimization` tree is much larger than GitHub is suitable
for as a normal Git repository. On 2026-04-29 it was about 138G, with many
files larger than GitHub's normal file limits.

## Push To GitHub

- Paper text and notes: `Paper/`, `paper.md`, `experiment.md`.
- Workspace instructions: `AGENTS.md`.
- Rebuild/run scripts, Dockerfiles, and local wrapper scripts.
- Entire curated case set under `CompilerOptimization/Result/AllUsefulCases/`.
- Full `CompilerOptimization/CompilerResult` trees only for these selected
  targets: `flatbuffers`, `lepton`, `curl`, `libsndfile`, `masscan`, `redis`,
  `tengine`, `zfp`, and `zopfli`.
- Target/tool manifests that record upstream names, URLs, commits, local
  paths, and relevant notes.
- Small patches for locally modified third-party tool source.

## Do Not Push To Normal Git

- `CompilerOptimization/CompilerResult/cJSON/`.
- `CompilerOptimization/CompilerResult` trees for `cjson`, `duckdb`, `flite`,
  `grpc`, `leveldb`, `libco`, `libexpat`, `miniz`, `opencv`, `rapidjson`,
  `rethinkdb`, `tiny-AES-c`, and `zlib`.
- Raw analyzer results outside `CompilerOptimization/Result/AllUsefulCases/`,
  unless they are small top-level summaries or scripts.
- Vendored target source trees under `CompilerOptimization/Target`.
- Vendored analyzer source trees or downloaded archives under
  `CompilerOptimization/Tools`.
- Docker image layers or `docker save` tarballs.

The selected `AllUsefulCases` and `CompilerResult` trees contain files larger
than normal GitHub Git limits. They need Git LFS, external artifact storage, or
another large-file strategy before a GitHub push can succeed.

## Store Elsewhere

Full evidence should be archived as timestamped snapshots with checksums,
outside GitHub:

- full `CompilerOptimization` snapshot as `tar.zst`;
- `sha256sum` manifest for the snapshot;
- Docker image archives from `docker save | zstd`;
- at least one external disk copy and one off-machine/cloud/NAS copy.

GitHub is the index and curated evidence repository. The full artifact archive
is the restoration source of truth.
