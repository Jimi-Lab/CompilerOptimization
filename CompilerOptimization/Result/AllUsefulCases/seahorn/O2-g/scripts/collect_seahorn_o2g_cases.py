#!/usr/bin/env python3
"""Collect SeaHorn O2-g File/Line/Column/Bitcode blocks as useful cases."""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


csv.field_size_limit(sys.maxsize)

ROOT = Path("/home/jimi/PaperExperiment")
RESULT_TXT = ROOT / "CompilerOptimization/Result/AllUsefulCases/seahorn/result.txt"
OUT_DIR = ROOT / "CompilerOptimization/Result/AllUsefulCases/seahorn/O2-g"
TARGET_ROOT = ROOT / "CompilerOptimization/Target"

TARGET_ALIASES = {
    "tengine": "Tengine",
}

CASE_FIELDS = [
    "case_uid",
    "target",
    "tool",
    "priority",
    "priority_reason",
    "case_kind",
    "status_label",
    "run_dir",
    "run_id",
    "mode",
    "input_bc",
    "input_ll",
    "raw_artifact",
    "raw_row_or_line",
    "reported_file",
    "reported_line",
    "reported_column",
    "location_validity",
    "source_region",
    "project_source_only",
    "header_context",
    "ir_function",
    "ir_instruction",
    "ir_line",
    "ir_snippet",
    "source_snippet",
    "message",
    "root_cause_hint",
    "confidence",
    "needs_manual_review",
    "manual_verdict",
    "evidence_files",
    "notes",
]

RUN_FIELDS = [
    "target",
    "tool",
    "selected",
    "run_dir",
    "run_id",
    "universe",
    "input_bc",
    "input_ll",
    "mode",
    "status",
    "success_modes",
    "failed_modes",
    "timeout_modes",
    "raw_artifacts",
    "reason",
    "excluded_reason",
    "notes",
]


def parse_result_list() -> list[tuple[str, Path]]:
    current = ""
    runs: list[tuple[str, Path]] = []
    for line in RESULT_TXT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        if line.startswith("/"):
            if "/log/" in line:
                continue
            if not current:
                raise ValueError(f"run path without target header: {line}")
            runs.append((current, Path(line)))
    return runs


def target_source_root(target: str) -> Path:
    return TARGET_ROOT / TARGET_ALIASES.get(target, target)


def evidence_list(*paths: Path | None) -> str:
    return ";".join(str(path) for path in paths if path and path.exists())


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def parse_commands_input_bc(run_dir: Path, target: str) -> str:
    commands = run_dir / "log/commands.log"
    if not commands.exists():
        return ""
    text = commands.read_text(encoding="utf-8", errors="replace")
    paths = re.findall(r"((?:/home/jimi/PaperExperiment|/work/PaperExperiment)/[^\s'\"]+?\.bc)", text)
    paths = [
        "/home/jimi/PaperExperiment/" + p[len("/work/PaperExperiment/") :]
        if p.startswith("/work/PaperExperiment/")
        else p
        for p in paths
    ]
    preferred = [
        p
        for p in paths
        if f"/CompilerOptimization/CompilerResult/{target}/LLVM14-O2-g/" in p
    ]
    if target == "tengine":
        preferred.extend(
            p
            for p in paths
            if "/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/" in p
        )
    if preferred:
        return preferred[0]
    for p in paths:
        if "/CompilerOptimization/CompilerResult/" in p and "/LLVM14-O2-g/" in p:
            return p
    return paths[0] if paths else ""


def classify_region(target: str, source_path: Path, reported_file: str) -> tuple[str, str, str]:
    suffix = source_path.suffix.lower()
    is_header = suffix in {".h", ".hh", ".hpp", ".hxx", ".inc"}
    root = target_source_root(target)
    try:
        rel = source_path.relative_to(root)
        rel_parts = {part.lower() for part in rel.parts}
        rel_text = str(rel).lower()
    except ValueError:
        rel_parts = set()
        rel_text = str(source_path).lower()

    third_party_markers = {
        "deps",
        "third_party",
        "third-party",
        "external",
        "extern",
        "vendor",
        "vendors",
        "contrib",
    }
    third_party_names = {"stb_image.h", "xxhash.h", "fast_float.h"}
    is_third_party = bool(rel_parts & third_party_markers) or source_path.name.lower() in third_party_names
    if "/usr/include/" in str(source_path) or "/include/c++/" in str(source_path):
        region = "system_header" if is_header else "unknown"
    elif source_path.is_absolute() and root in source_path.parents:
        if is_third_party:
            region = "third_party_header" if is_header else "third_party_source"
        else:
            region = "project_header" if is_header else "project_source"
    elif reported_file.startswith("Target/"):
        if is_third_party or "deps/" in rel_text:
            region = "third_party_header" if is_header else "third_party_source"
        else:
            region = "project_header" if is_header else "project_source"
    else:
        region = "unknown"

    if region.endswith("_header"):
        header_context = region
    elif is_header:
        header_context = "unknown"
    else:
        header_context = "not_header"
    project_source_only = "1" if region == "project_source" else "0"
    return region, header_context, project_source_only


