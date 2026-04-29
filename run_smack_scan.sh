#!/usr/bin/env bash
set -u

BC_PATH="${BC_PATH:-/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM13-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc}"
REQ_OUT_DIR="${OUT_DIR:-/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/smack/smack-O2-g}"
IMAGE="smackers/smack:latest-full"
ROOT_MOUNT="/home/jimi/PaperExperiment"

OUT_DIR="$REQ_OUT_DIR"
if ! mkdir -p "$OUT_DIR" 2>/dev/null; then
  ALT_BASE="/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/smack"
  mkdir -p "$ALT_BASE" || exit 1
  ALT_OUT="$ALT_BASE/smack-O2-g-fallback-$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$ALT_OUT" || exit 1
  OUT_DIR="$ALT_OUT"
fi

mkdir -p "$OUT_DIR/log/stdout" "$OUT_DIR/log/stderr" "$OUT_DIR/artifacts" "$OUT_DIR/summary" "$OUT_DIR/report"
COMMANDS_LOG="$OUT_DIR/log/commands.log"
STATUS_CSV="$OUT_DIR/summary/smack_status.csv"
OVERVIEW_CSV="$OUT_DIR/summary/overview.csv"
FAIL_INV="$OUT_DIR/summary/failure_inventory.csv"
APPROX_WARN="$OUT_DIR/summary/approximation_warnings.csv"

touch "$COMMANDS_LOG"
printf '%s | %s | %s\n' "$(date -Iseconds)" "script_invocation" "bash run_smack_scan.sh" >> "$COMMANDS_LOG"

HOST_UID="$(id -u)"
HOST_GID="$(id -g)"
BC_IN_CONT="/work${BC_PATH#${ROOT_MOUNT}}"
OUT_IN_CONT="/work${OUT_DIR#${ROOT_MOUNT}}"

run_step() {
  local step="$1"
  local cmd="$2"
  local out="$OUT_DIR/log/stdout/${step}.out"
  local err="$OUT_DIR/log/stderr/${step}.err"
  printf '%s | %s | %s\n' "$(date -Iseconds)" "$step" "$cmd" >> "$COMMANDS_LOG"
  bash -lc "$cmd" >"$out" 2>"$err"
  local rc=$?
  printf '%s\n' "$rc" > "$OUT_DIR/log/${step}.rc"
  return $rc
}

collect_key_line() {
  local step="$1"
  local out="$OUT_DIR/log/stdout/${step}.out"
  local err="$OUT_DIR/log/stderr/${step}.err"
  local key
  key="$(grep -E 'SMACK found an error|SMACK found no errors|SMACK timed out|Traceback|type checking errors|overapproximating|approximating|unsupported|error:' "$out" "$err" 2>/dev/null | head -n 1 | tr '\n' ' ' | sed 's/"/""/g')"
  printf '%s' "$key"
}

classify_run() {
  local step="$1"
  local rc="$2"
  local out="$OUT_DIR/log/stdout/${step}.out"
  local err="$OUT_DIR/log/stderr/${step}.err"

  if [ "$rc" -eq 124 ] || grep -qi 'SMACK timed out' "$out" "$err"; then
    printf 'timeout'
    return
  fi
  if grep -q 'SMACK found an error' "$out" "$err"; then
    printf 'error'
    return
  fi
  if grep -Eqi 'SMACK found no errors|SMACK verified' "$out" "$err"; then
    printf 'verified'
    return
  fi
  if grep -Eqi 'Corral|Boogie|type checking errors|Z3|backend' "$out" "$err"; then
    printf 'backend failure'
    return
  fi
  if grep -Eqi 'unsupported|translation|llvm2bpl|cannot translate' "$out" "$err"; then
    printf 'unsupported / translation failure'
    return
  fi
  printf 'tool failure'
}

record_approx_warnings() {
  local step="$1"
  local out="$OUT_DIR/log/stdout/${step}.out"
  local err="$OUT_DIR/log/stderr/${step}.err"
  grep -Ein 'overapproximating|approximating llvm\.lifetime|can lead to false alarms' "$out" "$err" 2>/dev/null | while IFS= read -r line; do
    local escaped
    escaped="$(printf '%s' "$line" | sed 's/"/""/g')"
    printf '"%s","%s"\n' "$step" "$escaped" >> "$APPROX_WARN"
  done
}

printf 'item,status,detail\n' > "$OVERVIEW_CSV"
printf 'case_id,phase,check,integer_encoding,unroll,verifier,time_limit,outer_timeout,status,rc,stdout_log,stderr_log,key_line\n' > "$STATUS_CSV"
printf 'case_id,category,detail,stdout_log,stderr_log\n' > "$FAIL_INV"
printf 'case_id,warning\n' > "$APPROX_WARN"

