#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/jimi/PaperExperiment/CompilerOptimization/Result"
INNER="/home/jimi/PaperExperiment/CompilerOptimization/Result/run_all_targets_seahorn_O2_g_in_container.sh"

mkdir -p "$ROOT"

docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "/home/jimi/PaperExperiment:/work/PaperExperiment" \
  -v "$INNER:/tmp/run_all_targets_seahorn_O2_g.sh:ro" \
  --entrypoint /bin/bash \
  seahorn/seahorn-llvm14:nightly \
  /tmp/run_all_targets_seahorn_O2_g.sh | tee "$ROOT/run_all_targets_seahorn_O2_g.log"
