#!/usr/bin/env python3
"""Collect standardized useful cclyzer++ O2-g cases from ValueCases outputs."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/jimi/PaperExperiment")
OUT_DIR = ROOT / "CompilerOptimization/Result/AllUsefulCases/cclyzer++/O2-g"
TARGET_ROOT = ROOT / "CompilerOptimization/Target"

SELECTED_RUNS = {
    "flatbuffers": ROOT
    / "CompilerOptimization/Result/flatbuffers/cclyzerpp/LLVM14-O2-g/run_20260427_132609_flatbuffers_flatc_O2_g",
    "libsndfile": ROOT
    / "CompilerOptimization/Result/libsndfile/cclyzerpp/LLVM14-O2-g/run_20260427_132609_libsndfile_sndfile_convert_O2_g",
    "tengine": ROOT
    / "CompilerOptimization/Result/tengine/cclyzerpp/LLVM14-O2-g/run_20260427_132038_tengine",
    "zopfli": ROOT
    / "CompilerOptimization/Result/zopfli/cclyzerpp/LLVM14-O2-g/run_20260427_132038_zopfli_O2_g_zopfli_only",
    "lepton": ROOT / "CompilerOptimization/Result/lepton/cclyzerpp/LLVM14-O2-g/run_20260430_154121",
    "masscan": ROOT / "CompilerOptimization/Result/masscan/cclyzerpp/LLVM14-O2-g/run_20260430_120006",
    "zfp": ROOT / "CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927",
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


def read_tsv_first(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return rows[0] if rows else {}


def remap_path(path_text: str) -> Path:
    if not path_text:
        return Path("")
    candidates: list[Path] = []
    if path_text.startswith("/work/PaperExperiment/"):
        candidates.append(ROOT / path_text[len("/work/PaperExperiment/") :])
    if path_text.startswith("/work/"):
        candidates.append(ROOT / path_text[len("/work/") :])
    if path_text.startswith("/home/jimi/PaperExperiment/"):
        candidates.append(Path(path_text))
    if path_text.startswith("CompilerOptimization/"):
        candidates.append(ROOT / path_text)
    candidates.append(Path(path_text))
    for cand in candidates:
        if cand.exists():
            return cand
    return candidates[0]


def target_roots(target: str) -> list[Path]:
    roots = [TARGET_ROOT / target]
    if target == "tengine":
        roots.append(TARGET_ROOT / "Tengine")
    if target == "flatbuffers":
        roots.append(TARGET_ROOT / "flatbuffers")
    if target == "libsndfile":
        roots.append(TARGET_ROOT / "libsndfile")
    if target == "zopfli":
        roots.append(TARGET_ROOT / "zopfli")
    return roots


def resolve_source(target: str, source_file: str) -> tuple[Path, bool]:
    path = remap_path(source_file)
    if path.exists():
        return path, True
    text = source_file or ""
    for root in target_roots(target):
        marker = f"/Target/{root.name}/"
        if marker in text:
            rel = text.split(marker, 1)[1]
            candidate = root / rel
            if candidate.exists():
                return candidate, True
            return candidate, False
    return path, False


def is_header(path: Path) -> bool:
    return path.suffix.lower() in {".h", ".hh", ".hpp", ".hxx", ".inc", ".tcc"}


def classify_source_region(target: str, source_file: str, resolved: Path, exists: bool) -> tuple[str, str, str]:
    if not source_file:
        return "llvm_ir_only", "0", "unknown"
    text = source_file
    suffix_header = is_header(resolved)
    if text.startswith("/usr/") or "/include/c++/" in text or "/lib/gcc/" in text:
        return "system_header" if suffix_header else "system_header", "0", "system_header"
    root_names = {root.name for root in target_roots(target)}
    in_target_tree = "/CompilerOptimization/Target/" in text or any(str(root) in text for root in target_roots(target))
    if in_target_tree:
        parts = set(Path(text).parts)
        third_party_markers = {
            "third_party",
            "3rdparty",
            "external",
            "deps",
            "vendor",
            "stb",
            "onnx",
        }
        if parts & third_party_markers:
            return (
                "third_party_header" if suffix_header else "third_party_source",
                "0",
                "third_party_header" if suffix_header else "not_header",
            )
        # Tengine carries vendored stb headers under examples/tests/common.
        if target == "tengine" and resolved.name.startswith("stb_"):
            return "third_party_header", "0", "third_party_header"
        return (
            "project_header" if suffix_header else "project_source",
            "0" if suffix_header else "1",
            "project_header" if suffix_header else "not_header",
        )
    if any(name in text for name in root_names):
        return (
            "project_header" if suffix_header else "project_source",
            "0" if suffix_header else "1",
            "project_header" if suffix_header else "not_header",
        )
    return ("unknown", "0", "unknown")


def to_int(text: str) -> int | None:
    try:
        if text == "":
            return None
        return int(text)
    except ValueError:
        return None


def source_context(row: dict[str, str]) -> str:
    text = row.get("source_line_text", "")
    context = row.get("source_context", "")
    return text or context


def is_project_region(source_region: str) -> bool:
    return source_region in {"project_source", "project_header"}


def p2_external(reason: str, validity: str) -> tuple[str, str, str, str, str]:
    return "P2", reason, "RunOrLocationWeakEvidence", validity, "1"


def classify_case(row: dict[str, str], source_region: str, source_exists: bool) -> tuple[str, str, str, str, str]:
    mapping = row.get("mapping_status", "")
    line = to_int(row.get("line", ""))
    col = to_int(row.get("column", ""))
    source_file = row.get("source_file", "")

    if line == 0:
        if is_project_region(source_region):
            return "P0", "LineZero", "LocationInvalid", "line_zero", "0"
        return p2_external("ExternalOrUnresolvedLineZero", "line_zero")
    if mapping == "LineOutOfRange":
        if is_project_region(source_region):
            return "P0", "LineOutOfRange", "LocationInvalid", "line_out_of_range", "0"
        return p2_external("ExternalOrUnresolvedLineOutOfRange", "line_out_of_range")
    if mapping == "ColumnOutOfRange":
        if is_project_region(source_region):
            return "P0", "ColumnOutOfRange", "LocationInvalid", "column_out_of_range", "0"
        return p2_external("ExternalOrUnresolvedColumnOutOfRange", "column_out_of_range")
    if mapping == "SourceExistsCodeMismatch":
        if is_project_region(source_region):
            return "P1", "SourceIRMismatchNeedsSemanticReview", "IRSourceMismatch", "valid", "1"
        return p2_external("ExternalOrUnresolvedSourceIRMismatch", "valid")
    if mapping == "SourceFileMissing":
        if not source_file:
            return p2_external("NoSourceFileInFact", "unknown")
        if is_project_region(source_region) and not source_exists:
            return "P0", "MissingSourceFile", "LocationInvalid", "missing_file", "0"
        return "P2", "ExternalOrUnresolvedSource", "RunOrLocationWeakEvidence", "missing_file", "1"
    if mapping == "NoDebugLoc" or row.get("debug_line") == "0" and row.get("debug_column") == "0":
        if is_project_region(source_region):
            return "P1", "NoDebugLocNeedsIRReview", "NoDebugLoc", "no_debug_loc", "1"
        return p2_external("ExternalOrUnresolvedNoDebugLoc", "no_debug_loc")
    if mapping in {"MappedLineOnly", "InlineAttribution", "FunctionMismatch"}:
        if is_project_region(source_region):
            return "P1", mapping, "LocationDrift", "valid", "1"
        return p2_external(f"ExternalOrUnresolved{mapping}", "valid")
    if col == 0:
        if is_project_region(source_region):
            return "P1", "MappedLineOnly", "LocationDrift", "valid", "1"
        return p2_external("ExternalOrUnresolvedMappedLineOnly", "valid")
    if is_project_region(source_region):
        return "P1", "ValidFactNeedsSemanticReview", "LocationDrift", "valid", "1"
    return p2_external("ExternalOrUnresolvedFact", "valid")


def make_message(row: dict[str, str]) -> str:
    parts = [
        row.get("phenomenon_label", ""),
        row.get("relation_name", ""),
        row.get("mapping_status", ""),
    ]
    metric = row.get("metric_name", "")
    if metric:
        parts.append(f"{metric}={row.get('metric_value', '')}")
    return "; ".join(part for part in parts if part)


def collect_cases() -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    cases: list[dict[str, str]] = []
    runs: list[dict[str, str]] = []
    stats: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "cclyzer++",
        "universe": "LLVM14-O2-g",
        "selected_runs": [],
        "input_case_files": [],
        "case_counts_by_target": {},
        "priority_counts": {},
        "priority_reason_counts": {},
        "source_region_counts": {},
        "mapping_status_counts": {},
        "phenomenon_counts": {},
        "notes": [
            "Selected completed LLVM14-O2-g cclyzer++ runs for flatbuffers, libsndfile, tengine, zopfli, lepton, masscan, and zfp.",
            "Per-run ValueCases/all_cases.csv were generated from native relations/*.csv.gz and then reclassified to the useful_cases_matrix_plan.md schema.",
            "The collector does not read extract/candidates.tsv or extract/relation_counts.tsv because those extract summaries can be incomplete.",
            "P0 is restricted to objective invalid source locations in project source/header files.",
            "Semantic source/IR mismatch candidates are P1 for project code and P2 for external/unresolved code.",
            "NoDebugLoc without an objective project source line/column failure is not promoted to P0.",
        ],
    }

    priority_counts = Counter()
    reason_counts = Counter()
    region_counts = Counter()
    mapping_counts = Counter()
    phenomenon_counts = Counter()
    target_counts = Counter()

    for target, run_dir in SELECTED_RUNS.items():
        value_dir = run_dir / "ValueCases"
        case_file = value_dir / "all_cases.csv"
        status_row = read_tsv_first(run_dir / "status/run_status.tsv")
        command_path = run_dir / "commands/command.txt"
        command_artifact = command_path if command_path.exists() else None
        raw_artifacts = [
            case_file,
            run_dir / "relations",
            run_dir / "commands/command.txt",
            run_dir / "status/run_status.tsv",
            run_dir / "log/cclyzerpp.log",
            run_dir / "report/final_report.md",
            value_dir / "analysis_manifest.json",
            value_dir / "inventory/relation_row_counts.tsv",
            value_dir / "index/ir_instruction_index.tsv",
            value_dir / "map/native_fact_source_map.tsv",
            value_dir / "report/final_native_output_analysis.md",
        ]
        raw_artifact_text = ";".join(str(path) for path in raw_artifacts if path.exists())

        input_ll = ""
        row_count = 0
        if case_file.exists():
            with case_file.open(newline="", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader, start=1):
                    row_count += 1
                    input_ll = input_ll or row.get("input_ll", "")
                    resolved, exists = resolve_source(target, row.get("source_file", ""))
                    source_region, project_source_only, header_context = classify_source_region(
                        target, row.get("source_file", ""), resolved, exists
                    )
                    priority, reason, case_kind, validity, review = classify_case(row, source_region, exists)
                    case_uid = f"cclyzerpp.{target}.O2g.{idx:06d}"
                    raw_row_ref = f"{row.get('relation_name', '')}:{row.get('relation_row_number', '')}:{row.get('relation_row_hash', '')}"
                    evidence_files = ";".join(
                        part.strip()
                        for part in row.get("evidence_files", "").split(",")
                        if part.strip()
                    )
                    if raw_artifact_text:
                        evidence_files = ";".join(part for part in [evidence_files, raw_artifact_text] if part)
                    notes = (
                        f"source_exists={int(exists)}; original_priority={row.get('priority', '')}; "
                        f"mapping_status={row.get('mapping_status', '')}; phenomenon={row.get('phenomenon_label', '')}"
                    )
                    cases.append(
                        {
                            "case_uid": case_uid,
                            "target": target,
                            "tool": "cclyzer++",
                            "priority": priority,
                            "priority_reason": reason,
                            "case_kind": case_kind,
                            "status_label": "reported",
                            "run_dir": str(run_dir),
                            "run_id": run_dir.name,
                            "mode": row.get("relation_name", ""),
                            "input_bc": row.get("input_bc", "") or status_row.get("input_bc", ""),
                            "input_ll": row.get("input_ll", ""),
                            "raw_artifact": str(case_file),
                            "raw_row_or_line": raw_row_ref,
                            "reported_file": row.get("source_file", ""),
                            "reported_line": row.get("line", ""),
                            "reported_column": row.get("column", ""),
                            "location_validity": validity,
                            "source_region": source_region,
                            "project_source_only": project_source_only,
                            "header_context": header_context,
                            "ir_function": row.get("demangled_function", "") or row.get("function_id", ""),
                            "ir_instruction": row.get("ir_instruction_id", ""),
                            "ir_line": row.get("debug_line", ""),
                            "ir_snippet": row.get("ir_snippet", ""),
                            "source_snippet": source_context(row),
                            "message": make_message(row),
                            "root_cause_hint": row.get("root_cause_hint", ""),
                            "confidence": row.get("confidence", ""),
                            "needs_manual_review": review,
                            "manual_verdict": row.get("manual_verdict", ""),
                            "evidence_files": evidence_files,
                            "notes": notes,
                        }
                    )
                    priority_counts[priority] += 1
                    reason_counts[reason] += 1
                    region_counts[source_region] += 1
                    mapping_counts[row.get("mapping_status", "")] += 1
                    phenomenon_counts[row.get("phenomenon_label", "")] += 1
                    target_counts[target] += 1

        runs.append(
            {
                "target": target,
                "tool": "cclyzer++",
                "selected": "1",
                "run_dir": str(run_dir),
                "run_id": run_dir.name,
                "universe": status_row.get("universe", "LLVM14-O2-g"),
                "input_bc": status_row.get("input_bc", ""),
                "input_ll": input_ll,
                "mode": "subset",
                "status": status_row.get("status", "missing_value_cases" if not case_file.exists() else "reported"),
                "success_modes": "subset" if status_row.get("status") == "reported" or case_file.exists() else "",
                "failed_modes": "",
                "timeout_modes": "",
                "raw_artifacts": raw_artifact_text,
                "reason": "selected completed cclyzer++ LLVM14-O2-g native-relations run",
                "excluded_reason": "",
                "notes": f"return_code={status_row.get('return_code', '')}; elapsed_sec={status_row.get('elapsed_sec', '')}; value_cases={row_count}; command={command_artifact or ''}",
            }
        )
        stats["selected_runs"].append(str(run_dir))
        if case_file.exists():
            stats["input_case_files"].append(str(case_file))

    stats["case_counts_by_target"] = dict(sorted(target_counts.items()))
    stats["priority_counts"] = dict(priority_counts.most_common())
    stats["priority_reason_counts"] = dict(reason_counts.most_common())
    stats["source_region_counts"] = dict(region_counts.most_common())
    stats["mapping_status_counts"] = dict(mapping_counts.most_common())
    stats["phenomenon_counts"] = dict(phenomenon_counts.most_common())
    return cases, runs, stats


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(counter: Counter | dict[str, int]) -> str:
    items = counter.items() if isinstance(counter, Counter) else counter.items()
    lines = ["| key | count |", "| --- | ---: |"]
    for key, count in items:
        lines.append(f"| `{key}` | {count} |")
    return "\n".join(lines)


def validate_p0(row: dict[str, str], source_cache: dict[str, list[str] | None]) -> str:
    reason = row.get("priority_reason", "")
    reported_file = row.get("reported_file", "")
    path = remap_path(reported_file)
    key = str(path)
    if key not in source_cache:
        if path.exists() and path.is_file():
            source_cache[key] = path.read_text(encoding="utf-8", errors="replace").splitlines()
        else:
            source_cache[key] = None
    lines = source_cache[key]
    line = to_int(row.get("reported_line", ""))
    column = to_int(row.get("reported_column", ""))

    if reason == "LineZero":
        return "ok" if lines is not None and line == 0 else "failed"
    if reason == "LineOutOfRange":
        return "ok" if lines is not None and line is not None and line > len(lines) else "failed"
    if reason == "ColumnOutOfRange":
        if lines is not None and line is not None and column is not None and 1 <= line <= len(lines):
            return "ok" if column > len(lines[line - 1]) else "failed"
        return "failed"
    if reason == "MissingSourceFile":
        return "ok" if lines is None else "failed"
    return "not_checked"


def write_p0_audit(cases: list[dict[str, str]]) -> dict[str, object]:
    p0_rows = [row for row in cases if row["priority"] == "P0"]
    row_reasons = Counter(row["priority_reason"] for row in p0_rows)
    row_targets = Counter(row["target"] for row in p0_rows)
    source_cache: dict[str, list[str] | None] = {}
    unique: dict[tuple[str, str, str, str], dict[str, str]] = {}
    validation = Counter()

    for row in p0_rows:
        key = (
            row.get("reported_file", ""),
            row.get("reported_line", ""),
            row.get("reported_column", ""),
            row.get("priority_reason", ""),
        )
        if key in unique:
            continue
        status = validate_p0(row, source_cache)
        validation[status] += 1
        unique[key] = {
            "target": row.get("target", ""),
            "priority_reason": row.get("priority_reason", ""),
            "reported_file": row.get("reported_file", ""),
            "reported_line": row.get("reported_line", ""),
            "reported_column": row.get("reported_column", ""),
            "location_validity": row.get("location_validity", ""),
            "source_region": row.get("source_region", ""),
            "example_case_uid": row.get("case_uid", ""),
            "example_raw_artifact": row.get("raw_artifact", ""),
            "example_raw_row_or_line": row.get("raw_row_or_line", ""),
            "ir_snippet": row.get("ir_snippet", ""),
            "source_snippet": row.get("source_snippet", ""),
            "validation_status": status,
        }

    unique_fields = [
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
        "ir_snippet",
        "source_snippet",
        "validation_status",
    ]
    write_csv(OUT_DIR / "p0_unique_locations.csv", unique_fields, list(unique.values()))

    unique_reasons = Counter(row["priority_reason"] for row in unique.values())
    unique_targets = Counter(row["target"] for row in unique.values())
    unique_files = {row["reported_file"] for row in unique.values() if row["reported_file"]}

    lines = ["# cclyzer++ P0 Final Audit\n\n"]
    lines.append("## Scope\n")
    lines.append("- tool: `cclyzer++`\n")
    lines.append("- universe: `LLVM14-O2-g` / `O2-g`\n")
    lines.append(f"- source CSV: `{OUT_DIR / 'tool_cases.csv'}`\n")
    lines.append(f"- unique locations CSV: `{OUT_DIR / 'p0_unique_locations.csv'}`\n\n")
    lines.append("## P0 Counts\n")
    lines.append(f"- P0 rows: {len(p0_rows)}\n")
    lines.append(f"- P0 unique locations: {len(unique)}\n")
    lines.append(f"- P0 unique files: {len(unique_files)}\n\n")
    lines.append("## P0 Rows By Reason\n")
    lines.append(markdown_table(row_reasons) + "\n\n")
    lines.append("## P0 Unique Locations By Reason\n")
    lines.append(markdown_table(unique_reasons) + "\n\n")
    lines.append("## P0 Rows By Target\n")
    lines.append(markdown_table(row_targets) + "\n\n")
    lines.append("## P0 Unique Locations By Target\n")
    lines.append(markdown_table(unique_targets) + "\n\n")
    lines.append("## Validation\n")
    lines.append(markdown_table(validation) + "\n\n")
    lines.append("## Interpretation Notes\n")
    lines.append("- P0 rows are relation-level evidence rows, not independent paper cases.\n")
    lines.append("- Unique locations deduplicate by `(reported_file, reported_line, reported_column, priority_reason)`.\n")
    lines.append("- `LineZero` supports no valid source line / source-location loss; only rows with additional nonzero recovered IR line should be phrased as direct line mismatch.\n")
    lines.append("- `ColumnOutOfRange` and `LineOutOfRange` are direct objective line/column invalidity evidence.\n")
    (OUT_DIR / "p0_final_audit.md").write_text("".join(lines), encoding="utf-8")

    return {
        "p0_rows": len(p0_rows),
        "p0_unique_locations": len(unique),
        "p0_unique_files": len(unique_files),
        "p0_rows_by_reason": dict(row_reasons),
        "p0_unique_by_reason": dict(unique_reasons),
        "p0_validation": dict(validation),
    }


def write_reports(cases: list[dict[str, str]], runs: list[dict[str, str]], stats: dict[str, object]) -> None:
    priority = Counter(row["priority"] for row in cases)
    reasons = Counter(row["priority_reason"] for row in cases)
    targets: dict[str, Counter] = defaultdict(Counter)
    regions: dict[str, Counter] = defaultdict(Counter)
    phenomena: dict[str, Counter] = defaultdict(Counter)
    project_only: dict[str, Counter] = defaultdict(Counter)
    validity = Counter(row["location_validity"] for row in cases)
    for row in cases:
        targets[row["target"]][row["priority"]] += 1
        regions[row["target"]][row["source_region"]] += 1
        phenomena[row["target"]][row["message"].split(";", 1)[0]] += 1
        if row["project_source_only"] == "1":
            project_only[row["target"]][row["priority"]] += 1

    target_lines = [
        "| target | cases | P0 | P1 | P2 | source regions | top phenomena |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for target in sorted(targets):
        total = sum(targets[target].values())
        region_text = ", ".join(f"{k}={v}" for k, v in regions[target].most_common())
        phen_text = ", ".join(f"{k}={v}" for k, v in phenomena[target].most_common(5))
        target_lines.append(
            f"| {target} | {total} | {targets[target]['P0']} | {targets[target]['P1']} | {targets[target]['P2']} | {region_text} | {phen_text} |"
        )

    project_lines = [
        "| target | project-source cases | P0 | P1 | P2 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for target in sorted(targets):
        total = sum(project_only[target].values())
        project_lines.append(
            f"| {target} | {total} | {project_only[target]['P0']} | {project_only[target]['P1']} | {project_only[target]['P2']} |"
        )
    p0_audit = write_p0_audit(cases)
    target_text = ", ".join(f"`{target}`" for target in SELECTED_RUNS)

    report = f"""# cclyzer++ O2-g Useful Case 收集报告