run_step pull_image "docker pull \"$IMAGE\""

run_step env_clang_13 "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'clang-13 --version'"
run_step env_llvm_link_13 "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'llvm-link-13 --version'"
run_step env_llvm_dis_13 "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'llvm-dis-13 --version'"
run_step env_smack_version "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'smack --version'"
run_step env_boogie_path "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'command -v boogie'"
run_step env_corral_path "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'command -v corral'"
run_step env_z3_path "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'command -v z3'"

run_step bc_llvm_dis "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'llvm-dis-13 -o /dev/null \"$BC_IN_CONT\"'"
run_step bc_main_check "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'llvm-nm-13 \"$BC_IN_CONT\" | grep \" main$\"'"
run_step bc_undefined_symbols "docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'llvm-nm-13 --undefined-only \"$BC_IN_CONT\"'"

TRANS_STEP="translate_only"
TRANS_CMD="docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'smack --no-verify -bc \"$OUT_IN_CONT/artifacts/smack.init.bc\" -ll \"$OUT_IN_CONT/artifacts/smack.final.ll\" -bpl \"$OUT_IN_CONT/artifacts/smack.bpl\" \"$BC_IN_CONT\"'"
run_step "$TRANS_STEP" "$TRANS_CMD"
TRANS_RC=$(cat "$OUT_DIR/log/${TRANS_STEP}.rc")
TRANS_STATUS=""
if [ "$TRANS_RC" -eq 0 ]; then
  TRANS_STATUS="ok"
else
  if grep -Eqi 'Corral|Boogie|type checking errors' "$OUT_DIR/log/stdout/${TRANS_STEP}.out" "$OUT_DIR/log/stderr/${TRANS_STEP}.err"; then
    TRANS_STATUS="backend/typecheck failure"
  else
    TRANS_STATUS="translation failure"
  fi
fi

printf 'translation,%s,"%s"\n' "$([ "$TRANS_STATUS" = "ok" ] && printf passed || printf failed)" "$TRANS_STATUS" >> "$OVERVIEW_CSV"

if [ "$TRANS_STATUS" != "ok" ]; then
  key_line="$(collect_key_line "$TRANS_STEP")"
  printf '"%s","%s","%s",10,%s,1800,2000,"%s",%s,"%s","%s","%s"\n' \
    "translate_only" "translate" "none" "boogie" "$TRANS_STATUS" "$TRANS_RC" \
    "log/stdout/${TRANS_STEP}.out" "log/stderr/${TRANS_STEP}.err" "$key_line" >> "$STATUS_CSV"
  printf '"%s","%s","%s","%s","%s"\n' "translate_only" "$TRANS_STATUS" "$key_line" "log/stdout/${TRANS_STEP}.out" "log/stderr/${TRANS_STEP}.err" >> "$FAIL_INV"

  cat > "$OUT_DIR/report/final_report.md" <<EOF
# SMACK Static Scan Final Report

## Input
- BC_PATH: $BC_PATH
- Requested OUT_DIR: $REQ_OUT_DIR
- Actual OUT_DIR: $OUT_DIR
- Docker image: $IMAGE

## Translation Check
- Result: $TRANS_STATUS
- Since translation failed, verification matrix was not executed.

## Progress Boundary
- Last successful major step: environment and BC checks
- Failed step: translation-only run
- Reason category: $TRANS_STATUS
- Remaining unfinished items: verification matrix and result classification of scan cases
EOF
  exit 2
fi

printf '"%s","%s","%s","%s",%s,%s,%s,%s,"%s",%s,"%s","%s","%s"\n' \
  "translate_only" "translate" "none" "default" "-" "-" "-" "-" "passed" "$TRANS_RC" \
  "log/stdout/${TRANS_STEP}.out" "log/stderr/${TRANS_STEP}.err" "translation artifacts exported" >> "$STATUS_CSV"

