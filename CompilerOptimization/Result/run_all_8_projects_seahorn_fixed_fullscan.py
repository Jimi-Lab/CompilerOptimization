#!/usr/bin/env python3
import csv
import os
import re
import shlex
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path('/home/jimi/PaperExperiment/CompilerOptimization/Result')
PROJECTS = [
    'flatbuffers',
    'lepton',
    'libsndfile',
    'masscan',
    'redis',
    'tengine',
    'zfp',
    'zopfli',
]

PREFERRED_IMAGE = 'seahorn/seahorn-llvm14:fixed'
FALLBACK_IMAGE = 'seahorn/seahorn-llvm14:nightly'


def pick_image() -> str:
    if subprocess.run(['docker', 'image', 'inspect', PREFERRED_IMAGE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        return PREFERRED_IMAGE
    return FALLBACK_IMAGE


def project_bc(project: str) -> Path:
    base = ROOT / project / 'seahorn' / 'seahorn-O2-g' / 'artifacts'
    if project == 'zopfli':
        z_only = base / 'zopfli_O2_g_zopfli_only.bc'
        if z_only.exists() and z_only.stat().st_size > 0:
            return z_only
    return base / f'{project}_O2_g.bc'


def run_cmd(image: str, cmd: str, timeout_s: int, stdout_path: Path, stderr_path: Path, cmdlog: Path, step: str, name: str):
    uid, gid = os.getuid(), os.getgid()
    host_cmd = (
        f"timeout {timeout_s} docker run --rm --user '{uid}:{gid}' "
        f"-v '/home/jimi/PaperExperiment:/work/PaperExperiment' "
        f"--workdir '/work/PaperExperiment' --entrypoint /bin/bash {image} -lc {shlex.quote(cmd)}"
    )
    st = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with cmdlog.open('a', encoding='utf-8') as f:
        f.write(f'[{st}] START step={step} name={name}\n')
        f.write(f'[{st}] CMD {host_cmd}\n')
    t0 = time.time()
    with stdout_path.open('w', encoding='utf-8') as o, stderr_path.open('w', encoding='utf-8') as e:
        proc = subprocess.run(host_cmd, shell=True, stdout=o, stderr=e)
    elapsed = int(time.time() - t0)
    et = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with cmdlog.open('a', encoding='utf-8') as f:
        f.write(f'[{et}] END step={step} name={name} exit_code={proc.returncode} elapsed_sec={elapsed}\n')
    return proc.returncode, elapsed, host_cmd


def parse_smc_cases(logd: Path):
    cases = []
    cid = 1
    for mode, stem in [('smc_typeoff', 'sea.smc.stats.typeoff'), ('smc_typeon', 'sea.smc.stats.typeon')]:
        for suf in ('.log', '.stderr.log'):
            p = logd / f'{stem}{suf}'
            if not p.exists():
                continue
            lines = p.read_text(encoding='utf-8', errors='ignore').splitlines()
            i = 0
            while i < len(lines):
                if lines[i].strip().startswith('Possible read of undefined value at'):
                    file_ = line = col = bit = ''
                    j = i + 1
                    while j < len(lines):
                        t = lines[j].strip()
                        if t.startswith('Possible read of undefined value at'):
                            break
                        if t.startswith('--- File'):
                            file_ = t.split(':', 1)[1].strip()
                        elif t.startswith('--- Line'):
                            line = t.split(':', 1)[1].strip()
                        elif t.startswith('--- Column'):
                            col = t.split(':', 1)[1].strip()
                        elif t.startswith('--- Bitcode'):
                            bit = t.split(':', 1)[1].strip()
                        j += 1
                    if file_ or line or col:
                        cases.append({
                            'case_id': cid,
                            'source_mode': mode,
                            'file': file_,
                            'line': line,
                            'column': col,
                            'message': 'Possible read of undefined value at',
                            'bitcode_snippet': bit,
                            'log_file': str(p),
                        })
                        cid += 1
                    i = j
                else:
                    i += 1
    return cases


def horn_result(exit_code: int, text: str) -> str:
    t = text.lower()
    if exit_code == 124:
        return 'timeout'
    if re.search(r'\bunsat\b', t):
        return 'unsat'
    if re.search(r'\bsat\b', t):
        return 'sat'
    if re.search(r'\bunknown\b', t):
        return 'unknown'
    if exit_code == 0:
        return 'unknown'
    return 'error'


def main():
    image = pick_image()
    batch_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    global_summary_path = ROOT / f'seahorn_fixed_fullscan_summary_{batch_ts}.csv'

    global_rows = []

    for project in PROJECTS:
        base = ROOT / project / 'seahorn' / 'seahorn-O2-g'
        bc = project_bc(project)
        run = base / 'result' / f'run_{batch_ts}_fixed_fullscan'
        logd = run / 'log'
        artd = run / 'artifact'
        repd = run / 'report'
        sumd = run / 'summary'
        statusd = run / 'status'
        for d in (logd, artd, repd, sumd, statusd):
            d.mkdir(parents=True, exist_ok=True)

        (base / 'result' / 'latest.txt').write_text(str(run) + '\n', encoding='utf-8')

        cmdlog = logd / 'commands.log'
        exitcsv = logd / 'exit_codes.csv'
        with exitcsv.open('w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(['step', 'name', 'exit_code', 'elapsed_sec', 'stdout', 'stderr'])

        if not bc.exists() or bc.stat().st_size == 0:
            (statusd / 'failed.marker').write_text(f'missing_bc={bc}\n', encoding='utf-8')
            global_rows.append({
                'project': project,
                'image': image,
                'run': str(run),
                'bc': str(bc),
                'smc_case_total': '0',
                'horn_sat': '0',
                'horn_unsat': '0',
                'horn_err_or_to': '0',
                'note': 'missing_bc',
            })
            continue

        cb = f'/work/PaperExperiment/CompilerOptimization/Result/{project}/seahorn/seahorn-O2-g/artifacts/{bc.name}'
        cr = f'/work/PaperExperiment/CompilerOptimization/Result/{project}/seahorn/seahorn-O2-g/result/{run.name}'

        steps = [
            ('01', 'inspect_profiler', 'sea.inspect.profiler.log', f'sea inspect-bitcode --profiler {cb}', 1800),
            ('02', 'inspect_mem_stats', 'sea.inspect.mem-stats.log', f'sea inspect-bitcode --mem-stats {cb}', 1800),
            ('03', 'inspect_callgraph_stats', 'sea.inspect.callgraph-stats.log', f'sea inspect-bitcode --mem-callgraph-stats {cb}', 1800),
            ('04', 'smc_typeoff', 'sea.smc.stats.typeoff.log', f'sea smc-checks --print-smc-stats --smc-check-threshold=100000 {cb}', 3600),
            ('05', 'smc_typeon', 'sea.smc.stats.typeon.log', f'sea smc-checks --print-smc-stats --smc-check-threshold=100000 --sea-dsa-type-aware {cb}', 3600),
            ('06', 'smc_instrument', 'sea.smc.instrument.log', f'sea smc-checks --smc-check-threshold=100000 {cb} -o {cr}/artifact/{project}_O2_g.smc.bc', 5400),
            ('07', 'horn_smc_reg', 'sea.horn.smc.reg.log', f'sea horn {cr}/artifact/{project}_O2_g.smc.bc --solve --step=large --track=reg --cpu 1800 --mem 24000', 2400),
            ('08', 'horn_smc_ptr', 'sea.horn.smc.ptr.log', f'sea horn {cr}/artifact/{project}_O2_g.smc.bc --solve --step=large --track=ptr --dsa sea-cs --cpu 3600 --mem 32000', 4200),
            ('09', 'horn_smc_mem', 'sea.horn.smc.mem.log', f'sea horn {cr}/artifact/{project}_O2_g.smc.bc --solve --step=small --track=mem --dsa sea-cs --cpu 7200 --mem 48000', 7800),
            ('10', 'ndc_instrument', 'sea.ndc.instrument.log', f'sea ndc-inst {cb} -o {cr}/artifact/{project}_O2_g.ndc.bc', 3600),
            ('11', 'horn_ndc_reg', 'sea.horn.ndc.reg.log', f'sea horn {cr}/artifact/{project}_O2_g.ndc.bc --solve --step=large --track=reg --cpu 1800 --mem 24000', 2400),
            ('12', 'horn_ndc_ptr', 'sea.horn.ndc.ptr.log', f'sea horn {cr}/artifact/{project}_O2_g.ndc.bc --solve --step=large --track=ptr --dsa sea-cs --cpu 3600 --mem 32000', 4200),
            ('13', 'horn_ndc_mem', 'sea.horn.ndc.mem.log', f'sea horn {cr}/artifact/{project}_O2_g.ndc.bc --solve --step=small --track=mem --dsa sea-cs --cpu 7200 --mem 48000', 7800),
            ('14', 'crab_instrument', 'sea.crab.instrument.log', f'sea crab-inst {cb} -o {cr}/artifact/{project}_O2_g.crab.bc', 3600),
            ('15', 'horn_crab_ptr', 'sea.horn.crab.ptr.log', f'sea horn {cr}/artifact/{project}_O2_g.crab.bc --solve --step=large --track=ptr --dsa sea-cs --cpu 3600 --mem 32000', 4200),
            ('16', 'term', 'sea.term.log', f'sea term {cb} --cpu 3600 --mem 24000', 4200),
        ]

        results = []
        for sid, name, logname, inner, timeout in steps:
            outp = logd / logname
            errp = logd / logname.replace('.log', '.stderr.log')
            ec, el, _ = run_cmd(image, inner, timeout, outp, errp, cmdlog, sid, name)
            with exitcsv.open('a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow([sid, name, ec, el, str(outp), str(errp)])
            results.append({'step': sid, 'name': name, 'exit_code': ec, 'elapsed': el, 'stdout': outp, 'stderr': errp})

        smc_cases = parse_smc_cases(logd)
        smc_csv = sumd / 'smc_cases.csv'
        with smc_csv.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['case_id', 'source_mode', 'file', 'line', 'column', 'message', 'bitcode_snippet', 'log_file'])
            w.writeheader()
            w.writerows(smc_cases)

        horn_rows = []
        for r in results:
            if not r['name'].startswith('horn_'):
                continue
            txt = ''
            for p in (r['stdout'], r['stderr']):
                if p.exists():
                    txt += p.read_text(encoding='utf-8', errors='ignore') + '\n'
            if '_smc_' in r['name']:
                ib = artd / f'{project}_O2_g.smc.bc'
            elif '_ndc_' in r['name']:
                ib = artd / f'{project}_O2_g.ndc.bc'
            else:
                ib = artd / f'{project}_O2_g.crab.bc'
            track = 'reg' if r['name'].endswith('_reg') else ('ptr' if r['name'].endswith('_ptr') else ('mem' if r['name'].endswith('_mem') else ''))
            step = 'small' if track == 'mem' else 'large'
            dsa = 'sea-cs' if track in ('ptr', 'mem') else ''
            horn_rows.append({
                'mode': r['name'],
                'input_bc': str(ib),
                'track': track,
                'step': step,
                'dsa': dsa,
                'result': horn_result(r['exit_code'], txt),
                'exit_code': r['exit_code'],
                'elapsed_sec': r['elapsed'],
                'log_file': str(r['stdout']),
            })

        horn_csv = sumd / 'horn_status.csv'
        with horn_csv.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['mode', 'input_bc', 'track', 'step', 'dsa', 'result', 'exit_code', 'elapsed_sec', 'log_file'])
            w.writeheader()
            w.writerows(horn_rows)

        produced = {
            'smc_bc': (artd / f'{project}_O2_g.smc.bc').exists(),
            'ndc_bc': (artd / f'{project}_O2_g.ndc.bc').exists(),
            'crab_bc': (artd / f'{project}_O2_g.crab.bc').exists(),
        }

        overview_rows = [
            ('smc_case_total', str(len(smc_cases))),
            ('smc_typeoff_cases', str(sum(1 for c in smc_cases if c['source_mode'] == 'smc_typeoff'))),
            ('smc_typeon_cases', str(sum(1 for c in smc_cases if c['source_mode'] == 'smc_typeon'))),
            ('unique_files', str(len({c['file'] for c in smc_cases if c['file']}))),
            ('unique_lines', str(len({(c['file'], c['line']) for c in smc_cases if c['file'] and c['line']}))),
            ('horn_sat_count', str(sum(1 for h in horn_rows if h['result'] == 'sat'))),
            ('horn_unsat_count', str(sum(1 for h in horn_rows if h['result'] == 'unsat'))),
            ('horn_unknown_or_timeout_count', str(sum(1 for h in horn_rows if h['result'] in ('unknown', 'timeout')))),
            ('image', image),
            ('smc_bc', '1' if produced['smc_bc'] else '0'),
            ('ndc_bc', '1' if produced['ndc_bc'] else '0'),
            ('crab_bc', '1' if produced['crab_bc'] else '0'),
        ]
        overview_csv = sumd / 'overview.csv'
        with overview_csv.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['metric', 'value'])
            w.writerows(overview_rows)

        fail_rows = []
        for r in results:
            s = r['stderr'].read_text(encoding='utf-8', errors='ignore') if r['stderr'].exists() else ''
            key = ''
            for ln in s.splitlines():
                low = ln.lower()
                if any(x in low for x in ['error', 'traceback', 'unknown parameter', 'parser error', 'timed out', 'unreachable code was reached', 'assertion violation']):
                    key = ln.strip()
                    break
            po = ''
            if r['name'] == 'smc_instrument':
                po = str(artd / f'{project}_O2_g.smc.bc')
            elif r['name'] == 'ndc_instrument':
                po = str(artd / f'{project}_O2_g.ndc.bc')
            elif r['name'] == 'crab_instrument':
                po = str(artd / f'{project}_O2_g.crab.bc')
            elif r['name'].startswith('horn_'):
                po = 'horn_status.csv entry'
            elif r['name'] == 'term':
                po = 'sea.term.log'
            fail_rows.append({'step': r['step'], 'name': r['name'], 'exit_code': r['exit_code'], 'produced_output': po, 'key_error': key})

        failure_csv = sumd / 'failure_inventory.csv'
        with failure_csv.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['step', 'name', 'exit_code', 'produced_output', 'key_error'])
            w.writeheader()
            w.writerows(fail_rows)

        fc = Counter(c['file'] for c in smc_cases if c['file'])
        lc = Counter((c['file'], c['line']) for c in smc_cases if c['file'] and c['line'])

        report_lines = [
            f'# {project} SeaHorn Static Analysis Report (fixed image fullscan)',
            '',
            '## Environment',
            f'- Docker image: `{image}`',
            f'- Input BC: `{bc}`',
            f'- Run root: `{run}`',
            '',
            '## Execution Matrix Status',
            '| Step | Name | Exit | Elapsed(s) |',
            '|---|---|---:|---:|',
        ]
        for r in results:
            report_lines.append(f"| {r['step']} | {r['name']} | {r['exit_code']} | {r['elapsed']} |")

        report_lines += [
            '',
            '## Produced/Not Produced Outputs (No Hiding)',
            f"- `smc_bc`: {'produced' if produced['smc_bc'] else 'NOT produced'}",
            f"- `ndc_bc`: {'produced' if produced['ndc_bc'] else 'NOT produced'}",
            f"- `crab_bc`: {'produced' if produced['crab_bc'] else 'NOT produced'}",
            '- Full failure list: `summary/failure_inventory.csv`',
            '',
            '## SMC Top File Distribution',
        ]
        if fc:
            report_lines += ['| File | Case Count |', '|---|---:|']
            for f, cnt in fc.most_common(15):
                report_lines.append(f'| `{f}` | {cnt} |')
        else:
            report_lines.append('- No SMC cases extracted.')

        report_lines += ['', '## SMC Top File:Line Distribution']
        if lc:
            report_lines += ['| File:Line | Case Count |', '|---|---:|']
            for (f, ln), cnt in lc.most_common(15):
                report_lines.append(f'| `{f}:{ln}` | {cnt} |')
        else:
            report_lines.append('- No line-level SMC cases extracted.')

        report_lines += ['', '## Horn Result Comparison', '| Mode | Track | Step | DSA | Result | Exit | Elapsed(s) |', '|---|---|---|---|---|---:|---:|']
        for h in horn_rows:
            report_lines.append(f"| {h['mode']} | {h['track']} | {h['step']} | {h['dsa']} | {h['result']} | {h['exit_code']} | {h['elapsed_sec']} |")

        report_lines += [
            '',
            '## Notes',
            '- This report does not hide failures. Any non-produced artifact is explicitly listed above and in failure_inventory.csv.',
            '- `term` can still end with UNKNOWN/parser warning; see logs for exact details.',
        ]

        final_report = repd / 'final_report.md'
        final_report.write_text('\n'.join(report_lines) + '\n', encoding='utf-8')

        # readmd detailed
        readmd = run / 'readmd.md'
        readmd_lines = [
            f'# {project} run detail (fullscan, fixed image)',
            '',
            f'- image: `{image}`',
            f'- input bc: `{bc}`',
            f'- run: `{run}`',
            '',
            '## Full command timeline',
            '```text',
        ]
        readmd_lines.extend(cmdlog.read_text(encoding='utf-8', errors='ignore').splitlines())
        readmd_lines += ['```', '', '## Raw outputs']
        for r in results:
            readmd_lines.append(f"- step {r['step']} `{r['name']}`: exit={r['exit_code']}, elapsed={r['elapsed']}s")
            readmd_lines.append(f"  - stdout: `{r['stdout']}`")
            readmd_lines.append(f"  - stderr: `{r['stderr']}`")
        readmd_lines += ['', '## Summary files']
        for p in [smc_csv, horn_csv, overview_csv, failure_csv, final_report]:
            readmd_lines.append(f'- `{p}`')
        readmd.write_text('\n'.join(readmd_lines) + '\n', encoding='utf-8')

        ok = produced['smc_bc'] and produced['ndc_bc']
        if ok:
            (statusd / 'success.marker').write_text(
                f"success_utc={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
                f"image={image}\n"
                f"run={run}\n"
                "note=fullscan_completed\n",
                encoding='utf-8',
            )
        else:
            (statusd / 'failed.marker').write_text('required_artifact_missing\n', encoding='utf-8')

        global_rows.append({
            'project': project,
            'image': image,
            'run': str(run),
            'bc': str(bc),
            'smc_case_total': str(len(smc_cases)),
            'horn_sat': str(sum(1 for h in horn_rows if h['result'] == 'sat')),
            'horn_unsat': str(sum(1 for h in horn_rows if h['result'] == 'unsat')),
            'horn_err_or_to': str(sum(1 for h in horn_rows if h['result'] in ('error', 'timeout'))),
            'note': '' if ok else 'required_artifact_missing',
        })

    with global_summary_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['project', 'image', 'run', 'bc', 'smc_case_total', 'horn_sat', 'horn_unsat', 'horn_err_or_to', 'note'])
        w.writeheader()
        w.writerows(global_rows)

    (ROOT / 'seahorn_fixed_fullscan_latest.txt').write_text(str(global_summary_path) + '\n', encoding='utf-8')
    print(global_summary_path)


if __name__ == '__main__':
    main()
