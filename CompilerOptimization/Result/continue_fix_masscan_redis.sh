#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/jimi/PaperExperiment/CompilerOptimization/Result"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

run_container() {
  local cmd="$1"
  local cmdlog="$2"
  local prolog="$3"
  printf '[%s] %s\n' "$(ts)" "docker run --rm --user \"$(id -u):$(id -g)\" -v \"/home/jimi/PaperExperiment:/work/PaperExperiment\" --workdir \"/work/PaperExperiment\" --entrypoint /bin/bash phasar:nosan -lc '$cmd'" >> "$cmdlog"
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    -v "/home/jimi/PaperExperiment:/work/PaperExperiment" \
    --workdir "/work/PaperExperiment" \
    --entrypoint /bin/bash \
    phasar:nosan \
    -lc "$cmd" >> "$prolog" 2>&1
}

generate_bc_from_dryrun_in_container() {
  local project="$1"
  local srcdir_work="$2"
  local o2dir_work="$3"
  local cmdlog="$4"
  local prolog="$5"
  local py="import hashlib, re, shlex, subprocess\nfrom pathlib import Path\no2dir=Path('${o2dir_work}')\nsrcdir=Path('${srcdir_work}')\ndryrun=o2dir/'log'/'make_dryrun.log'\nobjdir=o2dir/'artifacts'/'bc_objs'\nlist_path=o2dir/'artifacts'/'bc_files.list'\ntext=dryrun.read_text(encoding='utf-8',errors='ignore').splitlines()\nclang_frag_re=re.compile(r'(?:^|;)\\s*(?:/usr/bin/)?clang(?:\\+\\+)?-?16\\b[^;]*\\s-c\\s[^;]*')\nlink_frag_re=re.compile(r'(?:^|;)\\s*(?:/usr/bin/)?clang(?:\\+\\+)?-?16\\b[^;]*\\s-o\\s+[^;]+')\nlink_objs=[]\nfor line in text:\n  for m in link_frag_re.finditer(line):\n    frag=m.group(0).lstrip(';').strip()\n    try:toks=shlex.split(frag)\n    except Exception: continue\n    objs=[Path(t).name for t in toks if t.endswith('.o')]\n    if objs: link_objs.append(objs)\nselected_obj_set=set(max(link_objs,key=len)) if link_objs else None\nexclude_marks=('/test/','/tests/','/benchmark/','/bench/','/examples/','/example/','/docs/','/fuzz/')\nseen_src=set(); outs=[]\nfor i,line in enumerate(text):\n  for m in clang_frag_re.finditer(line):\n    frag=m.group(0).lstrip(';').strip()\n    try:toks=shlex.split(frag)\n    except Exception: continue\n    out_obj=None\n    for j,t in enumerate(toks):\n      if t=='-o' and j+1<len(toks): out_obj=Path(toks[j+1]).name; break\n      if t.startswith('-o') and t!='-o': out_obj=Path(t[2:]).name; break\n    if selected_obj_set and out_obj and out_obj not in selected_obj_set: continue\n    src=None\n    for t in reversed(toks):\n      if t.endswith(('.c','.cc','.cpp','.cxx')): src=t; break\n    if not src: continue\n    src_abs=str((srcdir/src).resolve()) if not Path(src).is_absolute() else str(Path(src).resolve())\n    lsrc=src_abs.lower()\n    if any(m in lsrc for m in exclude_marks): continue\n    if src_abs in seen_src: continue\n    seen_src.add(src_abs)\n    out_bc=objdir/(hashlib.sha1((str(i)+'|'+src_abs).encode()).hexdigest()[:16]+'.bc')\n    new=[]; skip=False\n    for t in toks:\n      if skip: skip=False; continue\n      if t=='-o': skip=True; continue\n      if t.startswith('-o') and t!='-o': continue\n      if t in ('-MMD','-MD'): continue\n      if t in ('-MF','-MT','-MQ'): skip=True; continue\n      new.append(t)\n    if '-c' not in new: new.append('-c')\n    new.extend(['-emit-llvm','-o',str(out_bc)])\n    try:\n      subprocess.run(new,cwd=srcdir,check=True)\n      outs.append(str(out_bc))\n    except subprocess.CalledProcessError:\n      pass\nwith list_path.open('w') as f:\n  for p in outs: f.write(p+'\\n')\nprint('project','${project}')\nprint('dryrun_lines',len(text))\nprint('selected_obj_count',len(selected_obj_set) if selected_obj_set else 0)\nprint('selected_sources',len(seen_src))\nprint('generated_bc',len(outs))"
  run_container "python3 -c \"${py}\"" "$cmdlog" "$prolog"
}

