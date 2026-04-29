#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


VECTOR_OPS = (
    'insertelement',
    'extractelement',
    'shufflevector',
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description='Analyze only line/column-bearing SeaHorn cases across all_cases.csv files.'
    )
    p.add_argument('inputs', nargs='*', help='Input all_cases.csv files')
    p.add_argument('--root', help='Search root for **/summary/all_cases.csv')
    p.add_argument('--out-dir', required=True, help='Output directory')
    return p.parse_args()


def discover_inputs(args: argparse.Namespace) -> list[Path]:
    inputs = [Path(x).resolve() for x in args.inputs]
    if args.root:
        inputs.extend(sorted(Path(args.root).resolve().glob('**/summary/all_cases.csv')))
    out = []
    seen = set()
    for p in inputs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    if not out:
        raise SystemExit('No input all_cases.csv files found')
    return out


def field_limit_max() -> None:
    max_size = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_size)
            return
        except OverflowError:
            max_size //= 10


def infer_project(path: Path) -> str:
    parts = path.parts
    if 'Result' in parts:
        i = parts.index('Result')
        if i + 1 < len(parts):
            return parts[i + 1]
    return path.parent.parent.parent.name


def infer_run(path: Path) -> str:
    for part in path.parts:
        if part.startswith('run_'):
            return part
    return 'unknown_run'


def normalize_bool(v: bool) -> str:
    return '1' if v else '0'


def source_kind(file_path: str) -> str:
    p = file_path.lower()
    if p.endswith(('.h', '.hpp', '.hh', '.hxx')):
        return 'header'
    if p.endswith(('.c', '.cc', '.cpp', '.cxx')):
        return 'source'
    return 'other'


def locate_source(file_path: str, result_root: Path) -> Path | None:
    cand = Path(file_path)
    if cand.exists():
        return cand.resolve()
    repo_root = result_root.parents[2]
    alt = repo_root / file_path
    if alt.exists():
        return alt.resolve()
    target_pos = file_path.find('Target/')
    if target_pos != -1:
        alt2 = repo_root / file_path[target_pos:]
        if alt2.exists():
            return alt2.resolve()
    return None


def analyze_line_case(row: dict[str, str], result_root: Path, project: str, run: str) -> dict[str, str] | None:
    file_path = row.get('file', '').strip()
    line_raw = row.get('line', '').strip()
    col_raw = row.get('column', '').strip()
    if not file_path or not line_raw or not col_raw:
        return None
    try:
        line_num = int(line_raw)
        col_num = int(col_raw)
    except ValueError:
        return None

    resolved = locate_source(file_path, result_root)
    file_exists = resolved is not None
    line_exists = False
    line_text = ''
    if resolved is not None:
        try:
            lines = resolved.read_text(encoding='utf-8', errors='ignore').splitlines()
            if 1 <= line_num <= len(lines):
                line_exists = True
                line_text = lines[line_num - 1].strip()
        except Exception:
            line_exists = False

    bitcode = row.get('bitcode_snippet', '').lower()
    src_kind = source_kind(file_path)
    vectorized_ir = any(op in bitcode for op in VECTOR_OPS)
    inline_risk = src_kind == 'header' or vectorized_ir

    if line_num <= 0 or col_num <= 0:
        quality = 'invalid_line_zero'
    elif not file_exists:
        quality = 'missing_file'
    elif not line_exists:
        quality = 'line_oob'
    elif src_kind == 'header':
        quality = 'header_source_location'
    else:
        quality = 'source_location_ok'

    if quality in ('invalid_line_zero', 'missing_file', 'line_oob'):
        paper_bucket = 'misreported_location_case'
        paper_priority = 'high'
    elif quality in ('source_location_ok', 'header_source_location') and inline_risk:
        paper_bucket = 'optimization_sensitive_case'
        paper_priority = 'high'
    elif quality == 'source_location_ok' and not inline_risk:
        paper_bucket = 'stable_control_case'
        paper_priority = 'medium'
    else:
        paper_bucket = 'not_paper_ready'
        paper_priority = 'low'

    return {
        'project': project,
        'run': run,
        'case_id': row.get('case_id', ''),
        'case_kind': row.get('case_kind', ''),
        'step': row.get('step', ''),
        'name': row.get('name', ''),
        'exit_code': row.get('exit_code', ''),
        'elapsed_sec': row.get('elapsed_sec', ''),
        'source_log': row.get('source_log', ''),
        'file': file_path,
        'resolved_file': str(resolved) if resolved else '',
        'line': str(line_num),
        'column': str(col_num),
        'file_exists': normalize_bool(file_exists),
        'line_exists': normalize_bool(line_exists),
        'source_kind': src_kind,
        'vectorized_ir': normalize_bool(vectorized_ir),
        'inline_risk': normalize_bool(inline_risk),
        'location_quality': quality,
        'paper_bucket': paper_bucket,
        'paper_priority': paper_priority,
        'line_text': line_text,
        'message': row.get('message', ''),
        'bitcode_snippet': row.get('bitcode_snippet', ''),
    }


