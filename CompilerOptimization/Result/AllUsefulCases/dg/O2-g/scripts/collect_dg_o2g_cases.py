#!/usr/bin/env python3
"""Collect useful DG O2-g cases from selected high_precision runs.

The collector follows
CompilerOptimization/Result/AllUsefulCases/useful_cases_matrix_plan.md.

DG's high_precision runs already preserve native output and normalized summaries:

* summary/line_hits.csv: per-line reports recovered from native --c-lines stdout.
* summary/warnings.csv: native stderr warnings, often unsupported/precision-loss IR.
* summary/failures.csv: timeout/failure/unsupported-mode run evidence.
* summary/steps.csv, report.md, commands.log: run manifest and exact commands.

This script keeps every reported row. For line-hit rows with multiple source
candidate files, it emits one standardized case per candidate so each row maps
to a single source file whenever possible.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


csv.field_size_limit(sys.maxsize)

ROOT = Path("/home/jimi/PaperExperiment")
RESULT_TXT = ROOT / "CompilerOptimization/Result/AllUsefulCases/dg/result.txt"
OUT_DIR = ROOT / "CompilerOptimization/Result/AllUsefulCases/dg/O2-g"
TARGET_ROOT = ROOT / "CompilerOptimization/Target"

TARGET_ALIASES = {
    "tengine": "Tengine",
}

SOURCE_LINE_CACHE: dict[str, tuple[list[str] | None, str]] = {}
LOCATION_CACHE: dict[tuple[str, str, int, int, bool], dict[str, str]] = {}

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
    for raw_line in RESULT_TXT.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        if line.startswith("/"):
            if not current:
                raise ValueError(f"run path without target header: {line}")
            runs.append((current, Path(line)))
    return runs


def read_csv(path: Path) -> Iterable[tuple[int, dict[str, str]]]:
    if not path.exists():
        return
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row_no, row in enumerate(reader, start=2):
            yield row_no, row


def parse_int(text: object, default: int = 0) -> int:
    try:
        return int(str(text).strip())
    except (TypeError, ValueError):
        return default


def target_source_root(target: str) -> Path:
    return TARGET_ROOT / TARGET_ALIASES.get(target, target)


def remap_container_path(path_text: str) -> str:
    if path_text.startswith("/work/PaperExperiment/"):
        return str(ROOT / path_text[len("/work/PaperExperiment/") :])
    if path_text.startswith("/work/"):
        return str(ROOT / path_text[len("/work/") :])
    return path_text


def path_exists_maybe(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False


def source_candidates(target: str, reported_file: str) -> list[Path]:
    raw = remap_container_path(reported_file.strip())
    root = target_source_root(target)
    if not raw:
        return []

    candidates: list[Path] = []
    path = Path(raw)

    if path.is_absolute():
        candidates.append(path)
        marker = "/home/jimi/PaperExperiment/"
        if raw.startswith(marker):
            candidates.append(ROOT / raw[len(marker) :])
    if raw.startswith("CompilerOptimization/"):
        candidates.append(ROOT / raw)
    if raw.startswith("Target/"):
        candidates.append(ROOT / "CompilerOptimization" / raw)
        after = raw[len("Target/") :]
        parts = Path(after).parts
        if parts:
            candidates.append(TARGET_ROOT / Path(*parts))
            if parts[0].lower() == target.lower() or parts[0] == TARGET_ALIASES.get(target, ""):
                candidates.append(root / Path(*parts[1:]))

    markers = [
        f"/CompilerOptimization/Target/{target}/",
        f"/CompilerOptimization/Target/{TARGET_ALIASES.get(target, target)}/",
        f"CompilerOptimization/Target/{target}/",
        f"CompilerOptimization/Target/{TARGET_ALIASES.get(target, target)}/",
        f"/CompilerOptimization/CompilerResult/{target}/LLVM14-O2-g/work/",
        f"CompilerOptimization/CompilerResult/{target}/LLVM14-O2-g/work/",
        f"/CompilerOptimization/Result/{target}/seahorn/seahorn-O2-g/work/",
        f"CompilerOptimization/Result/{target}/seahorn/seahorn-O2-g/work/",
    ]
    for marker in markers:
        if marker in raw:
            suffix = raw.split(marker, 1)[1]
            candidates.append(root / suffix)
            parts = Path(suffix).parts
            if parts:
                first = parts[0].lower()
                strip_first = (
                    first == target.lower()
                    or first == TARGET_ALIASES.get(target, target).lower()
                    or first == f"{target.lower()}-src"
                    or first.endswith("-src")
                    or first.endswith("_src")
                    or first.endswith("_rebuild")
                )
                if strip_first and len(parts) > 1:
                    candidates.append(root / Path(*parts[1:]))

    candidates.append(root / raw)

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
    existing = [p for p in candidates if path_exists_maybe(p)]
    if not existing:
        return None, "missing", candidates
    root = target_source_root(target)
    under_root = [p for p in existing if p == root or root in p.parents]
    pool = under_root or existing
    pool = sorted(pool, key=lambda p: (0 if root in p.parents else 1, len(str(p)), str(p)))
    resolution = "exact" if len(pool) == 1 else "ambiguous_chose_first"
    return pool[0], resolution, candidates


def is_probably_system_or_external_path(path_text: str) -> bool:
    low = path_text.lower()
    return (
        low.startswith("/usr/")
        or "/usr/include/" in low
        or "/include/c++/" in low
        or "/lib/gcc/" in low
        or "/llvm-" in low
    )


def classify_region(target: str, source_path: Path | None, reported_file: str) -> tuple[str, str, str]:
    text = str(source_path or reported_file)
    low = text.lower()
    suffix = Path(text).suffix.lower()
    is_header = suffix in {".h", ".hh", ".hpp", ".hxx", ".inc", ".inl", ".tcc"}
    if is_probably_system_or_external_path(text):
        region = "system_header" if is_header else "unknown"
    elif source_path is not None:
        root = target_source_root(target)
        try:
            rel = source_path.resolve().relative_to(root.resolve())
            parts = {p.lower() for p in rel.parts}
        except (ValueError, OSError):
            parts = set()
        third_party_markers = {
            "deps",
            "third_party",
            "third-party",
            "external",
            "extern",
            "vendor",
            "vendors",
            "contrib",
            "3rdparty",
        }
        third_party_names = {"stb_image.h", "xxhash.h", "fast_float.h", "lua", "jemalloc"}
        is_third_party = bool(parts & third_party_markers) or source_path.name.lower() in third_party_names
        try:
            under_root = root.resolve() in source_path.resolve().parents or source_path.resolve() == root.resolve()
        except OSError:
            under_root = False
        if under_root:
            if is_third_party:
                region = "third_party_header" if is_header else "third_party_source"
            else:
                region = "project_header" if is_header else "project_source"
        else:
            region = "unknown"
    elif reported_file.startswith("Target/") or "/CompilerOptimization/Target/" in reported_file:
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


def is_empty_or_comment_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped.startswith("//"):
        return True
    if re.fullmatch(r"/\*.*\*/", stripped):
        return True
    if stripped == "*/":
        return True
    return False


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


def read_source_lines(source_path: Path) -> tuple[list[str] | None, str]:
    key = str(source_path)
    cached = SOURCE_LINE_CACHE.get(key)
    if cached is not None:
        return cached
    try:
        lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
        result: tuple[list[str] | None, str] = (lines, "")
    except OSError as exc:
        result = (None, str(exc))
    SOURCE_LINE_CACHE[key] = result
    return result


def analyze_location(
    target: str,
    reported_file: str,
    line_no: int,
    column_no: int,
    include_snippet: bool,
) -> dict[str, str]:
    cache_key = (target, reported_file, line_no, column_no, include_snippet)
    cached = LOCATION_CACHE.get(cache_key)
    if cached is not None:
        return cached.copy()

    source_path, resolution, candidates = resolve_source(target, reported_file)
    region, header_context, project_source_only = classify_region(target, source_path, reported_file)
    info = {
        "resolved_source": str(source_path) if source_path else "",
        "source_resolution": resolution,
        "location_validity": "unknown",
        "source_region": region,
        "project_source_only": project_source_only,
        "header_context": header_context,
        "source_snippet": "",
        "source_line": "",
        "notes": "",
    }

    def finish() -> dict[str, str]:
        LOCATION_CACHE[cache_key] = info.copy()
        return info

    if line_no == 0:
        info["location_validity"] = "line_zero"
        info["notes"] = f"source_resolution={resolution}"
        return finish()

    if source_path is None:
        if is_probably_system_or_external_path(reported_file):
            info["location_validity"] = "unknown"
            info["notes"] = "external_or_system_source_unresolved;source_candidates=" + "|".join(
                str(p) for p in candidates[:10]
            )
        else:
            info["location_validity"] = "missing_file"
            info["notes"] = "source_candidates=" + "|".join(str(p) for p in candidates[:10])
        return finish()

    lines, read_error = read_source_lines(source_path)
    if lines is None:
        info["location_validity"] = "unknown"
        info["notes"] = f"read_error={read_error}"
        return finish()

    if line_no > len(lines):
        info["location_validity"] = "line_out_of_range"
        info["notes"] = f"resolved_source={source_path};total_lines={len(lines)};source_resolution={resolution}"
        return finish()

    source_line = lines[line_no - 1]
    info["source_line"] = source_line
    if include_snippet:
        info["source_snippet"] = source_snippet(lines, line_no)

    if column_no < 1 or column_no > len(source_line) + 1:
        info["location_validity"] = "column_out_of_range"
    elif is_empty_or_comment_line(source_line):
        info["location_validity"] = "empty_or_comment_line"
    elif source_line.strip().startswith("#"):
        info["location_validity"] = "preprocessor_only"
    else:
        info["location_validity"] = "valid"

    info["notes"] = f"resolved_source={source_path};source_resolution={resolution}"
    return finish()


def priority_for_line_hit(location_validity: str, source_region: str) -> tuple[str, str, str, str, str, str]:
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
            "reported",
            "dg_c_lines_reported_invalid_source_location",
            "0",
        )
    if source_region in {"system_header", "unknown"}:
        return (
            "P2",
            "ExternalOrUnresolvedSource",
            "RunOrLocationWeakEvidence",
            "reported",
            "dg_c_lines_external_or_unresolved_location",
            "1",
        )
    return (
        "P2",
        "ValidDgLineHit",
        "DGLineHit",
        "reported",
        "dg_c_lines_valid_location_without_mismatch",
        "0",
    )


def priority_for_warning(location_validity: str, source_region: str, has_debug_loc: bool) -> tuple[str, str, str, str, str, str]:
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
            "reported",
            "dg_native_warning_invalid_source_location",
            "0",
        )
    if has_debug_loc and source_region not in {"system_header", "unknown"} and location_validity == "valid":
        return (
            "P1",
            "ToolWarningWithDebugLocNeedsReview",
            "ToolWarningDebugLocCandidate",
            "reported",
            "dg_native_warning_with_project_debug_location",
            "1",
        )
    return (
        "P2",
        "ToolWarningOnly",
        "RunOrLocationWeakEvidence",
        "reported",
        "dg_native_warning_without_actionable_source_mapping",
        "1",
    )


def priority_for_failure(row: dict[str, str]) -> tuple[str, str, str, str, str, str]:
    status = (row.get("overall_status") or row.get("line_status") or row.get("dot_status") or "").lower()
    expected = (row.get("expected_unsupported") or "").strip()
    issue = " ".join(
        part
        for part in [row.get("line_issue", ""), row.get("dot_issue", "")]
        if part
    ).lower()
    if "timeout" in status or "timeout" in issue:
        reason = "RunTimeoutOnly"
        status_label = "timeout"
        root = "dg_mode_timeout_without_specific_source_case"
    elif expected == "1" or "unsupported" in issue:
        reason = "UnsupportedModeFailure"
        status_label = "tool failure"
        root = "dg_unsupported_mode_failure"
    else:
        reason = "ToolFailureOnly"
        status_label = "tool failure"
        root = "dg_mode_failure_without_specific_source_case"
    return ("P2", reason, "RunDegradation", status_label, root, "1")


def evidence_list(*paths: Path | None) -> str:
    return ";".join(str(path) for path in paths if path and path_exists_maybe(path))


def find_input_bc(run_dir: Path, target: str) -> str:
    candidates = []
    for path in [run_dir / "commands.log", run_dir / "report.md"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.findall(r"((?:/home/jimi/PaperExperiment|/work)/[^\s'\"`]+?\.bc)", text):
            candidates.append(remap_container_path(match))
    preferred = [p for p in candidates if f"/CompilerOptimization/CompilerResult/{target}/LLVM14-O2-g/" in p]
    if target == "tengine":
        preferred += [p for p in candidates if "/CompilerOptimization/CompilerResult/tengine/LLVM14-O2-g/" in p]
    if preferred:
        return preferred[0]
    for p in candidates:
        if "/CompilerOptimization/CompilerResult/" in p and "/LLVM14-O2-g/" in p:
            return p
    return candidates[0] if candidates else ""


class DebugMetadataIndex:
    def __init__(self, ll_path: Path):
        self.ll_path = ll_path
        self.meta: dict[str, str] = {}
        self.file_cache: dict[str, str] = {}
        if ll_path.exists():
            self._load(ll_path)

    def _load(self, ll_path: Path) -> None:
        meta_re = re.compile(r"^!(\d+)\s*=\s*(.*)$")
        with ll_path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                m = meta_re.match(line.rstrip("\n"))
                if m:
                    self.meta[m.group(1)] = m.group(2)

    def location_for_dbg(self, dbg_id: str) -> tuple[str, int, int] | None:
        text = self.meta.get(dbg_id, "")
        if "!DILocation" not in text:
            return None
        line_m = re.search(r"\bline:\s*(\d+)", text)
        col_m = re.search(r"\bcolumn:\s*(\d+)", text)
        scope_m = re.search(r"\bscope:\s*!(\d+)", text)
        if not scope_m:
            return None
        line_no = int(line_m.group(1)) if line_m else 0
        column_no = int(col_m.group(1)) if col_m else 0
        file_path = self.file_for_scope(scope_m.group(1))
        if not file_path:
            return None
        return file_path, line_no, column_no

    def file_for_scope(self, scope_id: str) -> str:
        if scope_id in self.file_cache:
            return self.file_cache[scope_id]
        seen: set[str] = set()
        cur = scope_id
        for _ in range(40):
            if cur in seen:
                break
            seen.add(cur)
            text = self.meta.get(cur, "")
            file_m = re.search(r"\bfile:\s*!(\d+)", text)
            if file_m:
                file_path = self.file_for_di_file(file_m.group(1))
                if file_path:
                    self.file_cache[scope_id] = file_path
                    return file_path
            scope_m = re.search(r"\bscope:\s*!(\d+)", text)
            if not scope_m:
                break
            cur = scope_m.group(1)
        self.file_cache[scope_id] = ""
        return ""

    def file_for_di_file(self, file_id: str) -> str:
        text = self.meta.get(file_id, "")
        if "!DIFile" not in text:
            return ""
        filename_m = re.search(r'filename:\s*"([^"]*)"', text)
        directory_m = re.search(r'directory:\s*"([^"]*)"', text)
        filename = filename_m.group(1) if filename_m else ""
        directory = directory_m.group(1) if directory_m else ""
        if not filename:
            return ""
        path = Path(filename)
        if path.is_absolute():
            return remap_container_path(str(path))
        if directory:
            return remap_container_path(str(Path(directory) / filename))
        return filename


def find_work_ll(run_dir: Path) -> Path | None:
    work = run_dir / "work"
    if not work.exists():
        return None
    paths = sorted(work.glob("*.ll"))
    return paths[0] if paths else None


def warning_debug_location(warning: str, index: DebugMetadataIndex | None) -> tuple[str, int, int, str]:
    dbg_ids = re.findall(r"!dbg\s+!(\d+)", warning)
    if not dbg_ids or index is None:
        return "", 0, 0, ""
    for dbg_id in dbg_ids:
        loc = index.location_for_dbg(dbg_id)
        if loc:
            file_path, line_no, column_no = loc
            return file_path, line_no, column_no, dbg_id
    return "", 0, 0, ";".join(dbg_ids)


def warning_family(warning: str) -> str:
    low = warning.lower()
    if "unhandled" in low:
        return "unhandled_ir"
    if "shufflevector" in low:
        return "unsupported_shufflevector"
    if "non-0 memset" in low:
        return "nonzero_memset"
    if "inttoptr" in low:
        return "inttoptr_constant"
    if "unsupported" in low:
        return "unsupported_ir"
    if "error:" in low:
        return "native_error"
    if "warning" in low:
        return "native_warning"
    return "native_diagnostic"


def write_csv_header(path: Path, fields: list[str]) -> csv.DictWriter:
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open("w", newline="", encoding="utf-8")
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer._file_handle = f  # type: ignore[attr-defined]
    return writer


def close_writer(writer: csv.DictWriter) -> None:
    handle = getattr(writer, "_file_handle", None)
    if handle is not None:
        handle.close()


def counter_table(counter: Counter) -> str:
    lines = ["| key | count |", "| --- | ---: |"]
    for key, count in counter.most_common():
        lines.append(f"| `{key}` | {count} |")
    return "\n".join(lines)


def status_label_from_step(row: dict[str, str]) -> str:
    status = (row.get("overall_status") or "").lower()
    if "timeout" in status:
        return "timeout"
    if "failed" in status:
        return "tool failure"
    if status:
        return "reported"
    return "reported"


def summarize_run_status(step_rows: list[dict[str, str]]) -> tuple[str, str, str, str]:
    success_modes: list[str] = []
    failed_modes: list[str] = []
    timeout_modes: list[str] = []
    for row in step_rows:
        mode = row.get("step", "")
        status = (row.get("overall_status") or "").lower()
        if status in {"completed", "completed_with_warnings"}:
            success_modes.append(mode)
        elif "timeout" in status:
            timeout_modes.append(mode)
        elif status:
            failed_modes.append(mode)
    if timeout_modes or failed_modes:
        status = "partial/failure" if success_modes else "failure"
    elif success_modes:
        status = "ok"
    else:
        status = "unknown"
    return status, ";".join(success_modes), ";".join(failed_modes), ";".join(timeout_modes)


def write_reports(stats: dict[str, object], run_rows: list[dict[str, str]]) -> None:
    target_lines = [
        "| target | line-hit rows | expanded line-hit cases | warnings | failures | P0 | P1 | P2 | invalid locations | source regions |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for target, tstats in stats["targets"].items():
        pc = tstats["priority_counts"]
        lv = ", ".join(f"{k}={v}" for k, v in sorted(tstats["location_validity_counts"].items()))
        sr = ", ".join(f"{k}={v}" for k, v in sorted(tstats["source_region_counts"].items()))
        target_lines.append(
            f"| {target} | {tstats['line_hit_rows']} | {tstats['expanded_line_hit_cases']} | "
            f"{tstats['warning_rows']} | {tstats['failure_rows']} | "
            f"{pc.get('P0', 0)} | {pc.get('P1', 0)} | {pc.get('P2', 0)} | {lv} | {sr} |"
        )

    report = f"""# DG O2-g Case Collection Report

