#!/usr/bin/env python3

import argparse
import csv
import json
import re
from pathlib import Path




# python3 CompilerOptimization/Tools/phasar/DiffCheck/DiffCheck.py \
#   -r "<psr-report.txt路径>" \
#   -s "<git源码根目录>" \ 
#   --out-csv  <csv路径> --out-json <json路径>








USE_HEADER_RE = re.compile(r"^-+\s+(\d+)\.\s+Use")


def parse_report(report_path: Path):
    lines = report_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    cases = []
    cur = None

    for line in lines:
        m = USE_HEADER_RE.match(line)
        if m:
            if cur is not None:
                cases.append(cur)
            cur = {
                "case": int(m.group(1)),
                "file": "",
                "line": None,
                "source": "",
                "function": "",
            }
            continue

        if cur is None:
            continue

        if line.startswith("File"):
            cur["file"] = line.split(":", 1)[1].strip() if ":" in line else ""
        elif line.startswith("Line"):
            raw = line.split(":", 1)[1].strip() if ":" in line else ""
            try:
                cur["line"] = int(raw)
            except ValueError:
                cur["line"] = None
        elif line.startswith("Source code"):
            cur["source"] = line.split(":", 1)[1].strip() if ":" in line else ""
        elif line.startswith("Function"):
            cur["function"] = line.split(":", 1)[1].strip() if ":" in line else ""

    if cur is not None:
        cases.append(cur)

    return cases


def try_suffix_resolve(source_root: Path, report_file: Path):
    parts = report_file.parts
    for i in range(len(parts)):
        candidate = source_root.joinpath(*parts[i:])
        if candidate.exists():
            return candidate
    return None


def resolve_to_source(source_root: Path, report_file_str: str):
    if not report_file_str:
        return None, "empty_file"

    rf = Path(report_file_str)

    if not rf.is_absolute():
        candidate = (source_root / report_file_str).resolve()
        if candidate.exists():
            return candidate, "relative_join"
        candidate2 = (source_root / report_file_str.lstrip("./")).resolve()
        if candidate2.exists():
            return candidate2, "relative_join"
        return None, "missing_file"

    source_root_resolved = source_root.resolve()
    rf_resolved = rf.resolve() if rf.exists() else rf

    try:
        rel = rf_resolved.relative_to(source_root_resolved)
        candidate = source_root_resolved / rel
        if candidate.exists():
            return candidate, "under_source_root"
    except Exception:
        pass

    suffix_candidate = try_suffix_resolve(source_root_resolved, rf)
    if suffix_candidate is not None:
        return suffix_candidate.resolve(), "suffix_match"

    return None, "missing_file"


def compare_cases(cases, source_root: Path):
    rows = []

    for c in cases:
        case_id = int(c.get("case", 0) or 0)
        report_file = str(c.get("file", "") or "")
        report_line = c.get("line", None)
        report_source = str(c.get("source", "") or "")
        func = str(c.get("function", "") or "")

        resolved_path, resolve_mode = resolve_to_source(source_root, report_file)

        status = "unknown"
        reason = ""
        actual_source = ""
        resolved_relative = ""

        line_no = int(report_line) if isinstance(report_line, int) else 0

        if resolved_path is None:
            status = "missing_file"
            reason = "file not found under source root"
        else:
            try:
                resolved_relative = str(resolved_path.resolve().relative_to(source_root.resolve()))
            except Exception:
                resolved_relative = str(resolved_path)

            src_lines = resolved_path.read_text(encoding="utf-8", errors="ignore").splitlines()

            if line_no < 1 or line_no > len(src_lines):
                status = "line_oob"
                reason = f"line {line_no} out of range (1..{len(src_lines)})"
            else:
                actual_source = src_lines[line_no - 1]
                if actual_source.strip() == report_source.strip():
                    status = "match"
                else:
                    status = "mismatch"
                    reason = "source text mismatch"

        rows.append(
            {
                "case": case_id,
                "file": report_file,
                "line": line_no,
                "function": func,
                "status": status,
                "report_source": report_source,
                "actual_source": actual_source,
                "reason": reason,
                "resolve_mode": resolve_mode,
                "resolved_relative": resolved_relative,
                "resolved_path": str(resolved_path) if resolved_path else "",
            }
        )

    return rows


def sanitize_name(name: str):
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name)


def main():
    parser = argparse.ArgumentParser(
        description="Validate PhASAR psr-report.txt entries against source code lines."
    )
    parser.add_argument("report_pos", nargs="?", help="Path to psr-report.txt")
    parser.add_argument("source_pos", nargs="?", help="Path to git source root")
    parser.add_argument("-r", "--report", help="Path to psr-report.txt")
    parser.add_argument("-s", "--source-root", help="Path to git source root")
    parser.add_argument("--out-csv", help="Output CSV path")
    parser.add_argument("--out-json", help="Output JSON path")
    args = parser.parse_args()

    report_arg = args.report or args.report_pos
    source_arg = args.source_root or args.source_pos

    if not report_arg or not source_arg:
        parser.error("report and source-root are required")

    report_path = Path(report_arg).resolve()
    source_root = Path(source_arg).resolve()

    if not report_path.exists():
        raise SystemExit(f"report not found: {report_path}")
    if not source_root.exists():
        raise SystemExit(f"source root not found: {source_root}")

    default_tag = sanitize_name(source_root.name.lower())
    out_csv = Path(args.out_csv).resolve() if args.out_csv else report_path.parent / f"target_{default_tag}_linecheck.csv"
    out_json = Path(args.out_json).resolve() if args.out_json else report_path.parent / f"target_{default_tag}_linecheck.json"

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    cases = parse_report(report_path)
    rows = compare_cases(cases, source_root)

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "case",
                "file",
                "line",
                "function",
                "status",
                "report_source",
                "actual_source",
                "reason",
                "resolve_mode",
                "resolved_relative",
                "resolved_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    out_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = {}
    for r in rows:
        st = str(r["status"])
        counts[st] = counts.get(st, 0) + 1

    print(f"report: {report_path}")
    print(f"source_root: {source_root}")
    print(f"total_cases: {len(rows)}")
    print(f"status_counts: {counts}")
    print(f"csv: {out_csv}")
    print(f"json: {out_json}")


if __name__ == "__main__":
    main()
