#!/usr/bin/env bash
set -u

BC_PATH="/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/artifacts/flatbuffers_flatc_O2_g.bc"
REQUESTED_OUT_DIR="/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/smack/smack-O2-g"
IMAGE="smackers/smack:latest-full"
WORK_ROOT="/home/jimi/PaperExperiment"

OUT_DIR="$REQUESTED_OUT_DIR"
if ! mkdir -p "$OUT_DIR" 2>/dev/null || ! : > "$OUT_DIR/.write_test" 2>/dev/null; then
  OUT_DIR="/tmp/smack-O2-g-$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$OUT_DIR"
  FALLBACK_REASON="requested output directory is not writable"
else
  FALLBACK_REASON=""
fi
rm -f "$OUT_DIR/.write_test"

LOG_DIR="$OUT_DIR/log"
ART_DIR="$OUT_DIR/artifacts"
SUM_DIR="$OUT_DIR/summary"
REP_DIR="$OUT_DIR/report"
mkdir -p "$LOG_DIR" "$ART_DIR" "$SUM_DIR" "$REP_DIR"

COMMANDS_LOG="$LOG_DIR/commands.log"
: > "$COMMANDS_LOG"
printf '%s | %s\n' "$(date '+%F %T')" "[script-start] $0" >> "$COMMANDS_LOG"

record_raw_cmd() {
  printf '%s | %s\n' "$(date '+%F %T')" "$1" >> "$COMMANDS_LOG"
}

run_step() {
  local step="$1"
  shift
  local cmd="$*"
  local out="$LOG_DIR/${step}.stdout.log"
  local err="$LOG_DIR/${step}.stderr.log"
  record_raw_cmd "$cmd"
  bash -lc "$cmd" >"$out" 2>"$err"
  local rc=$?
  printf '%s\n' "$rc" > "$LOG_DIR/${step}.exitcode"
  return 0
}

# Record commands already executed before this script created commands.log.
record_raw_cmd "[executed-earlier] ls /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/artifacts"
record_raw_cmd "[executed-earlier] ls /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers"
record_raw_cmd "[executed-earlier] ls /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/smack"
record_raw_cmd "[executed-earlier] ls -la /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/smack/smack-O2-g"

record_raw_cmd "mkdir -p $LOG_DIR $ART_DIR $SUM_DIR $REP_DIR"
record_raw_cmd "rm -f $OUT_DIR/.write_test"

DOCKER_BASE="docker run --rm -u $(id -u):$(id -g) -v \"$WORK_ROOT:/work\" -w /work \"$IMAGE\" bash -lc"
BC_IN_CONTAINER="/work${BC_PATH#$WORK_ROOT}"
OUT_IN_CONTAINER="/work${OUT_DIR#$WORK_ROOT}"

run_step "host_docker_version" "docker --version"
run_step "host_docker_pull" "docker pull \"$IMAGE\""

run_step "env_clang13_version" "$DOCKER_BASE \"clang-13 --version\""
run_step "env_llvm_link13_version" "$DOCKER_BASE \"llvm-link-13 --version\""
run_step "env_llvm_dis13_version" "$DOCKER_BASE \"llvm-dis-13 --version\""
run_step "env_smack_version" "$DOCKER_BASE \"smack --version\""
run_step "env_boogie_path" "$DOCKER_BASE \"command -v boogie\""
run_step "env_corral_path" "$DOCKER_BASE \"command -v corral\""
run_step "env_z3_path" "$DOCKER_BASE \"command -v z3\""
run_step "env_llvm_nm13_version" "$DOCKER_BASE \"llvm-nm-13 --version\""

run_step "bc_exists" "$DOCKER_BASE \"test -f '$BC_IN_CONTAINER' && ls -l '$BC_IN_CONTAINER'\""
run_step "bc_has_main" "$DOCKER_BASE \"llvm-nm-13 '$BC_IN_CONTAINER' | grep ' main$'\""
run_step "bc_undefined_symbols" "$DOCKER_BASE \"llvm-nm-13 --undefined-only '$BC_IN_CONTAINER'\""
run_step "bc_llvm_disassemble" "$DOCKER_BASE \"llvm-dis-13 '$BC_IN_CONTAINER' -o /tmp/smack_precheck.ll && ls -l /tmp/smack_precheck.ll\""

