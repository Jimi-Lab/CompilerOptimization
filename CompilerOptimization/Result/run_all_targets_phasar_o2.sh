#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/jimi/PaperExperiment/CompilerOptimization/Result"
INNER="/home/jimi/PaperExperiment/CompilerOptimization/Result/run_all_targets_phasar_o2_in_container.sh"

mkdir -p "$ROOT"

docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "/home/jimi/PaperExperiment:/work/PaperExperiment" \
  -v "$INNER:/tmp/run_all_targets_phasar_o2.sh:ro" \
  --entrypoint /bin/bash \
  phasar:nosan \
  /tmp/run_all_targets_phasar_o2.sh | tee "$ROOT/run_all_targets_phasar_o2.log"
