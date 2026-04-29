#!/usr/bin/env python3
"""Audit yapall P0 rows emitted by collect_yapall_o2g_cases.py."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path("/home/jimi/PaperExperiment/CompilerOptimization/Result/AllUsefulCases/yapall/O2-g")
TOOL_CASES = OUT_DIR / "tool_cases.csv"

UNIQUE_FIELDS = [
    "target",
    "priority_reason",
    "reported_file",
    "reported_line",
    "reported_column",
    "location_validity",
    "source_region",
    "example_case_uid",
    "example_raw_artifact",
    "example_raw_row_or_line",
    "source_snippet",
    "validation_status",
]


def read_lines(path: str, cache: dict[str, list[str] | None]) -> list[str] | None:
    if not path:
        return None
    if path not in cache:
        p = Path(path)
        if not p.exists() or not p.is_file():
            cache[path] = None
        else:
            cache[path] = p.read_text(encoding="utf-8", errors="replace").splitlines()
    return cache[path]


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def non_code_status(text: str) -> bool:
    stripped = text.strip()
    return not stripped or stripped.startswith(("//", "/*", "*/", "#"))


def validate(row: dict, cache: dict[str, list[str] | None]) -> str:
    reason = row.get("priority_reason", "")
    path = row.get("reported_file", "")
    line_no = parse_int(row.get("reported_line", ""))
    col_no = parse_int(row.get("reported_column", ""))
    lines = read_lines(path, cache)

    if reason == "LineZero":
        if lines is not None and line_no == 0:
            return "ok"
        return "failed"

    if reason == "LineOutOfRange":
        if lines is not None and line_no is not None and line_no > len(lines):
            return "ok"
        return "failed"

    if reason == "ColumnOutOfRange":
        if lines is not None and line_no is not None and 1 <= line_no <= len(lines):
            if col_no is not None and col_no > len(lines[line_no - 1]):
                return "ok"
        return "failed"

    if reason == "MissingSourceFile":
        if lines is None:
            return "ok"
        return "failed"

    if reason == "SourceLineEmptyOrNonCode":
        if lines is not None and line_no is not None and 1 <= line_no <= len(lines):
            if non_code_status(lines[line_no - 1]):
                return "ok"
        return "failed"

    return "not_checked"


def main() -> None:
    cache: dict[str, list[str] | None] = {}
    total = 0
    by_target = Counter()
    by_reason = Counter()
    unique: dict[tuple[str, str, str, str], dict] = {}
    validation = Counter()
    target_reason = defaultdict(Counter)

    with TOOL_CASES.open(newline="", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            if row.get("priority") != "P0":
                continue
            total += 1
            target = row.get("target", "")
            reason = row.get("priority_reason", "")
            by_target[target] += 1
            by_reason[reason] += 1
            target_reason[target][reason] += 1
            key = (
                row.get("reported_file", ""),
                row.get("reported_line", ""),
                row.get("reported_column", ""),
                reason,
            )
            if key not in unique:
                status = validate(row, cache)
                validation[status] += 1
                unique[key] = {
                    "target": target,
                    "priority_reason": reason,
                    "reported_file": row.get("reported_file", ""),
                    "reported_line": row.get("reported_line", ""),
                    "reported_column": row.get("reported_column", ""),
                    "location_validity": row.get("location_validity", ""),
                    "source_region": row.get("source_region", ""),
                    "example_case_uid": row.get("case_uid", ""),
                    "example_raw_artifact": row.get("raw_artifact", ""),
                    "example_raw_row_or_line": row.get("raw_row_or_line", ""),
                    "source_snippet": row.get("source_snippet", ""),
                    "validation_status": status,
                }

    unique_path = OUT_DIR / "p0_unique_locations.csv"
    with unique_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=UNIQUE_FIELDS)
        writer.writeheader()
        for row in unique.values():
            writer.writerow(row)

    unique_by_reason = Counter(row["priority_reason"] for row in unique.values())
    unique_by_target = Counter(row["target"] for row in unique.values())
    unique_files = {row["reported_file"] for row in unique.values() if row["reported_file"]}

    lines = []
    lines.append("# yapall P0 Final Audit\n\n")
    lines.append("## Scope\n")
    lines.append("- tool: yapall\n")
    lines.append("- universe: LLVM14-O2-g / O2-g only\n")
    lines.append(f"- source CSV: {TOOL_CASES}\n")
    lines.append(f"- unique locations CSV: {unique_path}\n\n")
    lines.append("## P0 Counts\n")
    lines.append(f"- P0 rows: {total}\n")
    lines.append(f"- P0 unique locations: {len(unique)}\n")
    lines.append(f"- P0 unique files: {len(unique_files)}\n\n")
    lines.append("## P0 Rows By Reason\n")
    for key, value in by_reason.most_common():
        lines.append(f"- {key}: {value}\n")
    lines.append("\n## P0 Unique Locations By Reason\n")
    for key, value in unique_by_reason.most_common():
        lines.append(f"- {key}: {value}\n")
    lines.append("\n## P0 Rows By Target\n")
    for key, value in by_target.most_common():
        lines.append(f"- {key}: {value}\n")
    lines.append("\n## P0 Unique Locations By Target\n")
    for key, value in unique_by_target.most_common():
        lines.append(f"- {key}: {value}\n")
    lines.append("\n## Validation\n")
    for key, value in validation.most_common():
        lines.append(f"- {key}: {value}\n")
    lines.append("\n## Interpretation Notes\n")
    lines.append("- P0 rows are relation/use-site evidence rows, not independent paper cases.\n")
    lines.append("- Unique locations deduplicate by reported_file, reported_line, reported_column, and priority_reason.\n")
    if unique_by_reason.get("LineZero"):
        lines.append("- LineZero means the debug/source mapping reports line 0 in a project file.\n")
    if unique_by_reason.get("SourceLineEmptyOrNonCode"):
        lines.append("- SourceLineEmptyOrNonCode means the mapped project source line is empty, comment-only, or preprocessor-only while the row is tied to a concrete yapall issue site.\n")
    (OUT_DIR / "p0_final_audit.md").write_text("".join(lines), encoding="utf-8")

    print(f"P0 rows: {total}")
    print(f"P0 unique locations: {len(unique)}")
    print(f"P0 unique files: {len(unique_files)}")
    print(f"validation: {dict(validation)}")


if __name__ == "__main__":
    main()
