#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


VECTOR_OPS = (
    'insertelement',
    'extractelement',
    'shufflevector',
)

TOOL_FAILURE_KINDS = {
    'bad_alloc',
    'broken_module',
    'unsupported',
}

RESULT_VALIDITY_KINDS = {
    'trivial_safe_warning',
    'warning_line',
    'error_line',
    'unsupported',
    'bad_alloc',
    'broken_module',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Systematically analyze SeaHorn all_cases.csv files for source-location fidelity and result validity.'
    )
    parser.add_argument(
        'inputs',
        nargs='*',
        help='Input all_cases.csv files. If omitted, --root must be provided.',
    )
    parser.add_argument(
        '--root',
        help='Search root for **/summary/all_cases.csv and analyze all matches.',
    )
    parser.add_argument(
        '--out-dir',
        required=True,
        help='Directory where analysis CSV/MD outputs will be written.',
    )
    return parser.parse_args()


def discover_inputs(args: argparse.Namespace) -> list[Path]:
    inputs = [Path(p).resolve() for p in args.inputs]
    if args.root:
        root = Path(args.root).resolve()
        inputs.extend(sorted(root.glob('**/summary/all_cases.csv')))
    # dedupe preserve order
    seen = set()
    out: list[Path] = []
    for p in inputs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    if not out:
        raise SystemExit('No input all_cases.csv files provided or discovered.')
    return out


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


def source_kind(file_path: str) -> str:
    p = file_path.lower()
    if not p:
        return 'none'
    if p.endswith(('.h', '.hpp', '.hh', '.hxx')):
        return 'header'
    if p.endswith(('.c', '.cc', '.cpp', '.cxx')):
        return 'source'
    return 'other'


def normalize_bool(v: bool) -> str:
    return '1' if v else '0'


def analyze_row(row: dict[str, str], source_root: Path) -> dict[str, str]:
    file_path = row.get('file', '').strip()
    line_raw = row.get('line', '').strip()
    col_raw = row.get('column', '').strip()
    bitcode = row.get('bitcode_snippet', '').strip().lower()
    message = row.get('message', '').strip().lower()
    case_kind = row.get('case_kind', '').strip()

    has_source_loc = bool(file_path and line_raw and line_raw != '0')
    line_num = None
    col_num = None
    try:
        line_num = int(line_raw)
    except Exception:
        pass
    try:
        col_num = int(col_raw)
    except Exception:
        pass

    resolved_file = ''
    file_exists = False
    line_exists = False
    line_text = ''
    if file_path:
        candidate = Path(file_path)
        if candidate.exists():
            resolved = candidate
        else:
            resolved = source_root / file_path
        if resolved.exists():
            resolved_file = str(resolved.resolve())
            file_exists = True
            if line_num and line_num > 0:
                lines = resolved.read_text(encoding='utf-8', errors='ignore').splitlines()
                if 1 <= line_num <= len(lines):
                    line_exists = True
                    line_text = lines[line_num - 1].strip()

    src_kind = source_kind(file_path)
    vectorized_ir = any(op in bitcode for op in VECTOR_OPS)
    inline_risk = src_kind == 'header' or vectorized_ir

    if not file_path:
        location_quality = 'no_source_location'
    elif line_raw == '0' or line_num == 0:
        location_quality = 'invalid_line_zero'
    elif not file_exists:
        location_quality = 'missing_file'
    elif not line_exists:
        location_quality = 'line_oob'
    elif src_kind == 'header':
        location_quality = 'header_source_location'
    else:
        location_quality = 'source_location_ok'

    if case_kind == 'undefined_read_block' and location_quality in {'source_location_ok', 'header_source_location'}:
        analytic_group = 'source_case'
    elif case_kind == 'undefined_read_summary':
        analytic_group = 'summary_only'
    elif case_kind in RESULT_VALIDITY_KINDS:
        analytic_group = 'result_validity'
    else:
        analytic_group = 'other'

    if case_kind == 'trivial_safe_warning' or 'trivially safe' in message:
        trust_signal = 'trivial_safe'
    elif case_kind in TOOL_FAILURE_KINDS:
        trust_signal = 'tool_failure'
    elif case_kind == 'warning_line' and 'verifier.error' in message:
        trust_signal = 'verifier_error_warning'
    elif case_kind == 'undefined_read_block' and location_quality in {'source_location_ok', 'header_source_location'}:
        trust_signal = 'potential_source_case'
    elif case_kind == 'undefined_read_summary':
        trust_signal = 'summary_only'
    else:
        trust_signal = 'other'

    return {
        'project': row['project'],
        'run': row['run'],
        'case_id': row.get('case_id', ''),
        'case_kind': case_kind,
        'step': row.get('step', ''),
        'name': row.get('name', ''),
        'exit_code': row.get('exit_code', ''),
        'elapsed_sec': row.get('elapsed_sec', ''),
        'source_log': row.get('source_log', ''),
        'source_channel': row.get('source_channel', ''),
        'file': file_path,
        'resolved_file': resolved_file,
        'line': line_raw,
        'column': col_raw,
        'file_exists': normalize_bool(file_exists),
        'line_exists': normalize_bool(line_exists),
        'source_kind': src_kind,
        'vectorized_ir': normalize_bool(vectorized_ir),
        'inline_risk': normalize_bool(inline_risk),
        'location_quality': location_quality,
        'analytic_group': analytic_group,
        'trust_signal': trust_signal,
        'line_text': line_text,
        'message': row.get('message', ''),
        'bitcode_snippet': row.get('bitcode_snippet', ''),
    }


