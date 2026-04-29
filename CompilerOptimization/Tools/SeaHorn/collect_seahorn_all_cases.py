#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


POSSIBLE_READ_HEADER = 'Possible read of undefined value at'
CASE_KEYWORDS = (
    'warning:',
    'error:',
    'traceback',
    'unsupported',
    'not supported',
    'std::bad_alloc',
    'broken module',
    'trivially safe',
    'unreachable code was reached',
    'parser error',
    'unknown parameter',
    'loosing precision',
    'unhandled',
    'main function not found',
)


def build_log_index(exit_codes_csv: Path) -> dict[str, dict[str, str]]:
    idx: dict[str, dict[str, str]] = {}
    if not exit_codes_csv.exists():
        return idx
    with exit_codes_csv.open(encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            for key in ('stdout', 'stderr'):
                p = row.get(key, '')
                if p:
                    idx[str(Path(p).resolve())] = row
    return idx


def parse_possible_read_blocks(log_file: Path, lines: list[str], meta: dict[str, str], rows: list[dict[str, str]], counter: list[int]) -> None:
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith(POSSIBLE_READ_HEADER):
            file_ = ''
            line = ''
            column = ''
            bitcode = ''
            block_start = i + 1
            j = block_start
            while j < len(lines):
                text = lines[j].strip()
                if text.startswith(POSSIBLE_READ_HEADER):
                    break
                if text.startswith('--- File'):
                    file_ = text.split(':', 1)[1].strip()
                elif text.startswith('--- Line'):
                    line = text.split(':', 1)[1].strip()
                elif text.startswith('--- Column'):
                    column = text.split(':', 1)[1].strip()
                elif text.startswith('--- Bitcode'):
                    bitcode = text.split(':', 1)[1].strip()
                j += 1
            counter[0] += 1
            rows.append({
                'case_id': str(counter[0]),
                'case_kind': 'undefined_read_block',
                'step': meta.get('step', ''),
                'name': meta.get('name', ''),
                'exit_code': meta.get('exit_code', ''),
                'elapsed_sec': meta.get('elapsed_sec', ''),
                'source_log': str(log_file),
                'source_channel': 'stderr' if log_file.name.endswith('.stderr.log') else 'stdout',
                'file': file_,
                'line': line,
                'column': column,
                'message': POSSIBLE_READ_HEADER,
                'bitcode_snippet': bitcode,
                'raw_text': '\n'.join(lines[i:j]).strip(),
            })
            i = j
        else:
            i += 1


def parse_single_line_cases(log_file: Path, lines: list[str], meta: dict[str, str], rows: list[dict[str, str]], counter: list[int]) -> None:
    for raw in lines:
        text = raw.strip()
        if not text or text.startswith('--- '):
            continue
        low = text.lower()
        if text.startswith(POSSIBLE_READ_HEADER):
            continue
        if any(k in low for k in CASE_KEYWORDS):
            if 'found ' in low and 'possible reads of undefined values' in low:
                kind = 'undefined_read_summary'
            elif 'main function not found' in low or 'trivially safe' in low:
                kind = 'trivial_safe_warning'
            elif 'std::bad_alloc' in low:
                kind = 'bad_alloc'
            elif 'broken module' in low:
                kind = 'broken_module'
            elif 'unsupported' in low or 'not supported' in low:
                kind = 'unsupported'
            elif 'error:' in low or 'parser error' in low or 'traceback' in low or 'unknown parameter' in low:
                kind = 'error_line'
            else:
                kind = 'warning_line'
            counter[0] += 1
            rows.append({
                'case_id': str(counter[0]),
                'case_kind': kind,
                'step': meta.get('step', ''),
                'name': meta.get('name', ''),
                'exit_code': meta.get('exit_code', ''),
                'elapsed_sec': meta.get('elapsed_sec', ''),
                'source_log': str(log_file),
                'source_channel': 'stderr' if log_file.name.endswith('.stderr.log') else 'stdout',
                'file': '',
                'line': '',
                'column': '',
                'message': text,
                'bitcode_snippet': '',
                'raw_text': text,
            })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Collect all SeaHorn-reported cases from one run directory')
    parser.add_argument('run_dir', help='SeaHorn run directory that contains log/ and summary/')
    parser.add_argument('--out-csv', help='Optional output CSV path; defaults to summary/all_cases.csv in run_dir')
    parser.add_argument('--out-summary', help='Optional summary CSV path; defaults to summary/all_cases_summary.csv in run_dir')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    log_dir = run_dir / 'log'
    summary_dir = run_dir / 'summary'
    if not log_dir.is_dir():
        raise SystemExit(f'missing log directory: {log_dir}')
    summary_dir.mkdir(parents=True, exist_ok=True)

    out_csv = Path(args.out_csv).resolve() if args.out_csv else summary_dir / 'all_cases.csv'
    out_summary = Path(args.out_summary).resolve() if args.out_summary else summary_dir / 'all_cases_summary.csv'

    log_index = build_log_index(log_dir / 'exit_codes.csv')
    rows: list[dict[str, str]] = []
    counter = [0]

    for log_file in sorted(log_dir.glob('*.log')):
        if log_file.name in {'commands.log', 'exit_codes.csv'}:
            continue
        text = log_file.read_text(encoding='utf-8', errors='ignore')
        lines = text.splitlines()
        meta = log_index.get(str(log_file.resolve()), {})
        parse_possible_read_blocks(log_file, lines, meta, rows, counter)
        parse_single_line_cases(log_file, lines, meta, rows, counter)

    fieldnames = [
        'case_id', 'case_kind', 'step', 'name', 'exit_code', 'elapsed_sec',
        'source_log', 'source_channel', 'file', 'line', 'column', 'message',
        'bitcode_snippet', 'raw_text',
    ]
    with out_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    by_kind = Counter(r['case_kind'] for r in rows)
    by_step = Counter((r['step'], r['name']) for r in rows)
    with out_summary.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['category', 'key', 'count'])
        for kind, count in sorted(by_kind.items()):
            w.writerow(['case_kind', kind, count])
        for (step, name), count in sorted(by_step.items()):
            w.writerow(['step_name', f'{step}:{name}', count])

    print(out_csv)
    print(out_summary)
    print(f'total_cases={len(rows)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
