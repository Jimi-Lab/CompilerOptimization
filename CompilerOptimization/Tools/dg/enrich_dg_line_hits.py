#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


WORKSPACE = Path("/home/jimi/PaperExperiment")
WORK_PREFIX = "/work/PaperExperiment"


def normalize_source_path(raw: str) -> Path | None:
    raw = (raw or "").strip()
    if not raw:
        return None

    if raw.startswith(WORK_PREFIX):
        return WORKSPACE / raw[len(WORK_PREFIX) + 1 :]

    path = Path(raw)
    if path.is_absolute():
        return path

    return WORKSPACE / raw


def classify_confidence(line_no: int, candidate_count: int, exists: bool) -> str:
    if line_no <= 0 or candidate_count == 0 or not exists:
        return "low"
    if candidate_count == 1:
        return "high"
    return "medium"


def extract_snippet(path: Path, line_no: int, context: int) -> tuple[str, int, int, bool]:
    if line_no <= 0 or not path.exists() or not path.is_file():
        return "", 0, 0, False

    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if line_no > len(lines):
        return "", 0, 0, False

    start = max(1, line_no - context)
    end = min(len(lines), line_no + context)
    snippet_lines = []
    for idx in range(start, end + 1):
        prefix = ">" if idx == line_no else " "
        snippet_lines.append(f"{prefix}{idx}: {lines[idx - 1]}")
    return "\n".join(snippet_lines), start, end, True


def enrich(input_csv: Path, output_csv: Path, context: int) -> int:
    with input_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    enriched_rows = []
    for row in rows:
        source_files = [item.strip() for item in (row.get("source_files") or "").split(";") if item.strip()]
        if not source_files:
            source_files = [""]

        candidate_count = int(row.get("source_count") or 0)
        line_no = int(row.get("line") or 0)
        column_no = int(row.get("column") or 0)

        for index, raw_source in enumerate(source_files, start=1):
            normalized = normalize_source_path(raw_source)
            exists = bool(normalized and normalized.exists() and normalized.is_file())
            snippet, start_line, end_line, snippet_ok = extract_snippet(normalized, line_no, context) if normalized else ("", 0, 0, False)
            enriched_rows.append(
                {
                    "step": row.get("step", ""),
                    "analysis_kind": row.get("analysis_kind", ""),
                    "analysis_mode": row.get("analysis_mode", ""),
                    "line": line_no,
                    "column": column_no,
                    "candidate_index": index,
                    "candidate_count": candidate_count,
                    "raw_source_file": raw_source,
                    "normalized_source_file": str(normalized) if normalized else "",
                    "source_exists": "1" if exists else "0",
                    "confidence": classify_confidence(line_no, candidate_count, exists),
                    "snippet_available": "1" if snippet_ok else "0",
                    "snippet_start_line": start_line,
                    "snippet_end_line": end_line,
                    "output_file": row.get("output_file", ""),
                    "output_line": row.get("output_line", ""),
                    "dg_text": row.get("text", ""),
                    "code_snippet": snippet,
                }
            )

    fieldnames = [
        "step",
        "analysis_kind",
        "analysis_mode",
        "line",
        "column",
        "candidate_index",
        "candidate_count",
        "raw_source_file",
        "normalized_source_file",
        "source_exists",
        "confidence",
        "snippet_available",
        "snippet_start_line",
        "snippet_end_line",
        "output_file",
        "output_line",
        "dg_text",
        "code_snippet",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    return len(enriched_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich DG line_hits.csv with real source snippets")
    parser.add_argument("input_csv", help="Path to DG line_hits.csv")
    parser.add_argument("-o", "--output", help="Output CSV path (default: line_hits_enriched.csv next to input)")
    parser.add_argument("--context", type=int, default=10, help="Number of source lines before/after target line")
    args = parser.parse_args()

    input_csv = Path(args.input_csv).resolve()
    output_csv = Path(args.output).resolve() if args.output else input_csv.with_name("line_hits_enriched.csv")

    count = enrich(input_csv, output_csv, args.context)
    print(output_csv)
    print(f"rows={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