run_step "smack_help" "$DOCKER_BASE \"smack --help\""

TRANSLATE_CMD="$DOCKER_BASE \"mkdir -p '$OUT_IN_CONTAINER/artifacts' && cd '$OUT_IN_CONTAINER/artifacts' && smack --debug --check=assertions --integer-encoding=unbounded-integer --unroll=10 --time-limit=1800 '$BC_IN_CONTAINER'\""
run_step "translate_probe" "$TRANSLATE_CMD"
run_step "translate_artifacts_listing" "ls -la '$ART_DIR'"

if [ -f "$ART_DIR/smack.init.bc" ] && [ -f "$ART_DIR/smack.final.ll" ] && [ -f "$ART_DIR/smack.bpl" ]; then
  run_step "translate_artifacts_ready" "ls -l '$ART_DIR/smack.init.bc' '$ART_DIR/smack.final.ll' '$ART_DIR/smack.bpl'"
else
  run_step "translate_artifacts_missing" "ls -la '$ART_DIR'"
fi

translate_status="ok"
record_raw_cmd "grep -Eq 'Traceback|type checking errors|SMACK timed out|error:' $LOG_DIR/translate_probe.stderr.log $LOG_DIR/translate_probe.stdout.log"
if grep -Eq "Traceback|type checking errors|SMACK timed out|error:" "$LOG_DIR/translate_probe.stderr.log" "$LOG_DIR/translate_probe.stdout.log"; then
  translate_status="failed"
fi
if [ ! -f "$ART_DIR/smack.init.bc" ] || [ ! -f "$ART_DIR/smack.final.ll" ] || [ ! -f "$ART_DIR/smack.bpl" ]; then
  translate_status="failed"
fi

record_raw_cmd "write $SUM_DIR/matrix.tsv"
cat > "$SUM_DIR/matrix.tsv" << 'EOF'
case_id	check	integer_encoding	verifier	unroll	time_limit
A1	assertions	unbounded-integer	corral	10	1800
A2	memory-safety	unbounded-integer	corral	10	1800
A3	integer-overflow	unbounded-integer	corral	10	1800
A4	memory-safety	unbounded-integer	corral	16	1800
A5	assertions	bit-vector	corral	10	1800
A6	memory-safety	bit-vector	corral	10	1800
A7	integer-overflow	bit-vector	corral	10	1800
A8	memory-safety	unbounded-integer	svcomp	10	1800
EOF

if [ "$translate_status" = "ok" ]; then
  while IFS=$'\t' read -r case_id check integer_encoding verifier unroll time_limit; do
    if [ "$case_id" = "case_id" ]; then
      continue
    fi
    step="scan_${case_id}"
    cmd="$DOCKER_BASE \"mkdir -p '$OUT_IN_CONTAINER/artifacts/$case_id' && cd '$OUT_IN_CONTAINER/artifacts/$case_id' && smack --debug --check=$check --integer-encoding=$integer_encoding --verifier=$verifier --unroll=$unroll --time-limit=$time_limit '$BC_IN_CONTAINER'\""
    run_step "$step" "$cmd"
  done < "$SUM_DIR/matrix.tsv"
fi

record_raw_cmd "python3 - <summary/report generator>"
python3 - "$OUT_DIR" "$BC_PATH" "$REQUESTED_OUT_DIR" "$IMAGE" "$FALLBACK_REASON" << 'PY'
import csv
import os
import re
import sys
from pathlib import Path

out_dir = Path(sys.argv[1])
bc_path = sys.argv[2]
requested_out = sys.argv[3]
image = sys.argv[4]
fallback_reason = sys.argv[5]
log_dir = out_dir / "log"
sum_dir = out_dir / "summary"
rep_dir = out_dir / "report"
art_dir = out_dir / "artifacts"

def read_text(p):
    try:
        return p.read_text(errors="replace")
    except Exception:
        return ""

matrix = []
matrix_tsv = sum_dir / "matrix.tsv"
if matrix_tsv.exists():
    with matrix_tsv.open() as f:
        rows = [line.rstrip("\n").split("\t") for line in f if line.strip()]
    hdr = rows[0]
    for r in rows[1:]:
        matrix.append(dict(zip(hdr, r)))