run_case() {
  local case_id="$1"
  local check="$2"
  local encoding="$3"
  local unroll="$4"
  local verifier="$5"
  local time_limit="$6"
  local outer_timeout="$7"

  local step="case_${case_id}"
  local cmd="timeout ${outer_timeout}s docker run --rm -u ${HOST_UID}:${HOST_GID} -v \"$ROOT_MOUNT:/work\" -w /work \"$IMAGE\" bash -lc 'smack --check ${check} --integer-encoding ${encoding} --unroll ${unroll} --verifier ${verifier} --time-limit ${time_limit} \"$BC_IN_CONT\"'"

  run_step "$step" "$cmd"
  local rc
  rc=$(cat "$OUT_DIR/log/${step}.rc")
  local status
  status="$(classify_run "$step" "$rc")"
  local key_line
  key_line="$(collect_key_line "$step")"

  printf '"%s","%s","%s","%s",%s,%s,%s,%s,"%s",%s,"%s","%s","%s"\n' \
    "$case_id" "verify" "$check" "$encoding" "$unroll" "$verifier" "$time_limit" "$outer_timeout" "$status" "$rc" \
    "log/stdout/${step}.out" "log/stderr/${step}.err" "$key_line" >> "$STATUS_CSV"

  record_approx_warnings "$step"

  if [ "$status" != "verified" ]; then
    printf '"%s","%s","%s","%s","%s"\n' "$case_id" "$status" "$key_line" "log/stdout/${step}.out" "log/stderr/${step}.err" >> "$FAIL_INV"
  fi
}

run_case "A1" "assertions" "unbounded-integer" 10 "boogie" 1800 2000
run_case "A2" "memory-safety" "unbounded-integer" 10 "boogie" 1800 2000
run_case "A3" "integer-overflow" "unbounded-integer" 10 "boogie" 1800 2000
run_case "A4" "memory-safety" "unbounded-integer" 16 "boogie" 1800 2000
run_case "A5" "assertions" "bit-vector" 10 "boogie" 1800 2000
run_case "A6" "memory-safety" "bit-vector" 10 "boogie" 1800 2000
run_case "A7" "integer-overflow" "bit-vector" 10 "boogie" 1800 2000
run_case "A8" "memory-safety" "unbounded-integer" 10 "svcomp" 1800 2000

verified_count=$(awk -F',' 'NR>1 && $9 ~ /"verified"/ {c++} END{print c+0}' "$STATUS_CSV")
error_count=$(awk -F',' 'NR>1 && $9 ~ /"error"/ {c++} END{print c+0}' "$STATUS_CSV")
timeout_count=$(awk -F',' 'NR>1 && $9 ~ /"timeout"/ {c++} END{print c+0}' "$STATUS_CSV")
tool_failure_count=$(awk -F',' 'NR>1 && $9 ~ /"tool failure"/ {c++} END{print c+0}' "$STATUS_CSV")
backend_failure_count=$(awk -F',' 'NR>1 && $9 ~ /"backend failure"/ {c++} END{print c+0}' "$STATUS_CSV")
unsup_trans_count=$(awk -F',' 'NR>1 && $9 ~ /"unsupported \/ translation failure"/ {c++} END{print c+0}' "$STATUS_CSV")
approx_count=$(awk -F',' 'NR>1 {c++} END{print c+0}' "$APPROX_WARN")

printf 'verified,%s,number of verified runs\n' "$verified_count" >> "$OVERVIEW_CSV"
printf 'error,%s,number of runs with SMACK found an error\n' "$error_count" >> "$OVERVIEW_CSV"
printf 'timeout,%s,number of timed out runs\n' "$timeout_count" >> "$OVERVIEW_CSV"
printf 'tool failure,%s,number of tool failures\n' "$tool_failure_count" >> "$OVERVIEW_CSV"
printf 'backend failure,%s,number of backend failures\n' "$backend_failure_count" >> "$OVERVIEW_CSV"
printf 'unsupported/translation failure,%s,number of unsupported or translation failures\n' "$unsup_trans_count" >> "$OVERVIEW_CSV"
printf 'approximation warnings,%s,matched approximation warning lines\n' "$approx_count" >> "$OVERVIEW_CSV"

BUG_LINES_FILE="$OUT_DIR/summary/bug_candidates.txt"
NONBUG_LINES_FILE="$OUT_DIR/summary/nonbug_failures.txt"
> "$BUG_LINES_FILE"
> "$NONBUG_LINES_FILE"