def source_candidates(target: str, reported_file: str) -> list[Path]:
    root = target_source_root(target)
    candidates: list[Path] = []
    raw = reported_file.strip()
    if not raw:
        return candidates

    path = Path(raw)

    work_markers = [
        f"CompilerOptimization/CompilerResult/{target}/LLVM14-O2-g/work/",
        f"CompilerOptimization/Result/{target}/seahorn/seahorn-O2-g/work/",
    ]
    for marker in work_markers:
        if marker in raw:
            suffix = raw.split(marker, 1)[1]
            parts = Path(suffix).parts
            if len(parts) >= 2:
                candidates.append(root / Path(*parts[1:]))

    if path.is_absolute():
        candidates.append(path)
        marker = "/home/jimi/PaperExperiment/"
        if raw.startswith(marker):
            candidates.append(ROOT / raw[len(marker) :])
        work_marker = "/work/PaperExperiment/"
        if raw.startswith(work_marker):
            candidates.append(ROOT / raw[len(work_marker) :])

    if raw.startswith("Target/"):
        candidates.append(ROOT / "CompilerOptimization" / raw)
        after_target = raw[len("Target/") :]
        parts = Path(after_target).parts
        if parts:
            candidates.append(TARGET_ROOT / Path(*parts))
    if raw.startswith("CompilerOptimization/"):
        candidates.append(ROOT / raw)

    candidates.append(root / raw)

    # SeaHorn sometimes reports only a compile-unit basename, notably in redis.
    if "/" not in raw:
        for sub in ("src", "deps", "deps/fast_float", "deps/xxhash", "deps/lua/src"):
            candidates.append(root / sub / raw)
        candidates.extend(sorted(root.rglob(raw)))

    unique: list[Path] = []
    seen: set[str] = set()
    for cand in candidates:
        key = str(cand)
        if key not in seen:
            seen.add(key)
            unique.append(cand)
    return unique


def resolve_source(target: str, reported_file: str) -> tuple[Path | None, str, list[Path]]:
    candidates = source_candidates(target, reported_file)
    existing = [p for p in candidates if p.exists()]
    if not existing:
        return None, "missing", candidates
    target_root = target_source_root(target)
    under_target = [p for p in existing if target_root in p.parents or p == target_root]
    pool = under_target or existing
    if len(pool) == 1:
        return pool[0], "exact", candidates
    # Prefer source roots over duplicated build copies, then shorter paths.
    pool = sorted(pool, key=lambda p: (0 if target_root in p.parents else 1, len(str(p)), str(p)))
    return pool[0], "ambiguous_chose_first", candidates


def parse_int(text: str) -> int:
    try:
        return int(str(text).strip())
    except (TypeError, ValueError):
        return 0


def line_is_comment_or_empty(text: str) -> bool:
    stripped = text.strip()
    return (
        not stripped
        or stripped.startswith("//")
        or stripped.startswith("/*")
        or stripped.startswith("* ")
        or stripped == "*"
        or stripped.startswith("*/")
    )


def source_snippet(lines: list[str], line_no: int, context: int = 2) -> str:
    if line_no < 1 or line_no > len(lines):
        return ""
    start = max(1, line_no - context)
    end = min(len(lines), line_no + context)
    rendered = []
    for no in range(start, end + 1):
        marker = ">" if no == line_no else " "
        rendered.append(f"{marker}{no}: {lines[no - 1]}")
    return "\n".join(rendered)


