#!/usr/bin/env python3
"""Standardize yapall LLVM14-O2-g ValueCases for the useful-cases matrix."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


WORK_ROOT = Path("/home/jimi/PaperExperiment")
RESULT_ROOT = WORK_ROOT / "CompilerOptimization" / "Result"
TARGET_ROOT = WORK_ROOT / "CompilerOptimization" / "Target"
OUT_DIR = RESULT_ROOT / "AllUsefulCases" / "yapall" / "O2-g"
RUN_LIST = OUT_DIR.parent / "result.txt"

SELECTED_TARGETS = {"zopfli", "tengine", "masscan", "libsndfile", "lepton"}

TARGET_SOURCE_ROOTS = {
    "zopfli": TARGET_ROOT / "zopfli",
    "libsndfile": TARGET_ROOT / "libsndfile",
    "masscan": TARGET_ROOT / "masscan",
    "tengine": TARGET_ROOT / "Tengine",
    "lepton": TARGET_ROOT / "lepton",
    "zfp": TARGET_ROOT / "zfp",
}

TOOL_CASE_FIELDS = [
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

TOOL_RUN_FIELDS = [
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

WEAK_EVIDENCE_FIELDS = [
    "target",
    "run_dir",
    "classification",
    "mapping_status",
    "source_region",
    "rows",
    "reason",
]

HEADER_SUFFIXES = {
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".inc",
    ".ipp",
    ".tcc",
}

THIRD_PARTY_MARKERS = {
    "third_party",
    "third-party",
    "3rdparty",
    "3rd-party",
    "vendor",
    "vendors",
    "external",
    "extern",
    "deps",
    "dependency",
    "dependencies",
    "submodules",
}


class SourceCache:
    def __init__(self) -> None:
        self._cache: Dict[str, Optional[List[str]]] = {}
        self._region_cache: Dict[Tuple[str, str], Tuple[str, str, str]] = {}
        self._location_cache: Dict[Tuple[str, str, str, str, bool], Tuple[str, str, str, str]] = {}

    def lines(self, path: str) -> Optional[List[str]]:
        if not path:
            return None
        if path not in self._cache:
            p = Path(path)
            if not p.exists() or not p.is_file():
                self._cache[path] = None
            else:
                self._cache[path] = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return self._cache[path]

    def region(self, target: str, source_file: str) -> Tuple[str, str, str]:
        key = (target, source_file)
        if key not in self._region_cache:
            self._region_cache[key] = classify_source_region(target, source_file)
        return self._region_cache[key]

    def cached_location(self, key: Tuple[str, str, str, str, bool]) -> Optional[Tuple[str, str, str, str]]:
        return self._location_cache.get(key)

    def set_location(self, key: Tuple[str, str, str, str, bool], value: Tuple[str, str, str, str]) -> Tuple[str, str, str, str]:
        self._location_cache[key] = value
        return value


def rel_to(path: Path, root: Path) -> Optional[Path]:
    try:
        return path.resolve().relative_to(root.resolve())
    except (ValueError, FileNotFoundError, RuntimeError):
        return None


def target_from_run_dir(run_dir: Path) -> str:
    parts = run_dir.resolve().parts
    try:
        idx = parts.index("Result")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return ""


def is_header(path: str) -> bool:
    return Path(path).suffix.lower() in HEADER_SUFFIXES


def classify_source_region(target: str, source_file: str) -> Tuple[str, str, str]:
    if not source_file:
        return "llvm_ir_only", "0", "unknown"

    p = Path(source_file)
    suffix_header = is_header(source_file)
    header_context = "project_header" if suffix_header else "not_header"

    path_text = source_file
    if path_text.startswith(("/usr/include/", "/usr/lib/", "/usr/local/include/", "/opt/")):
        return "system_header" if suffix_header else "system_source", "0", "system_header" if suffix_header else "not_header"

    if "/CompilerOptimization/CompilerResult/" in path_text or "/build/" in path_text or "/cmake-build" in path_text:
        return "generated_source", "0", "unknown" if suffix_header else "not_header"

    root = TARGET_SOURCE_ROOTS.get(target, TARGET_ROOT / target)
    rel = rel_to(p, root)
    if rel is not None:
        parts = {part.lower() for part in rel.parts}
        if parts & THIRD_PARTY_MARKERS:
            return (
                "third_party_header" if suffix_header else "third_party_source",
                "0",
                "third_party_header" if suffix_header else "not_header",
            )
        return "project_header" if suffix_header else "project_source", "1", header_context

    if "include/c++" in path_text or "/llvm-" in path_text:
        return "system_header" if suffix_header else "system_source", "0", "system_header" if suffix_header else "not_header"

    return "unknown", "0", "unknown" if suffix_header else "not_header"


def parse_int(text: str) -> Optional[int]:
    try:
        return int(str(text))
    except (TypeError, ValueError):
        return None


def concrete_site(row: dict) -> bool:
    if row.get("site_resolution") in {"tool_output_insufficient", "unlocatable_operand"}:
        return False
    if row.get("site_role") == "allocation_only":
        return False
    return bool(row.get("site_inst_name") or row.get("ir_text"))


def non_code_status(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return "empty_or_comment_line"
    if stripped.startswith(("//", "/*", "*/")):
        return "empty_or_comment_line"
    if stripped.startswith("#"):
        return "preprocessor_only"
    return ""


def location_validity(row: dict, source_cache: SourceCache) -> Tuple[str, str, str, str]:
    target = row.get("target", "")
    source_file = row.get("source_file", "")
    source_line = row.get("source_line", "")
    source_column = row.get("source_column", "")
    has_concrete_site = concrete_site(row)
    cache_key = (target, source_file, source_line, source_column, has_concrete_site)
    cached = source_cache.cached_location(cache_key)
    if cached:
        return cached

    source_region, project_source_only, header_context = source_cache.region(target, source_file)

    if not source_file:
        if row.get("mapping_status") == "missing_debug_location":
            return source_cache.set_location(cache_key, ("no_debug_loc", source_region, project_source_only, header_context))
        return source_cache.set_location(cache_key, ("unknown", source_region, project_source_only, header_context))

    lines = source_cache.lines(source_file)
    if lines is None:
        return source_cache.set_location(cache_key, ("missing_file", source_region, project_source_only, header_context))

    line_no = parse_int(source_line)
    if line_no == 0:
        return source_cache.set_location(cache_key, ("line_zero", source_region, project_source_only, header_context))
    if line_no is None or line_no < 0:
        return source_cache.set_location(cache_key, ("unknown", source_region, project_source_only, header_context))
    if line_no > len(lines):
        return source_cache.set_location(cache_key, ("line_out_of_range", source_region, project_source_only, header_context))
    if line_no < 1:
        return source_cache.set_location(cache_key, ("unknown", source_region, project_source_only, header_context))

    text = lines[line_no - 1]
    col_no = parse_int(source_column)
    if col_no is not None and col_no > 0 and col_no > len(text):
        return source_cache.set_location(cache_key, ("column_out_of_range", source_region, project_source_only, header_context))

    if has_concrete_site:
        nc = non_code_status(text)
        if nc:
            return source_cache.set_location(cache_key, (nc, source_region, project_source_only, header_context))

    return source_cache.set_location(cache_key, ("valid", source_region, project_source_only, header_context))


def class_set(row: dict) -> set:
    classes = set()
    if row.get("classification"):
        classes.add(row["classification"])
    for item in row.get("all_matching_classes", "").split(";"):
        if item:
            classes.add(item)
    return classes


def priority_for(row: dict, loc_validity: str, source_region: str) -> Tuple[str, str, str, str, str]:
    project_region = source_region in {"project_source", "project_header"}
    classes = class_set(row)

    if project_region:
        if loc_validity == "line_zero":
            return "P0", "LineZero", "LocationInvalid", "high", "0"
        if loc_validity == "line_out_of_range":
            return "P0", "LineOutOfRange", "LocationInvalid", "high", "0"
        if loc_validity == "column_out_of_range":
            return "P0", "ColumnOutOfRange", "LocationInvalid", "high", "0"
        if loc_validity == "missing_file":
            return "P0", "MissingSourceFile", "LocationInvalid", "high", "0"
        if loc_validity in {"empty_or_comment_line", "preprocessor_only"}:
            return "P0", "SourceLineEmptyOrNonCode", "LocationInvalid", "high", "0"

    if loc_validity == "no_debug_loc" and concrete_site(row):
        return "P1", "NoDebugLoc", "NoDebugLoc", "medium", "1"

    if project_region:
        if "InlineAttributionDrift" in classes:
            return "P1", "InlineAttributionDrift", "LocationDrift", "medium", "1"
        if "WrongFunctionAttribution" in classes:
            return "P1", "WrongFunctionAttribution", "LocationDrift", "medium", "1"
        if "ColumnPointsToWrongToken" in classes:
            return "P1", "ColumnPointsToWrongToken", "WarningKindMismatch", "medium", "1"
        if "Wanted-CodeMismatch" in classes:
            return "P1", "SourceIRSemanticMismatch", "IRSourceMismatch", "medium", "1"
        if "Wanted-LineColumnMissing" in classes:
            return "P1", "SourceLocationWeakOrMissing", "LocationDrift", "medium", "1"

    if "tool_output_insufficient" in classes or row.get("site_resolution") == "tool_output_insufficient":
        return "P2", "ToolOutputInsufficient", "RunOrLocationWeakEvidence", "low", "1"
    if "unlocatable_operand" in classes or row.get("site_resolution") == "unlocatable_operand":
        return "P2", "UnlocatableOperand", "RunOrLocationWeakEvidence", "low", "1"
    if loc_validity == "missing_file":
        return "P2", "ExternalOrUnresolvedMissingFile", "RunOrLocationWeakEvidence", "low", "1"
    if loc_validity == "no_debug_loc":
        return "P2", "NoDebugLocWeak", "NoDebugLoc", "low", "1"
    if classes & {"InlineAttributionDrift", "WrongFunctionAttribution", "ColumnPointsToWrongToken", "Wanted-CodeMismatch", "Wanted-LineColumnMissing"}:
        return "P2", "ExternalOrUnresolvedCandidate", "RunOrLocationWeakEvidence", "low", "1"

    return "P2", "LowConfidenceRawIssue", "RunOrLocationWeakEvidence", "low", "1"


def should_exclude(row: dict) -> Tuple[bool, str]:
    classes = class_set(row)
    if row.get("classification") == "Useless-CodeConsistent" and classes <= {"Useless-CodeConsistent"}:
        return True, "Useless-CodeConsistent"
    return False, ""


def raw_row_or_line(row: dict) -> str:
    parts = []
    if row.get("raw_log_line_no"):
        parts.append(f"line={row['raw_log_line_no']}")
    if row.get("kind"):
        parts.append(f"kind={row['kind']}")
    if row.get("operand"):
        parts.append(f"operand={row['operand']}")
    if row.get("allocation"):
        parts.append(f"allocation={row['allocation']}")
    return "; ".join(parts)


def evidence_files(row: dict) -> str:
    files = [
        row.get("raw_log_path", ""),
        str(Path(row.get("run_dir", "")) / "commands" / "commands.log") if row.get("run_dir") else "",
        str(Path(row.get("run_dir", "")) / "status" / "run_status.tsv") if row.get("run_dir") else "",
        str(Path(row.get("run_dir", "")) / "report" / "final_report.md") if row.get("run_dir") else "",
        str(Path(row.get("run_dir", "")) / "ValueCases" / "summary.md") if row.get("run_dir") else "",
    ]
    return ";".join(dict.fromkeys(f for f in files if f))


def standardized_case(row: dict, ordinal: int, source_cache: SourceCache) -> Optional[dict]:
    excluded, _ = should_exclude(row)
    if excluded:
        return None

    loc_valid, source_region, project_source_only, header_context = location_validity(row, source_cache)
    priority, reason, case_kind, fallback_conf, fallback_review = priority_for(row, loc_valid, source_region)
    target = row.get("target", "")
    mode = f"{row.get('scan_mode','')}:k{row.get('contexts','')}:{row.get('check','')}"
    message = (
        f"{row.get('kind','')} issue; site_resolution={row.get('site_resolution','')}; "
        f"classification={row.get('classification','')}; all_classes={row.get('all_matching_classes','')}"
    )
    confidence = fallback_conf if priority == "P0" else (row.get("confidence", "") or fallback_conf)
    needs_manual_review = fallback_review if priority == "P0" else (row.get("needs_manual_review", "") or fallback_review)
    notes = [
        f"candidate_id={row.get('candidate_id','')}",
        f"issue_id={row.get('issue_id','')}",
        f"mapping_status={row.get('mapping_status','')}",
        f"token_at_column={row.get('token_at_column','')}",
        f"expected_token_kind={row.get('expected_token_kind','')}",
        f"actual_token_kind={row.get('actual_token_kind','')}",
        f"site_role={row.get('site_role','')}",
        f"ll_source={row.get('ll_source','')}",
    ]
    if row.get("notes"):
        notes.append(f"valuecase_notes={row.get('notes')}")

    return {
        "case_uid": f"yapall.{target}.O2g.{ordinal:09d}",
        "target": target,
        "tool": "yapall",
        "priority": priority,
        "priority_reason": reason,
        "case_kind": case_kind,
        "status_label": row.get("status", "reported") or "reported",
        "run_dir": row.get("run_dir", ""),
        "run_id": row.get("run_id", ""),
        "mode": mode,
        "input_bc": row.get("input_bc", ""),
        "input_ll": row.get("input_ll", ""),
        "raw_artifact": row.get("raw_log_path", ""),
        "raw_row_or_line": raw_row_or_line(row),
        "reported_file": row.get("source_file", ""),
        "reported_line": row.get("source_line", ""),
        "reported_column": row.get("source_column", ""),
        "location_validity": loc_valid,
        "source_region": source_region,
        "project_source_only": project_source_only,
        "header_context": header_context,
        "ir_function": row.get("ir_function", ""),
        "ir_instruction": row.get("site_inst_name", ""),
        "ir_line": row.get("ir_instruction_index", ""),
        "ir_snippet": row.get("ir_text", ""),
        "source_snippet": row.get("source_text", ""),
        "message": message,
        "root_cause_hint": row.get("root_cause_hint", "") or "DWARF location drift",
        "confidence": confidence,
        "needs_manual_review": needs_manual_review,
        "manual_verdict": "",
        "evidence_files": evidence_files(row),
        "notes": "; ".join(notes),
    }


def read_allowed_run_dirs() -> List[Path]:
    """Read the user-approved yapall run directories from result.txt."""
    if not RUN_LIST.exists():
        raise FileNotFoundError(f"missing run selection file: {RUN_LIST}")

    out = []
    seen = set()
    for raw_line in RUN_LIST.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line.startswith("/"):
            continue
        path = Path(line.rstrip("/")).resolve()
        if path not in seen:
            out.append(path)
            seen.add(path)

    if not out:
        raise RuntimeError(f"no absolute run directories found in {RUN_LIST}")
    return out


def find_valuecase_csvs(allowed_run_dirs: Iterable[Path]) -> List[Path]:
    out = []
    for run_dir in allowed_run_dirs:
        out.extend(sorted((run_dir / "ValueCases").glob("*_yapall_value_cases.csv")))
    return out


def discover_runs(allowed_run_dirs: Iterable[Path]) -> List[Path]:
    return list(allowed_run_dirs)


def read_csv_rows(path: Path, delimiter: str = ",") -> List[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8", errors="replace") as fh:
        return list(csv.DictReader(fh, delimiter=delimiter))


def read_first_csv_row(path: Path, delimiter: str = ",") -> dict:
    rows = read_csv_rows(path, delimiter)
    return rows[0] if rows else {}


def mode_from_status_row(row: dict) -> str:
    if not row:
        return ""
    return f"{row.get('mode','')}:k{row.get('contexts','')}:{row.get('check','')}"


def summarize_status(status_rows: List[dict]) -> Tuple[str, str, str, str, str]:
    modes = []
    success_modes = []
    failed_modes = []
    timeout_modes = []
    statuses = []

    for row in status_rows:
        mode = mode_from_status_row(row)
        status = row.get("status", "")
        if mode:
            modes.append(mode)
        if status:
            statuses.append(status)
        if status in {"reported", "verified/no-error"}:
            success_modes.append(mode)
        elif status == "timeout":
            timeout_modes.append(mode)
        elif status:
            failed_modes.append(mode)

    if not statuses:
        status = ""
    elif len(set(statuses)) == 1:
        status = statuses[0]
    elif success_modes and (failed_modes or timeout_modes):
        status = "partial"
    else:
        status = ";".join(dict.fromkeys(statuses))

    return (
        ";".join(dict.fromkeys(modes)),
        status,
        ";".join(m for m in dict.fromkeys(success_modes) if m),
        ";".join(m for m in dict.fromkeys(failed_modes) if m),
        ";".join(m for m in dict.fromkeys(timeout_modes) if m),
    )


def raw_artifacts_for_run(run_dir: Path, status_rows: List[dict], value_csv: Optional[Path]) -> str:
    files = []
    for row in status_rows:
        files.extend([row.get("log_path", ""), row.get("issues_path", "")])
    files.extend(
        [
            str(value_csv) if value_csv else "",
            str(run_dir / "status" / "run_status.tsv"),
            str(run_dir / "commands" / "commands.log"),
            str(run_dir / "report" / "final_report.md"),
            str(run_dir / "ValueCases" / "summary.md") if value_csv else "",
        ]
    )
    return ";".join(dict.fromkeys(f for f in files if f and Path(f).exists()))


def tool_run_row(run_dir: Path, selected_csvs: Dict[Path, Path]) -> dict:
    status_rows = read_csv_rows(run_dir / "status" / "run_status.tsv", delimiter="\t")
    status_row = status_rows[0] if status_rows else {}
    target = target_from_run_dir(run_dir)
    value_csv = selected_csvs.get(run_dir)
    value_row = read_first_csv_row(value_csv) if value_csv else {}
    mode, status, success_modes, failed_modes, timeout_modes = summarize_status(status_rows)
    input_bcs = [row.get("input_bc", "") for row in status_rows if row.get("input_bc", "")]
    if not value_csv:
        excluded_reason = "no_valuecases_csv_in_allowed_run"
    return {
        "target": target,
        "tool": "yapall",
        "selected": "1",
        "run_dir": str(run_dir),
        "run_id": run_dir.name,
        "universe": status_row.get("compiler_universe", "LLVM14-O2-g") or "LLVM14-O2-g",
        "input_bc": ";".join(dict.fromkeys(input_bcs)) or value_row.get("input_bc", ""),
        "input_ll": value_row.get("input_ll", ""),
        "mode": mode or f"{value_row.get('scan_mode','')}:k{value_row.get('contexts','')}:{value_row.get('check','')}",
        "status": status or value_row.get("status", ""),
        "success_modes": success_modes,
        "failed_modes": failed_modes,
        "timeout_modes": timeout_modes,
        "raw_artifacts": raw_artifacts_for_run(run_dir, status_rows, value_csv),
        "reason": "allowed run listed in result.txt",
        "excluded_reason": excluded_reason if not value_csv else "",
        "notes": "cases standardized from existing ValueCases; yapall was not rerun" if value_csv else "allowed native run has no ValueCases analysis directory; retained as run-level evidence only",
    }


def write_csv(path: Path, fields: List[str], rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})
            count += 1
    return count


def format_counter(counter: Counter) -> str:
    if not counter:
        return "- none\n"
    return "".join(f"- {key}: {value}\n" for key, value in counter.most_common())


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    allowed_run_dirs = read_allowed_run_dirs()
    allowed_targets = sorted({target_from_run_dir(path) for path in allowed_run_dirs})
    value_csvs = find_valuecase_csvs(allowed_run_dirs)
    selected_by_run = {p.parents[1]: p for p in value_csvs}
    source_cache = SourceCache()

    stats = {
        "raw_rows": 0,
        "included_rows": 0,
        "excluded_rows": 0,
    }
    by_priority: Counter = Counter()
    by_target_priority: Dict[str, Counter] = defaultdict(Counter)
    by_reason: Counter = Counter()
    by_target_reason: Dict[str, Counter] = defaultdict(Counter)
    by_case_kind: Counter = Counter()
    by_location_validity: Counter = Counter()
    by_source_region: Counter = Counter()
    by_classification: Counter = Counter()
    weak_evidence: Counter = Counter()
    excluded_reasons: Counter = Counter()
    target_raw_rows: Counter = Counter()

    cases_path = OUT_DIR / "tool_cases.csv"
    ordinal = 0
    with cases_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=TOOL_CASE_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for value_csv in value_csvs:
            with value_csv.open(newline="", encoding="utf-8", errors="replace") as in_fh:
                for row in csv.DictReader(in_fh):
                    stats["raw_rows"] += 1
                    target_raw_rows[row.get("target", "")] += 1
                    by_classification[row.get("classification", "")] += 1
                    _, source_region, _, _ = location_validity(row, source_cache)
                    weak_evidence[
                        (
                            row.get("target", ""),
                            row.get("run_dir", ""),
                            row.get("classification", ""),
                            row.get("mapping_status", ""),
                            source_region,
                        )
                    ] += 1
                    excluded, excluded_reason = should_exclude(row)
                    if excluded:
                        stats["excluded_rows"] += 1
                        excluded_reasons[excluded_reason] += 1
                        continue
                    ordinal += 1
                    case = standardized_case(row, ordinal, source_cache)
                    if not case:
                        continue
                    writer.writerow(case)
                    stats["included_rows"] += 1
                    by_priority[case["priority"]] += 1
                    by_target_priority[case["target"]][case["priority"]] += 1
                    by_reason[case["priority_reason"]] += 1
                    by_target_reason[case["target"]][case["priority_reason"]] += 1
                    by_case_kind[case["case_kind"]] += 1
                    by_location_validity[case["location_validity"]] += 1
                    by_source_region[case["source_region"]] += 1

    run_rows = [tool_run_row(run_dir, selected_by_run) for run_dir in discover_runs(allowed_run_dirs)]
    write_csv(OUT_DIR / "tool_runs.csv", TOOL_RUN_FIELDS, run_rows)
    weak_rows = (
        {
            "target": target,
            "run_dir": run_dir,
            "classification": classification,
            "mapping_status": mapping_status,
            "source_region": source_region,
            "rows": rows,
            "reason": "summarized raw ValueCases rows from result.txt-allowed runs only",
        }
        for (target, run_dir, classification, mapping_status, source_region), rows in sorted(weak_evidence.items())
    )
    write_csv(OUT_DIR / "weak_evidence_summary.csv", WEAK_EVIDENCE_FIELDS, weak_rows)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "yapall",
        "universe": "LLVM14-O2-g",
        "run_selection_file": str(RUN_LIST),
        "allowed_run_dirs": [str(p) for p in allowed_run_dirs],
        "selected_targets": allowed_targets,
        "selected_valuecase_csvs": [str(p) for p in value_csvs],
        "allowed_runs_without_valuecases": [str(p) for p in allowed_run_dirs if p not in selected_by_run],
        "output_dir": str(OUT_DIR),
        "stats": stats,
        "priority_counts": dict(by_priority),
        "reason_counts": dict(by_reason),
        "case_kind_counts": dict(by_case_kind),
        "location_validity_counts": dict(by_location_validity),
        "source_region_counts": dict(by_source_region),
        "classification_counts": dict(by_classification),
        "excluded_counts": dict(excluded_reasons),
        "target_raw_rows": dict(target_raw_rows),
        "target_priority_counts": {k: dict(v) for k, v in by_target_priority.items()},
        "target_reason_counts": {k: dict(v) for k, v in by_target_reason.items()},
        "notes": [
            "Existing yapall ValueCases were read; yapall analyzer was not rerun.",
            "All native run-level evidence is restricted to run directories listed in result.txt.",
            "Case-level ValueCases analysis is restricted to ValueCases CSVs found under result.txt-listed run directories.",
            "Useless-CodeConsistent rows with no other candidate class were excluded from tool_cases.csv.",
            "P0 is limited to objective project source/header invalid-location evidence.",
        ],
    }
    (OUT_DIR / "collection_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    report = []
    report.append("# yapall O2-g Case Collection Report\n\n")
    report.append("## Scope\n")
    report.append("- tool: yapall\n")
    report.append("- universe: LLVM14-O2-g / O2-g only\n")
    report.append("- run selection file: " + str(RUN_LIST) + "\n")
    report.append("- selected targets: " + ", ".join(allowed_targets) + "\n")
    report.append("- selected run directories: " + str(len(allowed_run_dirs)) + "\n")
    report.append("- analyzer rerun: no; collected from existing ValueCases\n")
    report.append("- output directory: " + str(OUT_DIR) + "\n\n")
    report.append("## Allowed Run Directories\n")
    for path in allowed_run_dirs:
        suffix = " (no ValueCases analysis directory; run-level evidence only)" if path not in selected_by_run else ""
        report.append(f"- {path}{suffix}\n")
    report.append("\n")
    report.append("## Row Counts\n")
    report.append(f"- raw ValueCases rows read: {stats['raw_rows']}\n")
    report.append(f"- included tool_cases rows: {stats['included_rows']}\n")
    report.append(f"- excluded rows: {stats['excluded_rows']}\n\n")
    report.append("## Priority Counts\n")
    report.append(format_counter(by_priority))
    report.append("\n## Priority Reasons\n")
    report.append(format_counter(by_reason))
    report.append("\n## Location Validity\n")
    report.append(format_counter(by_location_validity))
    report.append("\n## Source Regions\n")
    report.append(format_counter(by_source_region))
    report.append("\n## Per-target Priority Counts\n")
    for target in sorted(by_target_priority):
        counts = by_target_priority[target]
        report.append(f"- {target}: P0={counts.get('P0',0)}, P1={counts.get('P1',0)}, P2={counts.get('P2',0)}\n")
    report.append("\n## Excluded Rows\n")
    report.append(format_counter(excluded_reasons))
    report.append("\n## Selected ValueCases Inputs\n")
    for path in value_csvs:
        report.append(f"- {path}\n")
    missing_valuecases = [path for path in allowed_run_dirs if path not in selected_by_run]
    if missing_valuecases:
        report.append("\n## Allowed Runs Without ValueCases\n")
        for path in missing_valuecases:
            report.append(f"- {path}\n")
    report.append("\n## Interpretation Notes\n")
    report.append("- No auxiliary discovered runs are included; all run-level and case-level evidence is restricted to result.txt.\n")
    report.append("- P0 rows are objective invalid source-location evidence, not independent paper case counts.\n")
    report.append("- P1 rows are strong candidates that still need semantic/manual inspection.\n")
    report.append("- P2 rows are weak, external, unresolved, or output-insufficient evidence retained for appendix-scale context.\n")
    (OUT_DIR / "case_collection_report.md").write_text("".join(report), encoding="utf-8")

    profile = []
    profile.append("# yapall Native Output Profile\n\n")
    profile.append("## Run Selection Boundary\n")
    profile.append(f"- run selection file: {RUN_LIST}\n")
    profile.append("- only the run directories listed there are included in this profile and downstream CSVs\n\n")
    profile.append("## Native Inputs Used\n")
    profile.append("- ValueCases/*_yapall_value_cases.csv\n")
    profile.append("- ValueCases/raw_issues.csv and raw log paths referenced by each row\n")
    profile.append("- ValueCases/ll_provenance.csv via columns copied into each row\n")
    profile.append("- report/final_report.md, commands/commands.log, status/run_status.tsv as run evidence\n\n")
    profile.append("## Native Classification Counts\n")
    profile.append(format_counter(by_classification))
    profile.append("\n## Normalization Policy\n")
    profile.append("- Raw yapall issue rows are IR-level pointer-analysis reports, not source-level confirmed vulnerabilities.\n")
    profile.append("- Source file/line/column validity is recomputed against local source files when available.\n")
    profile.append("- Header locations are not automatically P0; they require objective invalidity.\n")
    profile.append("- Tool-output-insufficient rows are retained as P2 unless an objective project location invalidity is present.\n")
    (OUT_DIR / "native_output_profile.md").write_text("".join(profile), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