## 范围

- tool: `cclyzer++`
- universe: `LLVM14-O2-g`
- 纳入的 targets: {target_text}
- 数据来源: 每个 run 的原生 `relations/*.csv.gz`，经 `CompilerOptimization/Tools/cclyzerpp/analyze_native_value_cases.py` 生成 `ValueCases/all_cases.csv` 后统一标准化
- 明确未使用: `extract/candidates.tsv`、`extract/relation_counts.tsv` 等不完整 extract 摘要
- 重新分类依据: `CompilerOptimization/Result/AllUsefulCases/useful_cases_matrix_plan.md`
- 参考分析方案: `CompilerOptimization/Tools/cclyzerpp/AnalysisResult/cclyzerpp_native_output_case_analysis_plan.md`

## 优先级统计

{markdown_table(priority)}

## 优先级原因

{markdown_table(reasons)}

## Target 汇总

{chr(10).join(target_lines)}

## 仅项目源码统计

{chr(10).join(project_lines)}

## 位置有效性

{markdown_table(validity)}

## P0 最终审核

- P0 rows: `{p0_audit['p0_rows']}`
- P0 unique locations: `{p0_audit['p0_unique_locations']}`
- P0 unique files: `{p0_audit['p0_unique_files']}`
- 详细审核文件: `p0_final_audit.md`
- unique location 明细: `p0_unique_locations.csv`

