#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/jimi/PaperExperiment/CompilerOptimization/Result"

run_one() {
  local project="$1"
  local source_root="$2"
  local bc_name="$3"

  local base="$ROOT/$project/phasar/phasar-O2-g"
  local log_dir="$base/log"
  local runs_dir="$base/runs/ifds-uninit"
  local status_dir="$base/status"
  local bc_file="$base/artifacts/$bc_name"
  local cmd_log="$log_dir/commands.log"
  local proc_log="$log_dir/project.log"

  mkdir -p "$log_dir" "$runs_dir" "$status_dir"

  local start_utc start_epoch
  start_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  start_epoch=$(date +%s)

  {
    echo "[NO_TIMEOUT] project=$project"
    echo "[NO_TIMEOUT] start_utc=$start_utc"
    echo "[NO_TIMEOUT] source_root=$source_root"
    echo "[NO_TIMEOUT] bc_file=$bc_file"
  } >> "$proc_log"

  local cmd="docker run --rm --user \"$(id -u):$(id -g)\" -v \"/home/jimi/PaperExperiment:/work/PaperExperiment\" --workdir \"/work/PaperExperiment/CompilerOptimization/Result/$project/phasar/phasar-O2-g\" --entrypoint /bin/bash phasar:nosan -lc 'set -euo pipefail; phasar-cli -m artifacts/$bc_name -D ifds-uninit -P basic -C otf -E __ALL__ --emit-raw-results --emit-text-report --emit-stats --emit-statistics-as-json --out runs/ifds-uninit'"
  printf '[%s] %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$cmd" >> "$cmd_log"

  set +e
  eval "$cmd" > "$log_dir/ifds-uninit.no_timeout.stdout.log" 2> "$log_dir/ifds-uninit.no_timeout.stderr.log"
  local ec=$?
  set -e

  local end_utc end_epoch elapsed
  end_utc=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  end_epoch=$(date +%s)
  elapsed=$((end_epoch-start_epoch))

  echo "[NO_TIMEOUT] end_utc=$end_utc" >> "$proc_log"
  echo "[NO_TIMEOUT] exit_code=$ec" >> "$proc_log"
  echo "[NO_TIMEOUT] elapsed_sec=$elapsed" >> "$proc_log"

  local latest_run
  latest_run=$(RUNROOT="$runs_dir" python3 - <<'PYEOF'
from pathlib import Path
import os
runroot = Path(os.environ['RUNROOT'])
subs = [p for p in runroot.iterdir() if p.is_dir()]
subs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
print(subs[0] if subs else '')
PYEOF
)
  echo "[NO_TIMEOUT] latest_run=$latest_run" >> "$proc_log"

  if [ -n "$latest_run" ] && [ -f "$latest_run/psr-report.txt" ]; then
    REPORT="$latest_run/psr-report.txt" SOURCE_ROOT="$source_root" OUT_CSV="$runs_dir/target_linecheck.csv" OUT_JSON="$runs_dir/target_linecheck.json" python3 - <<'PYEOF'
import csv
import json
import os
import re
from pathlib import Path

report = Path(os.environ['REPORT'])
source_root = str(Path(os.environ['SOURCE_ROOT']).resolve()) + '/'
out_csv = Path(os.environ['OUT_CSV'])
out_json = Path(os.environ['OUT_JSON'])
text = report.read_text(encoding='utf-8', errors='ignore').splitlines()
use_header = re.compile(r'^-+\s+(\d+)\. Use')
rows = []
cur = None
for ln in text:
  m = use_header.match(ln)
  if m:
    if cur:
      rows.append(cur)
    cur = {'case': int(m.group(1)), 'file': None, 'line': None, 'source': ''}
    continue
  if cur is None:
    continue
  if ln.startswith('File'):
    cur['file'] = ln.split(':',1)[1].strip()
  elif ln.startswith('Line'):
    try:
      cur['line'] = int(ln.split(':',1)[1].strip())
    except Exception:
      cur['line'] = None
  elif ln.startswith('Source code'):
    cur['source'] = ln.split(':',1)[1].strip()
if cur:
  rows.append(cur)

out = []
for r in rows:
  f = r['file'] or ''
  if not f.startswith(source_root):
    continue
  rel = f[len(source_root):]
  hp = Path(source_root) / rel
  status = 'unknown'
  reason = ''
  actual = ''
  line = r['line'] or 0
  if not hp.exists():
    status = 'missing_file'
    reason = 'file not found'
  else:
    src_lines = hp.read_text(encoding='utf-8', errors='ignore').splitlines()
    if line < 1 or line > len(src_lines):
      status = 'line_oob'
      reason = f'line {line} out of range (1..{len(src_lines)})'
    else:
      actual = src_lines[line-1]
      if actual.strip() == (r['source'] or '').strip():
        status = 'match'
      else:
        status = 'mismatch'
        reason = 'source text mismatch'
  out.append({
    'case': r['case'],
    'file': rel,
    'line': line,
    'status': status,
    'report_source': r['source'],
    'actual_source': actual,
    'reason': reason,
  })

out_json.write_text(json.dumps(out, indent=2), encoding='utf-8')
with out_csv.open('w', newline='', encoding='utf-8') as f:
  w = csv.DictWriter(f, fieldnames=['case','file','line','status','report_source','actual_source','reason'])
  w.writeheader()
  w.writerows(out)
print('linecheck_rows', len(out))
PYEOF
  fi

  if [ "$ec" -eq 0 ]; then
    echo "analysis,exit_code,status,elapsed_sec" > "$log_dir/summary.csv"
    echo "ifds-uninit,0,ok,$elapsed" >> "$log_dir/summary.csv"
    {
      echo "success_utc=$end_utc"
      echo "run_dir=$latest_run"
      echo "exit_code=0"
      echo "mode=no_timeout"
    } > "$status_dir/success.marker"
    rm -f "$status_dir/failed.marker"
  else
    echo "analysis,exit_code,status,elapsed_sec" > "$log_dir/summary.csv"
    echo "ifds-uninit,$ec,error_or_timeout,$elapsed" >> "$log_dir/summary.csv"
    {
      echo "failed_utc=$end_utc"
      echo "exit_code=$ec"
      echo "mode=no_timeout"
    } > "$status_dir/failed.marker"
  fi
}