def read_rows(path: Path) -> list[dict[str, str]]:
    max_size = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_size)
            break
        except OverflowError:
            max_size //= 10
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    inputs = discover_inputs(args)
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    all_analyzed: list[dict[str, str]] = []
    per_project_summary: list[dict[str, str]] = []

    for csv_path in inputs:
        raw_rows = read_rows(csv_path)
        project = infer_project(csv_path)
        run = infer_run(csv_path)
        result_root = csv_path.parents[3]
        source_root = result_root.parents[2]

        analyzed_rows = []
        for row in raw_rows:
            row = dict(row)
            row['project'] = project
            row['run'] = run
            analyzed_rows.append(analyze_row(row, source_root))
        all_analyzed.extend(analyzed_rows)

        counts_kind = Counter(r['case_kind'] for r in analyzed_rows)
        counts_loc = Counter(r['location_quality'] for r in analyzed_rows)
        counts_trust = Counter(r['trust_signal'] for r in analyzed_rows)
        per_project_summary.append({
            'project': project,
            'run': run,
            'input_csv': str(csv_path),
            'total_cases': str(len(analyzed_rows)),
            'undefined_read_block': str(counts_kind.get('undefined_read_block', 0)),
            'summary_only': str(counts_trust.get('summary_only', 0)),
            'trivial_safe': str(counts_trust.get('trivial_safe', 0)),
            'tool_failure': str(counts_trust.get('tool_failure', 0)),
            'potential_source_case': str(counts_trust.get('potential_source_case', 0)),
            'source_location_ok': str(counts_loc.get('source_location_ok', 0)),
            'header_source_location': str(counts_loc.get('header_source_location', 0)),
            'invalid_line_zero': str(counts_loc.get('invalid_line_zero', 0)),
            'missing_file': str(counts_loc.get('missing_file', 0)),
            'line_oob': str(counts_loc.get('line_oob', 0)),
            'no_source_location': str(counts_loc.get('no_source_location', 0)),
        })

    analyzed_fields = [
        'project', 'run', 'case_id', 'case_kind', 'step', 'name', 'exit_code', 'elapsed_sec',
        'source_log', 'source_channel', 'file', 'resolved_file', 'line', 'column', 'file_exists',
        'line_exists', 'source_kind', 'vectorized_ir', 'inline_risk', 'location_quality',
        'analytic_group', 'trust_signal', 'line_text', 'message', 'bitcode_snippet',
    ]
    write_csv(out_dir / 'seahorn_all_cases_analyzed.csv', all_analyzed, analyzed_fields)

    summary_fields = list(per_project_summary[0].keys()) if per_project_summary else ['project']
    write_csv(out_dir / 'seahorn_all_cases_project_summary.csv', per_project_summary, summary_fields)

    report = []
    report.append('# SeaHorn All-Cases Analysis')
    report.append('')
    report.append('## Project Summary')
    for row in per_project_summary:
        report.append(
            f"- `{row['project']}` total={row['total_cases']} source_ok={row['source_location_ok']} "
            f"header={row['header_source_location']} trivial_safe={row['trivial_safe']} tool_failure={row['tool_failure']}"
        )
    report.append('')
    report.append('## Interpretation')
    report.append('- `source_location_ok` means the case has a file+line and that line exists in the source file.')
    report.append('- `header_source_location` means the location resolves into a header; this is often associated with inline/template/intrinsic mapping drift.')
    report.append('- `trivial_safe` means the result is not a trustworthy program bug/safety conclusion, usually due to missing `main` or invalid input semantics.')
    report.append('- `tool_failure` means backend/runtime/tool errors such as bad_alloc/broken_module/unsupported, not program bugs.')
    (out_dir / 'seahorn_all_cases_analysis.md').write_text('\n'.join(report) + '\n', encoding='utf-8')

    print(out_dir / 'seahorn_all_cases_analyzed.csv')
    print(out_dir / 'seahorn_all_cases_project_summary.csv')
    print(out_dir / 'seahorn_all_cases_analysis.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