link_and_scan() {
  local project="$1"
  local o2dir_host="$2"
  local o2dir_work="$3"
  local bcname="$4"
  local source_root_host="$5"

  local cmdlog="$o2dir_host/log/commands.log"
  local prolog="$o2dir_host/log/project.log"
  local summary="$o2dir_host/log/summary.csv"
  local runroot="$o2dir_host/runs/ifds-uninit"

  run_container "python3 -c \"import subprocess; from pathlib import Path; art=Path('${o2dir_work}/artifacts'); files=[x.strip() for x in (art/'bc_files.list').read_text().splitlines() if x.strip()]; subprocess.run(['/usr/lib/llvm-16/bin/llvm-link',*files,'-o',str(art/'${bcname}.bc')],check=True); subprocess.run(['/usr/lib/llvm-16/bin/llvm-dis',str(art/'${bcname}.bc'),'-o',str(art/'${bcname}.ll')],check=True); print('linked',art/'${bcname}.bc')\"" "$cmdlog" "$prolog"

  python3 - <<PY > "$o2dir_host/log/verify.log" 2>&1
from pathlib import Path
ll=Path('$o2dir_host/artifacts/${bcname}.ll')
t=ll.read_text(encoding='utf-8',errors='ignore')
print('phi:',t.count('= phi '))
print('alloca:',t.count('alloca '))
print('debug:',t.count('!DISubprogram')+t.count('!DILocation')+t.count('!DIFile'))
print('ll:',ll)
PY

  local start end ec elapsed st
  start=$(date +%s)
  printf '[%s] %s\n' "$(ts)" "docker run --rm ... timeout 420 phasar-cli -m artifacts/${bcname}.bc -D ifds-uninit ..." >> "$cmdlog"
  set +e
  docker run --rm \
    --user "$(id -u):$(id -g)" \
    -v "/home/jimi/PaperExperiment:/work/PaperExperiment" \
    --workdir "$o2dir_work" \
    --entrypoint /bin/bash \
    phasar:nosan \
    -lc "timeout 420 phasar-cli -m artifacts/${bcname}.bc -D ifds-uninit -P basic -C otf -E __ALL__ --emit-raw-results --emit-text-report --emit-stats --emit-statistics-as-json --out runs/ifds-uninit" > "$o2dir_host/log/ifds-uninit.stdout.log" 2> "$o2dir_host/log/ifds-uninit.stderr.log"
  ec=$?
  set -e
  end=$(date +%s)
  elapsed=$((end-start))
  st=error
  if [ "$ec" -eq 0 ]; then st=ok; elif [ "$ec" -eq 124 ]; then st=timeout; elif [ "$ec" -eq 137 ]; then st=oom_or_killed; fi
  printf 'analysis,exit_code,status,elapsed_sec\nifds-uninit,%s,%s,%s\n' "$ec" "$st" "$elapsed" > "$summary"

  local latest
  latest=$(RUNROOT="$runroot" python3 - <<'PY'
from pathlib import Path
import os
r=Path(os.environ['RUNROOT'])
subs=[p for p in r.iterdir() if p.is_dir()]
subs.sort(key=lambda p:p.stat().st_mtime, reverse=True)
print(subs[0] if subs else '')
PY
)

  if [ -n "$latest" ] && [ -f "$latest/psr-report.txt" ]; then
    python3 - <<PY
import csv, json, re
from pathlib import Path
report=Path(r'''$latest/psr-report.txt''')
source_root=Path(r'''$source_root_host''').resolve()
prefix=str(source_root)+'/ '
prefix=str(source_root)+'/'
out_csv=Path(r'''$o2dir_host/runs/ifds-uninit/target_linecheck.csv''')
out_json=Path(r'''$o2dir_host/runs/ifds-uninit/target_linecheck.json''')
lines=report.read_text(encoding='utf-8',errors='ignore').splitlines()
use_header=re.compile(r'^-+\s+(\d+)\. Use')
rows=[]; cur=None
for ln in lines:
  m=use_header.match(ln)
  if m:
    if cur: rows.append(cur)
    cur={'case':int(m.group(1)),'file':None,'line':None,'source':''}; continue
  if not cur: continue
  if ln.startswith('File'): cur['file']=ln.split(':',1)[1].strip()
  elif ln.startswith('Line'):
    try: cur['line']=int(ln.split(':',1)[1].strip())
    except: cur['line']=None
  elif ln.startswith('Source code'): cur['source']=ln.split(':',1)[1].strip()
if cur: rows.append(cur)
out=[]
for r in rows:
  f=r['file'] or ''
  if not f.startswith(prefix): continue
  rel=f[len(prefix):]
  hp=source_root/rel
  line=r['line'] or 0
  status='unknown'; reason=''; actual=''
  if not hp.exists(): status='missing_file'; reason='file not found'
  else:
    src=hp.read_text(encoding='utf-8',errors='ignore').splitlines()
    if line<1 or line>len(src): status='line_oob'; reason=f'line {line} out of range (1..{len(src)})'
    else:
      actual=src[line-1]
      if actual.strip()==(r['source'] or '').strip(): status='match'
      else: status='mismatch'; reason='source text mismatch'
  out.append({'case':r['case'],'file':rel,'line':line,'status':status,'report_source':r['source'],'actual_source':actual,'reason':reason})
out_json.write_text(json.dumps(out,indent=2),encoding='utf-8')
with out_csv.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['case','file','line','status','report_source','actual_source','reason'])
  w.writeheader(); w.writerows(out)