def analyze_location(target: str, reported_file: str, line_no: int, column_no: int) -> dict[str, str]:
    source_path, resolution, candidates = resolve_source(target, reported_file)
    info = {
        "resolved_source": "",
        "source_resolution": resolution,
        "location_validity": "unknown",
        "source_region": "unknown",
        "project_source_only": "0",
        "header_context": "unknown",
        "source_snippet": "",
        "source_line": "",
        "notes": "",
    }
    if source_path is None:
        info["location_validity"] = "missing_file"
        info["notes"] = "source_candidates=" + "|".join(str(p) for p in candidates[:10])
        return info

    info["resolved_source"] = str(source_path)
    region, header_context, project_source_only = classify_region(target, source_path, reported_file)
    info["source_region"] = region
    info["header_context"] = header_context
    info["project_source_only"] = project_source_only

    if line_no == 0:
        info["location_validity"] = "line_zero"
        return info

    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if line_no > len(lines):
        info["location_validity"] = "line_out_of_range"
        info["notes"] = f"resolved_source={source_path};total_lines={len(lines)}"
        return info

    source_line = lines[line_no - 1]
    info["source_line"] = source_line
    info["source_snippet"] = source_snippet(lines, line_no)
    if column_no < 1 or column_no > len(source_line) + 1:
        info["location_validity"] = "column_out_of_range"
    elif line_is_comment_or_empty(source_line):
        info["location_validity"] = "empty_or_comment_line"
    elif source_line.strip().startswith("#"):
        info["location_validity"] = "preprocessor_only"
    else:
        info["location_validity"] = "valid"

    extra_notes = [f"resolved_source={source_path}", f"source_resolution={resolution}"]
    if resolution == "ambiguous_chose_first":
        extra_notes.append("candidate_count=" + str(len([p for p in candidates if p.exists()])))
    info["notes"] = ";".join(extra_notes)
    return info


def priority_for_location(location_validity: str, source_region: str) -> tuple[str, str, str, str, str]:
    p0_reasons = {
        "missing_file": "MissingSourceFile",
        "line_zero": "LineZero",
        "line_out_of_range": "LineOutOfRange",
        "column_out_of_range": "ColumnOutOfRange",
        "empty_or_comment_line": "SourceLineEmptyOrNonCode",
        "preprocessor_only": "SourceLinePreprocessorOnly",
    }
    if location_validity in p0_reasons:
        return (
            "P0",
            p0_reasons[location_validity],
            "LocationInvalid",
            "location_invalid_or_untrusted_debug_location",
            "0",
        )
    if source_region in {"system_header", "unknown"}:
        return (
            "P2",
            "ExternalOrUnresolvedSource",
            "RunOrLocationWeakEvidence",
            "external_or_unresolved_source_location",
            "1",
        )
    return (
        "P1",
        "ValidBitcodeSourceMappingNeedsSemanticReview",
        "IRSourceSemanticCandidate",
        "optimized_ir_undefined_read_mapping_candidate",
        "1",
    )


def run_status(run_dir: Path) -> str:
    if (run_dir / "status/success.marker").exists():
        return "ok"
    if (run_dir / "status/failed.marker").exists():
        return "partial/failure"
    return "unknown"


