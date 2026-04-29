#!/usr/bin/env bash
set -euo pipefail

export PROFILE_DIR_NAME="phasar-O2-g"
export LOG_DIR_NAME="log"
export SUMMARY_FILE_NAME="phasar_O2_g_linecheck_summary.csv"
export O2G_ONLY="1"
export IFDS_TIMEOUT_SEC="${IFDS_TIMEOUT_SEC:-420}"

bash "/work/PaperExperiment/CompilerOptimization/Result/run_all_targets_phasar_o2_in_container.sh"