print('linecheck_rows',len(out))
PY
  fi

  if [ "$ec" -eq 0 ]; then
    printf 'success_utc=%s\nrun_dir=%s\nexit_code=0\nprofile=phasar-O2-g\n' "$(ts)" "$latest" > "$o2dir_host/status/success.marker"
    rm -f "$o2dir_host/status/failed.marker"
  else
    printf 'failed_utc=%s\nexit_code=%s\nstatus=%s\nprofile=phasar-O2-g\n' "$(ts)" "$ec" "$st" > "$o2dir_host/status/failed.marker"
  fi
}

run_masscan() {
  local project="masscan"
  local o2dir_host="$ROOT/$project/phasar/phasar-O2-g"
  local o2dir_work="/work/PaperExperiment/CompilerOptimization/Result/$project/phasar/phasar-O2-g"
  local src_orig="/home/jimi/PaperExperiment/CompilerOptimization/Target/masscan"
  local src_copy_host="$o2dir_host/work/$project"
  local src_copy_work="$o2dir_work/work/$project"
  mkdir -p "$o2dir_host/log" "$o2dir_host/artifacts/bc_objs" "$o2dir_host/runs/ifds-uninit" "$o2dir_host/status" "$o2dir_host/work"
  : > "$o2dir_host/log/commands.log"
  : > "$o2dir_host/log/project.log"
  rm -rf "$src_copy_host"
  cp -a "$src_orig" "$src_copy_host"
  chmod -R u+w "$src_copy_host"

  run_container "make -C '$src_copy_work' clean || true" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"
  run_container "make -C '$src_copy_work' -j$(nproc) CC=clang-16 CFLAGS='-O2 -g' OPTIMIZATION='-O2'" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"
  run_container "make -C '$src_copy_work' -B -n CC=clang-16 CFLAGS='-O2 -g' OPTIMIZATION='-O2' > '$o2dir_work/log/make_dryrun.log'" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"

  generate_bc_from_dryrun_in_container "$project" "$src_copy_work" "$o2dir_work" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"
  link_and_scan "$project" "$o2dir_host" "$o2dir_work" "masscan_O2_g" "$src_copy_host"
}