def collect() -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    case_rows: list[dict[str, str]] = []
    run_rows: list[dict[str, str]] = []
    stats: dict[str, object] = {
        "targets": {},
        "priority_counts": Counter(),
        "priority_reason_counts": Counter(),
        "location_validity_counts": Counter(),
        "source_region_counts": Counter(),
        "case_kind_counts": Counter(),
    }
    runs = parse_result_list()
    for target, run_dir in runs:
        all_cases = run_dir / "summary/all_cases.csv"
        commands = run_dir / "log/commands.log"
        final_report = run_dir / "report/final_report.md"
        overview = run_dir / "summary/overview.csv"
        failure_inventory = run_dir / "summary/failure_inventory.csv"
        horn_status = run_dir / "summary/horn_status.csv"
        input_bc = parse_commands_input_bc(run_dir, target)
        input_ll = str(Path(input_bc).with_suffix(".ll")) if input_bc else ""

        rows = read_csv(all_cases)
        block_rows = [
            row
            for row in rows
            if row.get("case_kind") == "undefined_read_block"
            and row.get("file")
            and row.get("line")
            and row.get("column")
            and row.get("bitcode_snippet")
        ]
        by_kind = Counter(row.get("case_kind", "") for row in rows)
        mode_counts = Counter(row.get("name", "") for row in block_rows)
        raw_logs = sorted({row.get("source_log", "") for row in block_rows if row.get("source_log")})

        run_rows.append(
            {
                "target": target,
                "tool": "seahorn",
                "selected": "1",
                "run_dir": str(run_dir),
                "run_id": run_dir.name,
                "universe": "O2-g",
                "input_bc": input_bc,
                "input_ll": input_ll if Path(input_ll).exists() else "",
                "mode": "all_cases.undefined_read_block",
                "status": run_status(run_dir),
                "success_modes": ";".join(mode for mode, count in sorted(mode_counts.items()) if count),
                "failed_modes": "",
                "timeout_modes": "",
                "raw_artifacts": evidence_list(all_cases, commands, final_report, overview, failure_inventory, horn_status),
                "reason": "user_selected_from_result_txt",
                "excluded_reason": "",
                "notes": f"all_cases_rows={len(rows)};undefined_read_blocks={len(block_rows)};case_kind_counts={dict(by_kind)}",
            }
        )

        target_stats = {
            "all_cases_rows": len(rows),
            "undefined_read_blocks": len(block_rows),
            "case_kind_counts": dict(by_kind),
            "mode_counts": dict(mode_counts),
            "priority_counts": Counter(),
            "location_validity_counts": Counter(),
            "source_region_counts": Counter(),
            "raw_logs": raw_logs,
        }

        for local_index, row in enumerate(block_rows, start=1):
            line_no = parse_int(row.get("line", "0"))
            column_no = parse_int(row.get("column", "0"))
            loc = analyze_location(target, row.get("file", ""), line_no, column_no)
            priority, reason, normalized_kind, root_cause, needs_review = priority_for_location(
                loc["location_validity"], loc["source_region"]
            )
            confidence = "0.95" if priority == "P0" else "0.65" if priority == "P1" else "0.40"
            status_label = "reported"
            source_log = Path(row.get("source_log", "")) if row.get("source_log") else None
            case_uid = f"seahorn.{target}.O2g.{local_index:06d}"
            notes = [
                loc["notes"],
                f"all_cases_case_id={row.get('case_id', '')}",
                f"all_cases_step={row.get('step', '')}",
                f"all_cases_name={row.get('name', '')}",
                "collected_from=all_cases.undefined_read_block",
            ]
            if loc["resolved_source"]:
                notes.append(f"resolved_source={loc['resolved_source']}")

            case_rows.append(
                {
                    "case_uid": case_uid,
                    "target": target,
                    "tool": "seahorn",
                    "priority": priority,
                    "priority_reason": reason,
                    "case_kind": normalized_kind,
                    "status_label": status_label,
                    "run_dir": str(run_dir),
                    "run_id": run_dir.name,
                    "mode": row.get("name", ""),
                    "input_bc": input_bc,
                    "input_ll": input_ll if Path(input_ll).exists() else "",
                    "raw_artifact": str(source_log) if source_log else str(all_cases),
                    "raw_row_or_line": row.get("case_id", ""),
                    "reported_file": row.get("file", ""),
                    "reported_line": str(line_no),
                    "reported_column": str(column_no),
                    "location_validity": loc["location_validity"],
                    "source_region": loc["source_region"],
                    "project_source_only": loc["project_source_only"],
                    "header_context": loc["header_context"],
                    "ir_function": "",
                    "ir_instruction": "",
                    "ir_line": "",
                    "ir_snippet": row.get("bitcode_snippet", ""),
                    "source_snippet": loc["source_snippet"],
                    "message": row.get("message", ""),
                    "root_cause_hint": root_cause,
                    "confidence": confidence,
                    "needs_manual_review": needs_review,
                    "manual_verdict": "",
                    "evidence_files": evidence_list(all_cases, source_log, commands, final_report),
                    "notes": ";".join(part for part in notes if part),
                }
            )
            stats["priority_counts"][priority] += 1
            stats["priority_reason_counts"][reason] += 1
            stats["location_validity_counts"][loc["location_validity"]] += 1
            stats["source_region_counts"][loc["source_region"]] += 1
            stats["case_kind_counts"][normalized_kind] += 1
            target_stats["priority_counts"][priority] += 1
            target_stats["location_validity_counts"][loc["location_validity"]] += 1
            target_stats["source_region_counts"][loc["source_region"]] += 1

        stats["targets"][target] = target_stats

    return case_rows, run_rows, stats


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def counter_table(counter: Counter) -> str:
    lines = ["| key | count |", "| --- | ---: |"]
    for key, count in counter.most_common():
        lines.append(f"| `{key}` | {count} |")
    return "\n".join(lines)