run_one "tengine" "/home/jimi/PaperExperiment/CompilerOptimization/Target/Tengine" "tengine_O2_g.bc"
run_one "lepton" "/home/jimi/PaperExperiment/CompilerOptimization/Target/lepton" "lepton_O2_g.bc"

python3 - <<'PYEOF'
import csv
from pathlib import Path

result_root = Path('/home/jimi/PaperExperiment/CompilerOptimization/Result')
projects=['curl','tengine','wasmedge','duckdb','flatbuffers','flite','grpc','lepton','leveldb','libco','libsndfile','masscan','opencv','rapidjson','redis','rethinkdb','zfp','zopfli']

summary = result_root / 'phasar_O2_g_linecheck_summary.csv'
rows=[]
for p in projects:
  csv_path = result_root / p / 'phasar' / 'phasar-O2-g' / 'runs' / 'ifds-uninit' / 'target_linecheck.csv'
  if not csv_path.exists():
    continue
  total=match=mismatch=line_oob=0
  with csv_path.open(newline='', encoding='utf-8') as f:
    r=csv.DictReader(f)
    for row in r:
      total += 1
      st=row.get('status','')
      if st=='match': match += 1
      elif st=='mismatch': mismatch += 1
      elif st=='line_oob': line_oob += 1
  oob_rate = (line_oob/total*100.0) if total else 0.0
  rows.append({'project':p,'total_uses':total,'match':match,'mismatch':mismatch,'line_oob':line_oob,'oob_rate':f'{oob_rate:.2f}'})

rows.sort(key=lambda x: x['project'])
with summary.open('w', newline='', encoding='utf-8') as f:
  w=csv.DictWriter(f, fieldnames=['project','total_uses','match','mismatch','line_oob','oob_rate'])
  w.writeheader(); w.writerows(rows)

status_csv = result_root / 'phasar_O2_g_project_status.csv'
rows=[]
for p in projects:
  o2 = result_root / p / 'phasar' / 'phasar-O2-g'
  status='missing_dir'; ifds_status=''; ifds_exit=''; reason=''; has_report='0'
  if o2.exists():
    status='none'
    sm=o2/'status'/'success.marker'
    fm=o2/'status'/'failed.marker'
    if sm.exists(): status='success'
    elif fm.exists():
      status='failed'
      reason=fm.read_text(encoding='utf-8',errors='ignore').strip().replace('\n',' | ')
    s=o2/'log'/'summary.csv'
    if s.exists():
      rr=list(csv.DictReader(s.open()))
      for r in rr:
        if r.get('analysis')=='ifds-uninit':
          ifds_status=r.get('status',''); ifds_exit=r.get('exit_code','')
    run=o2/'runs'/'ifds-uninit'
    if run.exists():
      dirs=[d for d in run.iterdir() if d.is_dir()]
      dirs.sort(key=lambda d:d.stat().st_mtime, reverse=True)
      if dirs and (dirs[0]/'psr-report.txt').exists(): has_report='1'
  rows.append({'project':p,'status':status,'ifds_status':ifds_status,'ifds_exit':ifds_exit,'has_report':has_report,'reason':reason})

with status_csv.open('w', newline='', encoding='utf-8') as f:
  w=csv.DictWriter(f, fieldnames=['project','status','ifds_status','ifds_exit','has_report','reason'])
  w.writeheader(); w.writerows(rows)
PYEOF