run_redis() {
  local project="redis"
  local o2dir_host="$ROOT/$project/phasar/phasar-O2-g"
  local o2dir_work="/work/PaperExperiment/CompilerOptimization/Result/$project/phasar/phasar-O2-g"
  local src_orig="/home/jimi/PaperExperiment/CompilerOptimization/Target/redis"
  local src_copy_host="$o2dir_host/work/$project"
  local src_copy_work="$o2dir_work/work/$project"
  local mkroot_work="$src_copy_work/src"
  mkdir -p "$o2dir_host/log" "$o2dir_host/artifacts/bc_objs" "$o2dir_host/runs/ifds-uninit" "$o2dir_host/status" "$o2dir_host/work"
  : > "$o2dir_host/log/commands.log"
  : > "$o2dir_host/log/project.log"
  rm -rf "$src_copy_host"
  cp -a "$src_orig" "$src_copy_host"
  chmod -R u+w "$src_copy_host"
  chmod +x "$src_copy_host/src/mkreleasehdr.sh" || true

  run_container "make -C '$src_copy_work' distclean || true" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"
  run_container "make -C '$src_copy_work/deps' -j$(nproc) CC=clang-16 hiredis linenoise lua hdr_histogram fpconv fast_float xxhash || true" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"
  run_container "bash -lc 'cd \"$mkroot_work\" && ./mkreleasehdr.sh' || true" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"
  run_container "make -C '$mkroot_work' -j$(nproc) CC=clang-16 MALLOC=libc BUILD_TLS=no OPTIMIZATION='-O2' REDIS_CFLAGS='-g -DNULL=0' || true" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"
  run_container "make -C '$mkroot_work' -B -n CC=clang-16 MALLOC=libc BUILD_TLS=no OPTIMIZATION='-O2' REDIS_CFLAGS='-g -DNULL=0' > '$o2dir_work/log/make_dryrun.log'" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"

  generate_bc_from_dryrun_in_container "$project" "$mkroot_work" "$o2dir_work" "$o2dir_host/log/commands.log" "$o2dir_host/log/project.log"
  link_and_scan "$project" "$o2dir_host" "$o2dir_work" "redis_O2_g" "$src_copy_host"
}

refresh_global_summaries() {
  python3 - <<'PY'
import csv
from pathlib import Path
result_root=Path('/home/jimi/PaperExperiment/CompilerOptimization/Result')
projects=['curl','tengine','wasmedge','duckdb','flatbuffers','flite','grpc','lepton','leveldb','libco','libsndfile','masscan','opencv','rapidjson','redis','rethinkdb','zfp','zopfli']
summary=result_root/'phasar_O2_g_linecheck_summary.csv'
rows=[]
for p in projects:
    csv_path=result_root/p/'phasar'/'phasar-O2-g'/'runs'/'ifds-uninit'/'target_linecheck.csv'
    if not csv_path.exists():
        continue
    total=match=mismatch=line_oob=0
    with csv_path.open(newline='',encoding='utf-8') as f:
        r=csv.DictReader(f)
        for row in r:
            total+=1
            st=row.get('status','')
            if st=='match': match+=1
            elif st=='mismatch': mismatch+=1
            elif st=='line_oob': line_oob+=1
    oob=(line_oob/total*100.0) if total else 0.0
    rows.append({'project':p,'total_uses':total,'match':match,'mismatch':mismatch,'line_oob':line_oob,'oob_rate':f'{oob:.2f}'})
rows.sort(key=lambda x:x['project'])
with summary.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['project','total_uses','match','mismatch','line_oob','oob_rate'])
    w.writeheader(); w.writerows(rows)

status_csv=result_root/'phasar_O2_g_project_status.csv'
rows=[]
for p in projects:
    o2=result_root/p/'phasar'/'phasar-O2-g'
    status='missing_dir'; ifds_status=''; ifds_exit=''; reason=''; has_report='0'
    if o2.exists():
        status='none'
        sm=o2/'status'/'success.marker'; fm=o2/'status'/'failed.marker'
        if sm.exists(): status='success'
        elif fm.exists():
            status='failed'
            reason=fm.read_text(encoding='utf-8',errors='ignore').strip().replace('\n',' | ')
        s=o2/'log'/'summary.csv'
        if s.exists():
            rr=list(csv.DictReader(s.open()))
            for r in rr:
                if r.get('analysis')=='ifds-uninit': ifds_status=r.get('status',''); ifds_exit=r.get('exit_code','')
        run=o2/'runs'/'ifds-uninit'
        if run.exists():
            dirs=[d for d in run.iterdir() if d.is_dir()]
            dirs.sort(key=lambda d:d.stat().st_mtime, reverse=True)
            if dirs and (dirs[0]/'psr-report.txt').exists(): has_report='1'
    rows.append({'project':p,'status':status,'ifds_status':ifds_status,'ifds_exit':ifds_exit,'has_report':has_report,'reason':reason})
with status_csv.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['project','status','ifds_status','ifds_exit','has_report','reason'])
    w.writeheader(); w.writerows(rows)
print(summary)
print(status_csv)
PY
}

run_masscan
run_redis
refresh_global_summaries