def main() -> int:
    args = parse_args()
    field_limit_max()
    inputs = discover_inputs(args)
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    analyzed_rows = []
    project_rows = []

    for csv_path in inputs:
        project = infer_project(csv_path)
        run = infer_run(csv_path)
        result_root = csv_path.parents[3]
        with csv_path.open(encoding='utf-8', newline='') as f:
            raw_rows = list(csv.DictReader(f))
        rows = []
        for row in raw_rows:
            analyzed = analyze_line_case(row, result_root, project, run)
            if analyzed is not None:
                rows.append(analyzed)
        analyzed_rows.extend(rows)

        q = Counter(r['location_quality'] for r in rows)
        p = Counter(r['paper_bucket'] for r in rows)
        project_rows.append({
            'project': project,
            'run': run,
            'input_csv': str(csv_path),
            'line_cases_total': str(len(rows)),
            'source_location_ok': str(q.get('source_location_ok', 0)),
            'header_source_location': str(q.get('header_source_location', 0)),
            'missing_file': str(q.get('missing_file', 0)),
            'invalid_line_zero': str(q.get('invalid_line_zero', 0)),
            'line_oob': str(q.get('line_oob', 0)),
            'misreported_location_case': str(p.get('misreported_location_case', 0)),
            'optimization_sensitive_case': str(p.get('optimization_sensitive_case', 0)),
            'stable_control_case': str(p.get('stable_control_case', 0)),
            'not_paper_ready': str(p.get('not_paper_ready', 0)),
        })

    analyzed_fields = [
        'project', 'run', 'case_id', 'case_kind', 'step', 'name', 'exit_code', 'elapsed_sec',
        'source_log', 'file', 'resolved_file', 'line', 'column', 'file_exists', 'line_exists',
        'source_kind', 'vectorized_ir', 'inline_risk', 'location_quality', 'paper_bucket',
        'paper_priority', 'line_text', 'message', 'bitcode_snippet',
    ]
    with (out_dir / 'seahorn_all_cases_by_line.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=analyzed_fields)
        w.writeheader()
        w.writerows(analyzed_rows)

    summary_fields = list(project_rows[0].keys()) if project_rows else ['project']
    with (out_dir / 'seahorn_all_cases_by_line_project_summary.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=summary_fields)
        w.writeheader()
        w.writerows(project_rows)

    report = []
    report.append('# SeaHorn All-Cases By-Line Analysis')
    report.append('')
    report.append('## How to choose paper-ready cases')
    report.append('- `misreported_location_case` (high priority): file exists but line is zero, file is missing, or line is out-of-bounds. These are directly useful for your paper because they show location corruption/misreporting.')
    report.append('- `optimization_sensitive_case` (high priority): line resolves, but it maps to a header or vectorized IR (`insertelement`/`shufflevector`/`extractelement`). These are good cases for studying inline/optimization-induced location drift.')
    report.append('- `stable_control_case` (medium priority): line resolves cleanly to a source file and serves as a control/baseline case.')
    report.append('- `not_paper_ready` (low priority): line/column exists but the case still lacks enough evidence for a clean paper argument.')
    report.append('')
    report.append('## Project Summary')
    for row in project_rows:
        report.append(
            f"- `{row['project']}` line_cases={row['line_cases_total']} misreported={row['misreported_location_case']} "
            f"opt_sensitive={row['optimization_sensitive_case']} stable={row['stable_control_case']} not_ready={row['not_paper_ready']}"
        )

    (out_dir / 'seahorn_all_cases_by_line_analysis.md').write_text('\n'.join(report) + '\n', encoding='utf-8')

    print(out_dir / 'seahorn_all_cases_by_line.csv')
    print(out_dir / 'seahorn_all_cases_by_line_project_summary.csv')
    print(out_dir / 'seahorn_all_cases_by_line_analysis.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