while IFS=, read -r case_id phase check enc unroll verifier tlimit otimeout status rc stdout_log stderr_log key_line; do
  [ "$case_id" = "case_id" ] && continue
  clean_case=$(printf '%s' "$case_id" | tr -d '"')
  clean_status=$(printf '%s' "$status" | tr -d '"')
  clean_check=$(printf '%s' "$check" | tr -d '"')
  clean_stdout=$(printf '%s' "$stdout_log" | tr -d '"')
  clean_stderr=$(printf '%s' "$stderr_log" | tr -d '"')
  clean_key=$(printf '%s' "$key_line" | sed 's/^"//; s/"$//')

  if [ "$clean_status" = "error" ]; then
    trace_tail=$(tail -n 8 "$OUT_DIR/$clean_stderr" 2>/dev/null | sed 's/"/""/g' | tr '\n' ' ')
    [ -z "$trace_tail" ] && trace_tail=$(tail -n 8 "$OUT_DIR/$clean_stdout" 2>/dev/null | sed 's/"/""/g' | tr '\n' ' ')
    printf '- case `%s` | check `%s` | logs `%s`, `%s` | key `%s` | trace `%s`\n' "$clean_case" "$clean_check" "$clean_stdout" "$clean_stderr" "$clean_key" "$trace_tail" >> "$BUG_LINES_FILE"
  elif [ "$clean_status" != "verified" ] && [ "$clean_status" != "passed" ]; then
    printf '- case `%s` | status `%s` | logs `%s`, `%s` | detail `%s`\n' "$clean_case" "$clean_status" "$clean_stdout" "$clean_stderr" "$clean_key" >> "$NONBUG_LINES_FILE"
  fi
done < "$STATUS_CSV"

FINAL_CONCLUSION="PASS"
if [ "$error_count" -gt 0 ] && [ "$approx_count" -gt 0 ]; then
  FINAL_CONCLUSION="Found bug candidates, but result quality is limited by approximation warnings"
elif [ "$error_count" -gt 0 ]; then
  FINAL_CONCLUSION="FAIL"
elif [ "$timeout_count" -gt 0 ] || [ "$tool_failure_count" -gt 0 ] || [ "$backend_failure_count" -gt 0 ] || [ "$unsup_trans_count" -gt 0 ]; then
  FINAL_CONCLUSION="PARTIAL PASS"
fi

{
  echo "# SMACK Static Scan Final Report"
  echo
  echo "## 1. 输入信息"
  echo "- BC: $BC_PATH"
  echo "- OUT_DIR(请求): $REQ_OUT_DIR"
  echo "- OUT_DIR(实际): $OUT_DIR"
  echo "- Docker 镜像: $IMAGE"
  echo "- LLVM/SMACK 版本日志: log/stdout/env_*.out"
  echo
  echo "## 2. 扫描矩阵"
  echo "- A1: check=assertions, integer-encoding=unbounded-integer, unroll=10, verifier=boogie, time-limit=1800"
  echo "- A2: check=memory-safety, integer-encoding=unbounded-integer, unroll=10, verifier=boogie, time-limit=1800"
  echo "- A3: check=integer-overflow, integer-encoding=unbounded-integer, unroll=10, verifier=boogie, time-limit=1800"
  echo "- A4: check=memory-safety, integer-encoding=unbounded-integer, unroll=16, verifier=boogie, time-limit=1800"
  echo "- A5: check=assertions, integer-encoding=bit-vector, unroll=10, verifier=boogie, time-limit=1800"
  echo "- A6: check=memory-safety, integer-encoding=bit-vector, unroll=10, verifier=boogie, time-limit=1800"
  echo "- A7: check=integer-overflow, integer-encoding=bit-vector, unroll=10, verifier=boogie, time-limit=1800"
  echo "- A8: check=memory-safety, integer-encoding=unbounded-integer, unroll=10, verifier=svcomp, time-limit=1800"
  echo
  echo "## 3. 结果总览"
  echo "- verified: $verified_count"
  echo "- error: $error_count"
  echo "- timeout: $timeout_count"
  echo "- tool failure: $tool_failure_count"
  echo "- backend failure: $backend_failure_count"
  echo "- unsupported / translation failure: $unsup_trans_count"
  echo
  echo "## 4. Bug 候选列表"
  if [ -s "$BUG_LINES_FILE" ]; then
    cat "$BUG_LINES_FILE"
  else
    echo "- 无（未出现 `SMACK found an error`）"
  fi
  echo
  echo "## 5. 非 bug 失败列表"
  if [ -s "$NONBUG_LINES_FILE" ]; then
    cat "$NONBUG_LINES_FILE"
  else
    echo "- 无"
  fi
  echo
  echo "## 6. 最终结论"
  echo "- $FINAL_CONCLUSION"
} > "$OUT_DIR/report/final_report.md"

if [ "$OUT_DIR" != "$REQ_OUT_DIR" ]; then
  printf 'output_path,warning,"requested OUT_DIR not writable; used fallback %s"\n' "$OUT_DIR" >> "$OVERVIEW_CSV"
fi

exit 0