def classify(stdout, stderr, exitcode):
    text = stdout + "\n" + stderr
    if "SMACK found an error:" in text:
        return "error"
    if "SMACK found no errors" in text:
        return "verified"
    if "SMACK timed out" in text:
        return "timeout"
    if re.search(r"type checking errors|Corral.*type checking", text, re.I):
        return "backend failure"
    if re.search(r"Boogie.*error|Z3.*error|backend", text, re.I):
        return "backend failure"
    if re.search(r"unsupported|not supported|translation", text, re.I):
        return "unsupported / translation failure"
    if "Traceback" in text or exitcode not in (0,):
        return "tool failure"
    return "tool failure"

overview_rows = []
failure_rows = []
bug_candidates = []
approx_warnings = []

translate_stdout = read_text(log_dir / "translate_probe.stdout.log")
translate_stderr = read_text(log_dir / "translate_probe.stderr.log")
translate_exit = int(read_text(log_dir / "translate_probe.exitcode") or "0")
translate_status = classify(translate_stdout, translate_stderr, translate_exit)
if "SMACK found no errors" in translate_stdout + translate_stderr and translate_status == "verified":
    translate_status = "verified"

for m in matrix:
    case_id = m["case_id"]
    step = f"scan_{case_id}"
    so = log_dir / f"{step}.stdout.log"
    se = log_dir / f"{step}.stderr.log"
    ec = log_dir / f"{step}.exitcode"
    if not so.exists() and not se.exists() and translate_status in ("tool failure", "backend failure", "unsupported / translation failure"):
        status = "translation failure"
        exitcode = "NA"
        stdout = ""
        stderr = "translation stage failed; scans skipped"
    else:
        stdout = read_text(so)
        stderr = read_text(se)
        exitcode = int(read_text(ec) or "0") if ec.exists() else 0
        status = classify(stdout, stderr, exitcode)
    key_line = ""
    for line in (stdout + "\n" + stderr).splitlines():
        if any(k in line for k in ["SMACK found an error:", "SMACK timed out", "type checking", "Traceback", "unsupported", "not supported"]):
            key_line = line.strip()
            break
    overview_rows.append({
        "case_id": case_id,
        "check": m["check"],
        "integer_encoding": m["integer_encoding"],
        "verifier": m["verifier"],
        "unroll": m["unroll"],
        "time_limit": m["time_limit"],
        "status": status,
        "exit_code": exitcode,
        "stdout_log": f"log/{step}.stdout.log",
        "stderr_log": f"log/{step}.stderr.log",
        "key_line": key_line,
    })
    merged = stdout + "\n" + stderr
    for line in merged.splitlines():
        if "SMACK found an error:" in line:
            idx = merged.splitlines().index(line)
            tail = "\n".join(merged.splitlines()[max(0, idx-2):idx+6])
            bug_candidates.append((m, line.strip(), tail))
            break
    for line in merged.splitlines():
        if "overapproximating" in line or "approximating llvm.lifetime" in line or "can lead to false alarms" in line:
            approx_warnings.append((case_id, line.strip()))
    if status != "verified":
        failure_rows.append({
            "case_id": case_id,
            "status": status,
            "reason": key_line or "No definitive success marker",
            "stdout_log": f"log/{step}.stdout.log",
            "stderr_log": f"log/{step}.stderr.log",
        })

