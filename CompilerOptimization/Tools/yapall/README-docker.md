# Yapall LLVM14 Docker

This image is for reproducible BC-level yapall scans in the paper experiments.
It builds the patched local yapall source against LLVM 14 and installs:

- `/opt/yapall/bin/yapall`
- `/opt/yapall/signatures.json`

Use this image only for LLVM 14 bitcode, such as artifacts under
`CompilerOptimization/CompilerResult/<target>/LLVM14-*`. If a target was
compiled by a different LLVM major version, build a matching yapall image for
that LLVM version before scanning it.

## Build

Run from `/home/jimi/PaperExperiment`:

```bash
docker build \
  -f CompilerOptimization/Tools/yapall/Dockerfile.llvm14 \
  -t yapall:llvm14 \
  CompilerOptimization/Tools/yapall
```

The Docker build context is intentionally `CompilerOptimization/Tools/yapall`
so the image captures the patched local yapall source used by this workspace.

## Smoke Test

```bash
docker run --rm yapall:llvm14 --version
```

## Scan One BC

```bash
docker run --rm \
  -v /home/jimi/PaperExperiment:/work \
  -w /work \
  yapall:llvm14 \
  --metrics \
  --quiet \
  --check default \
  --contexts 0 \
  --signatures /opt/yapall/signatures.json \
  /work/CompilerOptimization/CompilerResult/zopfli/LLVM14-O2-g/artifacts/zopfli_O2_g_zopfli_only.bc
```

## Batch Scan With The Matrix Runner

The workspace runner can invoke this Docker image directly and will reject an
obvious LLVM-version mismatch by default:

```bash
YAPALL_DOCKER_IMAGE=yapall:llvm14 \
TARGET=libsndfile \
UNIVERSE=O2 \
COMPILER_UNIVERSE=LLVM14-O2-g \
CONTEXTS=0 \
MODES=subset \
DEFAULT_TIMEOUT=600 \
bash CompilerOptimization/Result/yapall/run_yapall_matrix.sh
```

For a linked-bitcode-only scan, pass `INPUT_BC`:

```bash
YAPALL_DOCKER_IMAGE=yapall:llvm14 \
TARGET=masscan \
UNIVERSE=O2 \
COMPILER_UNIVERSE=LLVM14-O2-g \
INPUT_BC=/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/masscan/LLVM14-O2-g/artifacts/masscan_O2_g.bc \
CONTEXTS=0 \
MODES=subset \
DEFAULT_TIMEOUT=600 \
bash CompilerOptimization/Result/yapall/run_yapall_matrix.sh
```

The output contains:

- `metrics`: aggregate counts such as `invalid loads` and `invalid stores`.
- `issues`: normalized candidate rows in `kind<TAB>operand<TAB>allocation`.

These are IR-level pointer-analysis candidate signals, not confirmed source
bugs. For paper cases, compare O0/O2/O2-noinline and map candidate IR
instructions back through debug metadata before assigning labels such as
`FP-LocationDrift`, `FP-PathInfeasible`, or `Timeout/TooComplex`.