## Scope

- tool: `dg`
- universe: `O2-g` / `LLVM14-O2-g`
- selected runs: `{len(run_rows)}`
- run list: `{RESULT_TXT}`
- output directory: `{OUT_DIR}`

## Collection Rules

- `summary/line_hits.csv` is treated as DG's normalized native `--c-lines` reported cases.
- Rows with multiple `source_files` are expanded to one standardized case per source candidate.
- `summary/warnings.csv` is collected as native stderr diagnostic evidence; warnings with parseable `!dbg !N` and a resolvable `!DILocation` are mapped back to source using the run's `work/*.ll`.
- `summary/failures.csv` is collected as run/mode-level P2 degradation evidence.
- P0 is reserved for objective invalid source locations according to the matrix plan.
- Valid ordinary DG line hits are kept as P2 unless a warning/debug-location mismatch or another objective invalidity is present.

## Priority Counts

{counter_table(stats['priority_counts'])}

## Priority Reasons

{counter_table(stats['priority_reason_counts'])}

## Case Kinds

{counter_table(stats['case_kind_counts'])}

## Target Summary

{chr(10).join(target_lines)}

## Location Validity

{counter_table(stats['location_validity_counts'])}

## Source Regions

{counter_table(stats['source_region_counts'])}

## Warning Families