with (sum_dir / "smack_status.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["case_id","check","integer_encoding","verifier","unroll","time_limit","status","exit_code","stdout_log","stderr_log","key_line"])
    w.writeheader()
    w.writerows(overview_rows)

counts = {"verified":0,"error":0,"timeout":0,"tool failure":0,"backend failure":0,"unsupported / translation failure":0,"translation failure":0}
for r in overview_rows:
    counts[r["status"]] = counts.get(r["status"],0)+1

with (sum_dir / "overview.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["metric","value"])
    for k in ["verified","error","timeout","tool failure","backend failure","unsupported / translation failure","translation failure"]:
        w.writerow([k, counts.get(k,0)])
    w.writerow(["requested_out_dir", requested_out])
    w.writerow(["actual_out_dir", str(out_dir)])
    w.writerow(["out_dir_fallback_reason", fallback_reason or "none"])

with (sum_dir / "failure_inventory.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["case_id","status","reason","stdout_log","stderr_log"])
    w.writeheader()
    w.writerows(failure_rows)

def read_first_line(name):
    p = log_dir / name
    txt = read_text(p).strip().splitlines()
    return txt[0] if txt else ""

clang_v = read_first_line("env_clang13_version.stdout.log")
llvm_link_v = read_first_line("env_llvm_link13_version.stdout.log")
llvm_dis_v = read_first_line("env_llvm_dis13_version.stdout.log")
smack_v = read_first_line("env_smack_version.stdout.log")
boogie_p = read_first_line("env_boogie_path.stdout.log")
corral_p = read_first_line("env_corral_path.stdout.log")
z3_p = read_first_line("env_z3_path.stdout.log")

main_exists = bool(read_text(log_dir / "bc_has_main.stdout.log").strip())
undef_syms = read_text(log_dir / "bc_undefined_symbols.stdout.log").strip().splitlines()

if counts.get("error",0) > 0:
    conclusion = "Found bug candidates, but result quality may be limited by approximation warnings if present"
elif counts.get("verified",0) == len(overview_rows) and len(overview_rows) > 0:
    conclusion = "PASS"
elif counts.get("verified",0) > 0:
    conclusion = "PARTIAL PASS"
else:
    conclusion = "No verified bug candidates; multiple backend/tool failures prevent strong conclusions"

report = []
report.append("# SMACK Static Scan Final Report")
report.append("")
report.append("## 1. Input Information")
report.append(f"- Bitcode: `{bc_path}`")
report.append(f"- Requested output directory: `{requested_out}`")
report.append(f"- Actual output directory: `{out_dir}`")
report.append(f"- Docker image: `{image}`")
report.append(f"- LLVM/SMACK versions: clang13=`{clang_v}`; llvm-link13=`{llvm_link_v}`; llvm-dis13=`{llvm_dis_v}`; smack=`{smack_v}`")
report.append(f"- boogie/corral/z3 in PATH: boogie=`{boogie_p or 'N/A'}`, corral=`{corral_p or 'N/A'}`, z3=`{z3_p or 'N/A'}`")
if fallback_reason:
    report.append(f"- Output fallback reason: {fallback_reason}")
report.append("")
report.append("## 2. Scan Matrix")
for r in overview_rows:
    report.append(f"- {r['case_id']}: check={r['check']}, integer_encoding={r['integer_encoding']}, verifier={r['verifier']}, unroll={r['unroll']}, time_limit={r['time_limit']}, status={r['status']}")
report.append("")
report.append("## 3. Overall Result")
for k in ["verified","error","timeout","tool failure","backend failure","unsupported / translation failure","translation failure"]:
    report.append(f"- {k}: {counts.get(k,0)}")
report.append("")
report.append("## 4. Bug Candidates")
if bug_candidates:
    for idx, (m, line, tail) in enumerate(bug_candidates, 1):
        logp = f"log/scan_{m['case_id']}.stdout.log"
        report.append(f"- Bug #{idx}: check={m['check']}, params=(encoding={m['integer_encoding']}, verifier={m['verifier']}, unroll={m['unroll']}, timeout={m['time_limit']}), log=`{logp}`, key_line=`{line}`")
        report.append("  - Trace tail:")
        report.append("```text")
        report.append(tail)
        report.append("```")
else:
    report.append("- No `SMACK found an error:` lines were observed.")
report.append("")
report.append("## 5. Non-bug Failures and Diagnostics")
if failure_rows:
    for r in failure_rows:
        report.append(f"- {r['case_id']}: status={r['status']}, reason={r['reason']}, stdout=`{r['stdout_log']}`, stderr=`{r['stderr_log']}`")
else:
    report.append("- None")
report.append(f"- BC `main` present: {main_exists}")
report.append(f"- Undefined symbols count: {len([x for x in undef_syms if x.strip()])}")
if approx_warnings:
    report.append("- Approximation warnings (may imply false positives/negatives):")
    for c, w in approx_warnings[:20]:
        report.append(f"  - {c}: {w}")
else:
    report.append("- No approximation warning pattern captured by this run parser.")
report.append("")
report.append("## 6. Final Conclusion")
report.append(f"- {conclusion}")

(rep_dir / "final_report.md").write_text("\n".join(report) + "\n")
PY

record_raw_cmd "printf '%s' $OUT_DIR > $SUM_DIR/actual_out_dir.txt"
printf '%s\n' "$OUT_DIR" > "$SUM_DIR/actual_out_dir.txt"
record_raw_cmd "echo DONE"
echo "DONE"