## 纳入的 Runs

""" + "\n".join(f"- `{row['target']}`: `{row['run_dir']}`" for row in runs) + """

## 说明

- 没有删除或修改 cclyzer++ 原始 `relations/`、`log/`、`status/`、`commands/` artifact。
- 新增 lepton/masscan/zfp 的 `ValueCases/` 是从原生 `relations/` 重建的分析输出；总表没有读取 `extract/`。
- `P0` 当前只限于 project source/header 中的客观无效位置：`LineZero`、`LineOutOfRange`、`ColumnOutOfRange`，以及明确缺失的项目文件。
- `SourceIRMismatch` 对 project code 归为 `P1`，因为它是 semantic/source-IR consistency candidate，不等同于工具原生 report 中可直接比对文本的 `SourceTextMismatch`。
- `NoDebugLoc` 对 project code 归为 `P1`，对 external/unresolved code 归为 `P2`；除非它同时具备具体的 project line/column invalidity，否则不升为 P0。
- 空 source file、system header、third-party header 和 unknown remap cases 会保留，但除非存在项目本地的客观无效证据，否则降为 `P2`。
- Header rows 会保留并通过 `source_region` 和 `header_context` 标注；仅仅因为位置在 header 中，不作为 P0 原因。
- 完整表保留 system/header/third-party cases 以便审计；论文正文统计 project-source 时应使用 `project_source_only=1`。

