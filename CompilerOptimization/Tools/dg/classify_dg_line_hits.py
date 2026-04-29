#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path


PTA_KEYWORDS = [
    "malloc", "calloc", "realloc", "free", "new ", "delete", "->", "*", "&", "[", "]",
    "ptr", "pointer", "alloc", "address", "field", "struct",
]

DDA_KEYWORDS = [
    "=", "+=", "-=", "*=", "/=", "%=", "++", "--", "memcpy", "memmove", "memset",
    "store", "write", "read", "copy", "update", "push", "pop", "insert", "erase",
]

CDA_KEYWORDS = [
    "if", "switch", "case", "for", "while", "do", "else", "?", "return", "break", "continue",
]

COMMENT_ONLY_RE = re.compile(r"^\s*(//|/\*|\*|\*/)?\s*$")


def target_code_line(snippet: str) -> str:
    for line in snippet.splitlines():
        if line.startswith(">"):
            parts = line.split(":", 1)
            return parts[1].strip() if len(parts) == 2 else line[1:].strip()
    return ""


def contains_keyword(code: str, keywords: list[str]) -> tuple[bool, str]:
    lower = f" {code.lower()} "
    for kw in keywords:
        if kw in {"*", "&", "[", "]", "?", "="}:
            if kw in code:
                return True, kw
            continue
        if kw.lower() in lower:
            return True, kw
    return False, ""


def classify_row(row: dict) -> tuple[str, str, str]:
    line = int(row.get("line") or 0)
    column = int(row.get("column") or 0)
    candidate_count = int(row.get("candidate_count") or 0)
    source_exists = row.get("source_exists") == "1"
    snippet_available = row.get("snippet_available") == "1"

    if line <= 0 or column <= 0 or candidate_count == 0 or not source_exists or not snippet_available:
        return "L0-Unmappable", "line0-or-no-source", "缺失可用源码位置"

    if candidate_count > 1:
        return "L1-Ambiguous", "multi-file", "同一 line:column 对应多个源码文件"

    code = target_code_line(row.get("code_snippet", ""))
    if not code or COMMENT_ONLY_RE.match(code):
        return "L2-Drift-Suspected", "no-actionable-code", "目标行为空白/注释/无明显语义"

    analysis_kind = (row.get("analysis_kind") or "").upper()
    if analysis_kind == "PTA":
        ok, kw = contains_keyword(code, PTA_KEYWORDS)
        return (
            ("L3-Matched" if ok else "L2-Drift-Suspected"),
            (f"pta-keyword:{kw}" if ok else "pta-no-keyword"),
            (f"PTA 目标行匹配关键词 `{kw}`" if ok else "PTA 目标行未体现明显指针/对象操作"),
        )
    if analysis_kind == "DDA":
        ok, kw = contains_keyword(code, DDA_KEYWORDS)
        return (
            ("L3-Matched" if ok else "L2-Drift-Suspected"),
            (f"dda-keyword:{kw}" if ok else "dda-no-keyword"),
            (f"DDA 目标行匹配关键词 `{kw}`" if ok else "DDA 目标行未体现明显读写/更新语义"),
        )
    if analysis_kind == "CDA":
        ok, kw = contains_keyword(code, CDA_KEYWORDS)
        return (
            ("L3-Matched" if ok else "L2-Drift-Suspected"),
            (f"cda-keyword:{kw}" if ok else "cda-no-keyword"),
            (f"CDA 目标行匹配关键词 `{kw}`" if ok else "CDA 目标行未体现明显控制语义"),
        )

    return "L4-Unknown", "unknown-analysis-kind", "未知分析类型，需人工判断"


def classify_csv(input_csv: Path, output_csv: Path) -> int:
    with input_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    enriched = []
    for row in rows:
        label, reason_key, review_note = classify_row(row)
        new_row = dict(row)
        new_row["final_label"] = label
        new_row["reason_key"] = reason_key
        new_row["review_note"] = review_note
        enriched.append(new_row)

    fieldnames = list(rows[0].keys()) + ["final_label", "reason_key", "review_note"]
    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched)
    return len(enriched)


def main() -> int:
    parser = argparse.ArgumentParser(description="Heuristically classify enriched DG line hits into L0/L1/L2/L3/L4")
    parser.add_argument("input_csv", help="Path to line_hits_enriched.csv")
    parser.add_argument("-o", "--output", help="Output CSV path (default: dg_manual_labels.csv next to input)")
    args = parser.parse_args()

    input_csv = Path(args.input_csv).resolve()
    output_csv = Path(args.output).resolve() if args.output else input_csv.with_name("dg_manual_labels.csv")
    count = classify_csv(input_csv, output_csv)
    print(output_csv)
    print(f"rows={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