def write_reports(case_rows: list[dict[str, str]], run_rows: list[dict[str, str]], stats: dict[str, object]) -> None:
    target_lines = [
        "| target | all_cases rows | blocks | P0 | P1 | P2 | invalid locations | source regions |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for target, raw in stats["targets"].items():
        tstats = raw
        pc = tstats["priority_counts"]
        lv = ", ".join(f"{k}={v}" for k, v in sorted(tstats["location_validity_counts"].items()))
        sr = ", ".join(f"{k}={v}" for k, v in sorted(tstats["source_region_counts"].items()))
        target_lines.append(
            f"| {target} | {tstats['all_cases_rows']} | {tstats['undefined_read_blocks']} | "
            f"{pc.get('P0', 0)} | {pc.get('P1', 0)} | {pc.get('P2', 0)} | {lv} | {sr} |"
        )

    report = f"""# SeaHorn O2-g File/Line/Column/Bitcode Block Collection Report

## Scope

- tool: `seahorn`
- universe: `O2-g` / `LLVM14-O2-g`
- selected runs: `{len(run_rows)}`
- parser source: `summary/all_cases.csv`
- collected case kind: `undefined_read_block`
- rule: collect every block with `File/Line/Column/Bitcode`, preserve duplicates and original per-run order.

## Priority Counts

{counter_table(stats['priority_counts'])}

## Priority Reasons

{counter_table(stats['priority_reason_counts'])}

## Target Summary

{chr(10).join(target_lines)}

## Location Validity

{counter_table(stats['location_validity_counts'])}

## Source Regions

{counter_table(stats['source_region_counts'])}

## Output Files

- `tool_cases.csv`: all collected SeaHorn blocks classified as P0/P1/P2.
- `tool_runs.csv`: selected run manifest from `result.txt`.
- `native_output_profile.md`: notes on SeaHorn native output and block mapping.
- `collection_manifest.json`: parser statistics and selected run list.
"""
    (OUT_DIR / "case_collection_report.md").write_text(report, encoding="utf-8")

    native_profile = """# SeaHorn Native Output Profile

SeaHorn emits several kinds of log events in these runs. This collector only treats
the complete `Possible read of undefined value at` block as a per-case source
mapping candidate because it contains the full quartet:

```text
--- File
--- Line
--- Column
--- Bitcode
```

The collector reads these blocks from `summary/all_cases.csv` as
`case_kind=undefined_read_block`. Rows such as `warning_line`, `error_line`,
`broken_module`, `trivial_safe_warning`, and `undefined_read_summary` are run-level
or tool-level evidence unless a future parser can recover a precise source
location and bitcode anchor from them.

Each collected block is mapped to `CompilerOptimization/Target/<repo>` or the
target's canonical source root, then checked for missing files, invalid line or
column numbers, empty/comment/preprocessor-only lines, and source-region class.
"""
    (OUT_DIR / "native_output_profile.md").write_text(native_profile, encoding="utf-8")

    manifest = {
        "tool": "seahorn",
        "universe": "O2-g",
        "result_txt": str(RESULT_TXT),
        "output_dir": str(OUT_DIR),
        "case_count": len(case_rows),
        "run_count": len(run_rows),
        "priority_counts": dict(stats["priority_counts"]),
        "priority_reason_counts": dict(stats["priority_reason_counts"]),
        "location_validity_counts": dict(stats["location_validity_counts"]),
        "source_region_counts": dict(stats["source_region_counts"]),
        "targets": {
            target: {
                "all_cases_rows": tstats["all_cases_rows"],
                "undefined_read_blocks": tstats["undefined_read_blocks"],
                "case_kind_counts": tstats["case_kind_counts"],
                "mode_counts": tstats["mode_counts"],
                "priority_counts": dict(tstats["priority_counts"]),
                "location_validity_counts": dict(tstats["location_validity_counts"]),
                "source_region_counts": dict(tstats["source_region_counts"]),
                "raw_logs": tstats["raw_logs"],
            }
            for target, tstats in stats["targets"].items()
        },
    }
    (OUT_DIR / "collection_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    case_rows, run_rows, stats = collect()
    write_csv(OUT_DIR / "tool_cases.csv", CASE_FIELDS, case_rows)
    write_csv(OUT_DIR / "tool_runs.csv", RUN_FIELDS, run_rows)
    write_reports(case_rows, run_rows, stats)
    print(f"wrote {len(case_rows)} cases and {len(run_rows)} runs to {OUT_DIR}")


if __name__ == "__main__":
    main()