{counter_table(stats['warning_family_counts'])}

## Output Files

- `tool_cases.csv`: standardized DG case inventory.
- `tool_runs.csv`: selected run manifest.
- `native_output_profile.md`: DG native output interpretation.
- `collection_manifest.json`: machine-readable stats and run selection.
"""
    (OUT_DIR / "case_collection_report.md").write_text(report, encoding="utf-8")

    native_profile = """# DG Native Output Profile

DG high_precision runs preserve the native analyzer outputs under `log/`.
The most useful case-level native form is `--c-lines` stdout, normalized by the
run scripts into `summary/line_hits.csv` with:

```text
step, analysis_kind, analysis_mode, line, column, source_files, source_count,
output_file, output_line, text
```

The collector maps each reported `line:column` and each source candidate to the
workspace source tree. If a row has multiple `source_files`, each candidate is
emitted as a separate standardized case while preserving the same raw row and
native `output_file:output_line` evidence.

Native stderr diagnostics are preserved in `summary/warnings.csv`. When a warning
contains a parseable `!dbg !N` whose metadata is a `!DILocation`, the collector
uses `work/*.ll` to recover file/line/column and classify that source location.
Warnings without actionable source mapping remain P2 run/tool evidence.

Failures and timeouts from `summary/failures.csv` are run-level P2 evidence unless
a future DG-specific parser recovers a concrete source/IR anchor from the native
stderr.
"""
    (OUT_DIR / "native_output_profile.md").write_text(native_profile, encoding="utf-8")

    manifest = {
        "tool": "dg",
        "universe": "O2-g",
        "result_txt": str(RESULT_TXT),
        "output_dir": str(OUT_DIR),
        "case_count": stats["case_count"],
        "run_count": len(run_rows),
        "priority_counts": dict(stats["priority_counts"]),
        "priority_reason_counts": dict(stats["priority_reason_counts"]),
        "case_kind_counts": dict(stats["case_kind_counts"]),
        "location_validity_counts": dict(stats["location_validity_counts"]),
        "source_region_counts": dict(stats["source_region_counts"]),
        "warning_family_counts": dict(stats["warning_family_counts"]),
        "targets": {
            target: {
                "run_dir": tstats["run_dir"],
                "input_bc": tstats["input_bc"],
                "line_hit_rows": tstats["line_hit_rows"],
                "expanded_line_hit_cases": tstats["expanded_line_hit_cases"],
                "warning_rows": tstats["warning_rows"],
                "warning_dbg_mapped": tstats["warning_dbg_mapped"],
                "failure_rows": tstats["failure_rows"],
                "priority_counts": dict(tstats["priority_counts"]),
                "priority_reason_counts": dict(tstats["priority_reason_counts"]),
                "case_kind_counts": dict(tstats["case_kind_counts"]),
                "location_validity_counts": dict(tstats["location_validity_counts"]),
                "source_region_counts": dict(tstats["source_region_counts"]),
                "warning_family_counts": dict(tstats["warning_family_counts"]),
            }
            for target, tstats in stats["targets"].items()
        },
    }
    (OUT_DIR / "collection_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )


def update_stats(stats: dict[str, object], tstats: dict[str, object], row: dict[str, str]) -> None:
    priority = row["priority"]
    reason = row["priority_reason"]
    kind = row["case_kind"]
    validity = row["location_validity"]
    region = row["source_region"]
    stats["case_count"] += 1
    stats["priority_counts"][priority] += 1
    stats["priority_reason_counts"][reason] += 1
    stats["case_kind_counts"][kind] += 1
    stats["location_validity_counts"][validity] += 1
    stats["source_region_counts"][region] += 1
    tstats["priority_counts"][priority] += 1
    tstats["priority_reason_counts"][reason] += 1
    tstats["case_kind_counts"][kind] += 1
    tstats["location_validity_counts"][validity] += 1
    tstats["source_region_counts"][region] += 1


def collect() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    case_writer = write_csv_header(OUT_DIR / "tool_cases.csv", CASE_FIELDS)
    run_writer = write_csv_header(OUT_DIR / "tool_runs.csv", RUN_FIELDS)
    run_rows: list[dict[str, str]] = []
    stats: dict[str, object] = {
        "case_count": 0,
        "targets": {},
        "priority_counts": Counter(),
        "priority_reason_counts": Counter(),
        "case_kind_counts": Counter(),
        "location_validity_counts": Counter(),
        "source_region_counts": Counter(),
        "warning_family_counts": Counter(),
    }

    try:
        for target, run_dir in parse_result_list():
            line_hits = run_dir / "summary/line_hits.csv"
            warnings = run_dir / "summary/warnings.csv"
            failures = run_dir / "summary/failures.csv"
            steps = run_dir / "summary/steps.csv"
            commands = run_dir / "commands.log"
            report = run_dir / "report.md"
            input_bc = find_input_bc(run_dir, target)
            input_ll = ""
            work_ll = find_work_ll(run_dir)
            if work_ll:
                input_ll = str(work_ll)
            elif input_bc and Path(input_bc).with_suffix(".ll").exists():
                input_ll = str(Path(input_bc).with_suffix(".ll"))

            step_rows = [row for _, row in read_csv(steps)] if steps.exists() else []
            run_status, success_modes, failed_modes, timeout_modes = summarize_run_status(step_rows)
            run_row = {
                "target": target,
                "tool": "dg",
                "selected": "1",
                "run_dir": str(run_dir),
                "run_id": run_dir.name,
                "universe": "O2-g",
                "input_bc": input_bc,
                "input_ll": input_ll,
                "mode": "line_hits+warnings+failures",
                "status": run_status,
                "success_modes": success_modes,
                "failed_modes": failed_modes,
                "timeout_modes": timeout_modes,
                "raw_artifacts": evidence_list(line_hits, warnings, failures, steps, commands, report, work_ll),
                "reason": "user_selected_from_result_txt",
                "excluded_reason": "",
                "notes": "",
            }
            run_rows.append(run_row)
            run_writer.writerow(run_row)

            tstats: dict[str, object] = {
                "run_dir": str(run_dir),
                "input_bc": input_bc,
                "line_hit_rows": 0,
                "expanded_line_hit_cases": 0,
                "warning_rows": 0,
                "warning_dbg_mapped": 0,
                "failure_rows": 0,
                "priority_counts": Counter(),
                "priority_reason_counts": Counter(),
                "case_kind_counts": Counter(),
                "location_validity_counts": Counter(),
                "source_region_counts": Counter(),
                "warning_family_counts": Counter(),
            }
            stats["targets"][target] = tstats
            debug_index = DebugMetadataIndex(work_ll) if work_ll else None
            case_index = 0
            step_status = {row.get("step", ""): status_label_from_step(row) for row in step_rows}

            for csv_row_no, row in read_csv(line_hits):
                tstats["line_hit_rows"] += 1
                line_no = parse_int(row.get("line"))
                column_no = parse_int(row.get("column"))
                source_files = [part for part in row.get("source_files", "").split(";") if part]
                if not source_files:
                    source_files = [""]
                source_count = parse_int(row.get("source_count"), 0)
                for candidate_index, reported_file in enumerate(source_files, start=1):
                    tstats["expanded_line_hit_cases"] += 1
                    include_snippet = line_no == 0 or source_count == 0
                    loc = analyze_location(target, reported_file, line_no, column_no, include_snippet)
                    priority, reason, kind, status_label, root_cause, needs_review = priority_for_line_hit(
                        loc["location_validity"], loc["source_region"]
                    )
                    if priority == "P0" and not loc["source_snippet"]:
                        loc = analyze_location(target, reported_file, line_no, column_no, True)
                    confidence = "0.95" if priority == "P0" else "0.45"
                    case_index += 1
                    notes = [
                        loc["notes"],
                        f"summary_csv=line_hits.csv",
                        f"summary_row={csv_row_no}",
                        f"source_candidate_index={candidate_index}",
                        f"source_count={source_count}",
                        f"native_output_line={row.get('output_line', '')}",
                    ]
                    case = {
                        "case_uid": f"dg.{target}.O2g.{case_index:07d}",
                        "target": target,
                        "tool": "dg",
                        "priority": priority,
                        "priority_reason": reason,
                        "case_kind": kind,
                        "status_label": status_label,
                        "run_dir": str(run_dir),
                        "run_id": run_dir.name,
                        "mode": row.get("step", ""),
                        "input_bc": input_bc,
                        "input_ll": input_ll,
                        "raw_artifact": row.get("output_file", "") or str(line_hits),
                        "raw_row_or_line": row.get("output_line", "") or str(csv_row_no),
                        "reported_file": reported_file,
                        "reported_line": str(line_no),
                        "reported_column": str(column_no),
                        "location_validity": loc["location_validity"],
                        "source_region": loc["source_region"],
                        "project_source_only": loc["project_source_only"],
                        "header_context": loc["header_context"],
                        "ir_function": "",
                        "ir_instruction": "",
                        "ir_line": "",
                        "ir_snippet": "",
                        "source_snippet": loc["source_snippet"],
                        "message": row.get("text", ""),
                        "root_cause_hint": root_cause,
                        "confidence": confidence,
                        "needs_manual_review": needs_review,
                        "manual_verdict": "",
                        "evidence_files": evidence_list(line_hits, Path(row.get("output_file", ""))),
                        "notes": ";".join(part for part in notes if part),
                    }
                    case_writer.writerow(case)
                    update_stats(stats, tstats, case)

            for csv_row_no, row in read_csv(warnings):
                tstats["warning_rows"] += 1
                warning = row.get("warning", "")
                family = warning_family(warning)
                stats["warning_family_counts"][family] += 1
                tstats["warning_family_counts"][family] += 1
                dbg_file, dbg_line, dbg_col, dbg_id = warning_debug_location(warning, debug_index)
                has_debug_loc = bool(dbg_file)
                if has_debug_loc:
                    tstats["warning_dbg_mapped"] += 1
                loc = analyze_location(target, dbg_file, dbg_line, dbg_col, True) if has_debug_loc else {
                    "resolved_source": "",
                    "source_resolution": "none",
                    "location_validity": "no_debug_loc" if "!dbg" not in warning else "unknown",
                    "source_region": "llvm_ir_only",
                    "project_source_only": "0",
                    "header_context": "unknown",
                    "source_snippet": "",
                    "source_line": "",
                    "notes": f"dbg_metadata={dbg_id}" if dbg_id else "no_parseable_dbg_metadata",
                }
                priority, reason, kind, status_label, root_cause, needs_review = priority_for_warning(
                    loc["location_validity"], loc["source_region"], has_debug_loc
                )
                confidence = "0.95" if priority == "P0" else "0.65" if priority == "P1" else "0.35"
                stderr_path = Path(row.get("stderr", "")) if row.get("stderr") else None
                case_index += 1
                notes = [
                    loc["notes"],
                    f"summary_csv=warnings.csv",
                    f"summary_row={csv_row_no}",
                    f"warning_family={family}",
                    f"channel={row.get('channel', '')}",
                    f"dbg_metadata={dbg_id}",
                ]
                case = {
                    "case_uid": f"dg.{target}.O2g.{case_index:07d}",
                    "target": target,
                    "tool": "dg",
                    "priority": priority,
                    "priority_reason": reason,
                    "case_kind": kind,
                    "status_label": status_label,
                    "run_dir": str(run_dir),
                    "run_id": run_dir.name,
                    "mode": row.get("step", ""),
                    "input_bc": input_bc,
                    "input_ll": input_ll,
                    "raw_artifact": str(stderr_path) if stderr_path else str(warnings),
                    "raw_row_or_line": str(csv_row_no),
                    "reported_file": dbg_file,
                    "reported_line": str(dbg_line) if has_debug_loc else "",
                    "reported_column": str(dbg_col) if has_debug_loc else "",
                    "location_validity": loc["location_validity"],
                    "source_region": loc["source_region"],
                    "project_source_only": loc["project_source_only"],
                    "header_context": loc["header_context"],
                    "ir_function": "",
                    "ir_instruction": "",
                    "ir_line": "",
                    "ir_snippet": warning,
                    "source_snippet": loc["source_snippet"],
                    "message": warning,
                    "root_cause_hint": root_cause,
                    "confidence": confidence,
                    "needs_manual_review": needs_review,
                    "manual_verdict": "",
                    "evidence_files": evidence_list(warnings, stderr_path, work_ll),
                    "notes": ";".join(part for part in notes if part),
                }
                case_writer.writerow(case)
                update_stats(stats, tstats, case)

            for csv_row_no, row in read_csv(failures):
                tstats["failure_rows"] += 1
                priority, reason, kind, status_label, root_cause, needs_review = priority_for_failure(row)
                line_stdout = Path(row.get("line_stdout", "")) if row.get("line_stdout") else None
                line_stderr = Path(row.get("line_stderr", "")) if row.get("line_stderr") else None
                dot_stderr = Path(row.get("dot_stderr", "")) if row.get("dot_stderr") else None
                case_index += 1
                message = row.get("line_issue") or row.get("dot_issue") or row.get("overall_status", "")
                notes = [
                    f"summary_csv=failures.csv",
                    f"summary_row={csv_row_no}",
                    f"line_status={row.get('line_status', '')}",
                    f"dot_status={row.get('dot_status', '')}",
                    f"line_exit_code={row.get('line_exit_code', '')}",
                    f"dot_exit_code={row.get('dot_exit_code', '')}",
                    f"expected_unsupported={row.get('expected_unsupported', '')}",
                ]
                case = {
                    "case_uid": f"dg.{target}.O2g.{case_index:07d}",
                    "target": target,
                    "tool": "dg",
                    "priority": priority,
                    "priority_reason": reason,
                    "case_kind": kind,
                    "status_label": status_label,
                    "run_dir": str(run_dir),
                    "run_id": run_dir.name,
                    "mode": row.get("step", ""),
                    "input_bc": input_bc,
                    "input_ll": input_ll,
                    "raw_artifact": str(line_stderr or dot_stderr or failures),
                    "raw_row_or_line": str(csv_row_no),
                    "reported_file": "",
                    "reported_line": "",
                    "reported_column": "",
                    "location_validity": "unknown",
                    "source_region": "llvm_ir_only",
                    "project_source_only": "0",
                    "header_context": "unknown",
                    "ir_function": "",
                    "ir_instruction": "",
                    "ir_line": "",
                    "ir_snippet": "",
                    "source_snippet": "",
                    "message": message,
                    "root_cause_hint": root_cause,
                    "confidence": "0.35",
                    "needs_manual_review": needs_review,
                    "manual_verdict": "",
                    "evidence_files": evidence_list(failures, line_stdout, line_stderr, dot_stderr),
                    "notes": ";".join(part for part in notes if part),
                }
                case_writer.writerow(case)
                update_stats(stats, tstats, case)

        write_reports(stats, run_rows)
    finally:
        close_writer(case_writer)
        close_writer(run_writer)

    print(f"wrote {stats['case_count']} cases and {len(run_rows)} runs to {OUT_DIR}")


if __name__ == "__main__":
    collect()