## 输出文件

- `tool_cases.csv`
- `tool_runs.csv`
- `native_output_profile.md`
- `collection_manifest.json`
- `scripts/collect_cclyzerpp_o2g_cases.py`
"""
    (OUT_DIR / "case_collection_report.md").write_text(report, encoding="utf-8")

    profile = f"""# cclyzer++ 原生输出 Profile

cclyzer++ 不输出 source-level bug report。它的原生输出是每个 run 的 `relations/*.csv.gz` 中的一组 Datalog relation facts。此次纳入的 run 都使用这些 raw relations 生成或复用 `ValueCases/`：relation inventory、IR/debug indexes、fact-to-source maps、classification TSVs、casebook entries，以及 `ValueCases/all_cases.csv`。

本 collector 不读取 `extract/` 摘要。它读取已完成的 `ValueCases/all_cases.csv` 文件，并保留指向 raw relation row 的证据字段：`relation_name`、`relation_row_number`、`relation_row_hash`，以及 IR snippet、source snippet、输入 `.bc`、生成的 `.ll`、`relations/` 和原始 evidence files。

从原生 case 分析中保留的主要 phenomenon labels：

{markdown_table(Counter(row['message'].split(';', 1)[0] for row in cases))}

输入 ValueCases 中观察到的 mapping statuses：

{markdown_table(Counter(note.split('mapping_status=', 1)[1].split(';', 1)[0] for note in (row['notes'] for row in cases)))}
"""
    (OUT_DIR / "native_output_profile.md").write_text(profile, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cases, runs, stats = collect_cases()
    write_csv(OUT_DIR / "tool_cases.csv", CASE_FIELDS, cases)
    write_csv(OUT_DIR / "tool_runs.csv", RUN_FIELDS, runs)
    (OUT_DIR / "collection_manifest.json").write_text(json.dumps(stats, indent=2, sort_keys=True), encoding="utf-8")
    write_reports(cases, runs, stats)
    print(f"wrote {len(cases)} cases and {len(runs)} runs to {OUT_DIR}")


if __name__ == "__main__":
    main()
