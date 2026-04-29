#!/usr/bin/env python3
"""Collect useful Phasar O2-g cases from selected psr-report.txt files."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path("/home/jimi/PaperExperiment")
RESULT_TXT = ROOT / "CompilerOptimization/Result/AllUsefulCases/phasar/result.txt"
OUT_DIR = ROOT / "CompilerOptimization/Result/AllUsefulCases/phasar/O2-g"
TARGET_ROOT = ROOT / "CompilerOptimization/Target"

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
    current = None
    reports: list[tuple[str, Path]] = []
    for line in RESULT_TXT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            continue
        if line.startswith("/"):
            if current is None:
                raise ValueError(f"report without target header: {line}")
            reports.append((current, Path(line)))
    return reports


def remap_path(path_text: str) -> Path:
    if not path_text:
        return Path("")
    candidates: list[Path] = []
    if path_text.startswith("/work/PaperExperiment/"):
        candidates.append(ROOT / path_text[len("/work/PaperExperiment/") :])
    if path_text.startswith("/home/jimi/PaperExperiment/"):
        candidates.append(Path(path_text))
    if path_text.startswith("TARGET/"):
        candidates.append(ROOT / "CompilerOptimization" / path_text)
    if path_text.startswith("CompilerOptimization/"):
        candidates.append(ROOT / path_text)
    candidates.append(Path(path_text))
    for cand in candidates:
        if cand.exists():
            return cand
    return candidates[0]


def resolve_reported_source(target: str, path_text: str) -> tuple[Path, str]:
    """Resolve Phasar's reported path, preferring the canonical Target tree."""
    local = remap_path(path_text)
    normalized = str(local)
    marker = f"/CompilerOptimization/Result/{target}/phasar/phasar-O2-g/work/{target}/"
    if marker in normalized:
        rel = normalized.split(marker, 1)[1]
        target_candidate = TARGET_ROOT / target / rel
        if target_candidate.exists():
            return target_candidate, "result_worktree_to_target"
    return local, "direct_or_container_remap"


def source_root_for_target(target: str) -> Path:
    if target == "curl":
        return TARGET_ROOT / "Curl/7.68.0/curl-curl-7_68_0"
    return TARGET_ROOT / target


def read_commands(phasar_dir: Path) -> str:
    path = find_first_existing(phasar_dir, ("log/commands.log", "logs/commands.log"))
    if path:
        return path.read_text(encoding="utf-8", errors="ignore")
    return ""


def find_first_existing(base: Path, rels: tuple[str, ...]) -> Path | None:
    for rel in rels:
        path = base / rel
        if path.exists():
            return path
    return None


def evidence_list(*paths: Path | None) -> str:
    return ";".join(str(path) for path in paths if path is not None and path.exists())


def extract_input_paths(phasar_dir: Path, report: Path) -> tuple[str, str]:
    commands = read_commands(phasar_dir)
    bc = ""
    m = re.search(r"(?:^|\s)-m\s+['\"]?([^'\"\s]+\.bc)['\"]?", commands)
    if m:
        raw = m.group(1)
        if raw.startswith("artifacts/"):
            bc_path = phasar_dir / raw
        else:
            bc_path = remap_path(raw)
        bc = str(bc_path)
    if not bc:
        artifacts = sorted((phasar_dir / "artifacts").glob("*.bc"))
        if artifacts:
            bc = str(artifacts[0])
    ll = ""
    if bc:
        maybe_ll = Path(bc).with_suffix(".ll")
        if maybe_ll.exists():
            ll = str(maybe_ll)
    return bc, ll


def parse_summary(phasar_dir: Path) -> tuple[str, str]:
    path = find_first_existing(phasar_dir, ("log/summary.csv", "logs/summary.csv"))
    if path:
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("analysis") == "ifds-uninit":
                    return row.get("status", ""), row.get("elapsed_sec", "")
    return "", ""


def parse_report(report: Path) -> list[dict[str, object]]:
    text = report.read_text(encoding="utf-8", errors="ignore").splitlines()
    use_header = re.compile(r"^-+\s+(\d+)\. Use")
    line_inline = re.compile(r"\bLine\s*:\s*(\d+)")
    rows: list[dict[str, object]] = []
    cur: dict[str, object] | None = None

    def flush() -> None:
        if cur is not None:
            rows.append(cur.copy())

    for lineno, line in enumerate(text, start=1):
        m = use_header.match(line)
        if m:
            flush()
            cur = {
                "case": int(m.group(1)),
                "report_line": lineno,
                "variables": "",
                "line": None,
                "source": "",
                "function": "",
                "file": "",
                "ir": "",
                "ir_report_line": "",
            }
            continue
        if cur is None:
            continue
        if line.startswith("Variable(s)"):
            cur["variables"] = line.split(":", 1)[1].strip()
            m2 = line_inline.search(line)
            if m2:
                cur["line"] = int(m2.group(1))
        elif line.startswith("Line"):
            try:
                cur["line"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                cur["line"] = None
        elif "Line" in line and ":" in line:
            m2 = line_inline.search(line)
            if m2:
                cur["line"] = int(m2.group(1))
        elif line.startswith("Source code"):
            cur["source"] = line.split(":", 1)[1].strip()
        elif line.startswith("Function"):
            cur["function"] = line.split(":", 1)[1].strip()
        elif line.startswith("File"):
            cur["file"] = line.split(":", 1)[1].strip()
        elif line.startswith("At IR Statement") and not cur.get("ir"):
            cur["ir"] = line.split(":", 1)[1].strip()
            cur["ir_report_line"] = str(lineno)
    flush()
    return rows


def classify_source_region(local_file: Path, source_root: Path) -> tuple[str, str, str]:
    suffix = local_file.suffix.lower()
    path_text = str(local_file)
    is_header = (
        suffix in {".h", ".hh", ".hpp", ".hxx", ".inc", ".inl", ".tcc"}
        or "/include/" in path_text
        or "/include/c++/" in path_text
    )
    try:
        rel = local_file.resolve().relative_to(source_root.resolve())
        parts = {p.lower() for p in rel.parts}
        third_party_markers = {
            "deps",
            "dependencies",
            "third_party",
            "vendor",
            "external",
            "modules",
        }
        if parts & third_party_markers:
            region = "third_party_header" if is_header else "third_party_source"
            project_only = "0"
        else:
            region = "project_header" if is_header else "project_source"
            project_only = "0" if is_header else "1"
    except ValueError:
        if path_text.startswith("/usr/") or "/include/" in path_text:
            region = "system_header" if is_header or path_text.startswith("/usr/") else "third_party_source"
        else:
            region = "unknown"
        project_only = "0"
    if region.endswith("_header"):
        header_context = region
    else:
        header_context = "not_header"
    return region, project_only, header_context


def is_noncode_line(text: str) -> tuple[bool, str]:
    stripped = text.strip()
    if not stripped:
        return True, "empty_or_comment_line"
    if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*/"):
        return True, "empty_or_comment_line"
    if stripped.startswith("#"):
        return True, "preprocessor_only"
    return False, ""


def classify_case(
    row: dict[str, object],
    local_file: Path,
    source_region: str,
    source_cache: dict[Path, list[str]],
) -> tuple[str, str, str, str, str, str, str]:
    line = int(row.get("line") or 0)
    report_source = str(row.get("source") or "")
    if line == 0:
        return (
            "P0",
            "LineZero",
            "LocationInvalid",
            "line_zero",
            "",
            "0.99",
            "0",
        )
    if not local_file.exists():
        if source_region in {
            "system_header",
            "third_party_header",
            "third_party_source",
            "unknown",
        }:
            return (
                "P2",
                "ExternalOrUnresolvedSource",
                "RunOrLocationWeakEvidence",
                "missing_file",
                "",
                "0.50",
                "1",
            )
        return (
            "P0",
            "MissingSourceFile",
            "LocationInvalid",
            "missing_file",
            "",
            "0.98",
            "0",
        )
    if local_file not in source_cache:
        source_cache[local_file] = local_file.read_text(
            encoding="utf-8", errors="ignore"
        ).splitlines()
    src_lines = source_cache[local_file]
    if line < 1 or line > len(src_lines):
        if source_region in {"system_header", "third_party_header", "third_party_source"}:
            return (
                "P2",
                "ExternalSourceLineOutOfRange",
                "RunOrLocationWeakEvidence",
                "line_out_of_range",
                "",
                "0.55",
                "1",
            )
        return (
            "P0",
            "LineOutOfRange",
            "LocationInvalid",
            "line_out_of_range",
            "",
            "0.99",
            "0",
        )
    actual = src_lines[line - 1]
    noncode, noncode_kind = is_noncode_line(actual)
    if noncode:
        return (
            "P0",
            "SourceLineEmptyOrNonCode",
            "LocationInvalid",
            noncode_kind,
            actual,
            "0.95",
            "0",
        )
    if actual.strip() != report_source.strip():
        return (
            "P0",
            "SourceTextMismatch",
            "LocationDrift",
            "valid",
            actual,
            "0.95",
            "0",
        )
    return ("", "", "", "valid", actual, "", "")


def build_case_rows() -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    cases: list[dict[str, str]] = []
    runs: list[dict[str, str]] = []
    stats: dict[str, object] = {"targets": {}}

    for target, report in parse_result_list():
        if not report.exists():
            raise FileNotFoundError(report)
        source_root = source_root_for_target(target)
        run_dir = report.parent
        run_id = run_dir.name
        phasar_dir = report.parents[3]
        input_bc, input_ll = extract_input_paths(phasar_dir, report)
        run_status, elapsed = parse_summary(phasar_dir)
        commands_log = find_first_existing(phasar_dir, ("log/commands.log", "logs/commands.log"))
        summary_csv = find_first_existing(phasar_dir, ("log/summary.csv", "logs/summary.csv"))
        run_evidence = evidence_list(report, commands_log, summary_csv)
        parsed = parse_report(report)
        counts = Counter()
        useful_counts = Counter()
        source_cache: dict[Path, list[str]] = {}
        resolution_counts = Counter()

        for row in parsed:
            reported_file = str(row.get("file") or "")
            local_file, resolution_note = resolve_reported_source(target, reported_file)
            resolution_counts[resolution_note] += 1
            region, project_only, header_context = classify_source_region(local_file, source_root)
            priority, reason, kind, validity, actual, confidence, needs_review = classify_case(
                row, local_file, region, source_cache
            )
            counts[validity] += 1
            if not priority:
                counts["match_or_not_useful"] += 1
                continue
            useful_counts[priority] += 1
            case_num = int(row["case"])
            rel_reported = reported_file
            try:
                rel_reported = str(local_file.resolve().relative_to(ROOT))
            except Exception:
                pass
            cases.append(
                {
                    "case_uid": f"phasar.{target}.O2g.{case_num:06d}",
                    "target": target,
                    "tool": "phasar",
                    "priority": priority,
                    "priority_reason": reason,
                    "case_kind": kind,
                    "status_label": "reported",
                    "run_dir": str(run_dir),
                    "run_id": run_id,
                    "mode": "ifds-uninit",
                    "input_bc": input_bc,
                    "input_ll": input_ll,
                    "raw_artifact": str(report),
                    "raw_row_or_line": str(row.get("report_line") or case_num),
                    "reported_file": rel_reported,
                    "reported_line": str(int(row.get("line") or 0)),
                    "reported_column": "",
                    "location_validity": validity,
                    "source_region": region,
                    "project_source_only": project_only,
                    "header_context": header_context,
                    "ir_function": str(row.get("function") or ""),
                    "ir_instruction": "",
                    "ir_line": str(row.get("ir_report_line") or ""),
                    "ir_snippet": str(row.get("ir") or ""),
                    "source_snippet": actual,
                    "message": f"Phasar IFDS-Uninitialized use; variables={row.get('variables') or ''}; reported_source={row.get('source') or ''}",
                    "root_cause_hint": "debug_location_or_source_attribution_drift_candidate",
                    "confidence": confidence,
                    "needs_manual_review": needs_review,
                    "manual_verdict": "",
                    "evidence_files": run_evidence,
                    "notes": f"Generated by re-parsing psr-report.txt; source_resolution={resolution_note}; exact source line was revalidated against the resolved source tree.",
                }
            )

        runs.append(
            {
                "target": target,
                "tool": "phasar",
                "selected": "1",
                "run_dir": str(run_dir),
                "run_id": run_id,
                "universe": "O2-g",
                "input_bc": input_bc,
                "input_ll": input_ll,
                "mode": "ifds-uninit",
                "status": run_status or "unknown",
                "success_modes": "ifds-uninit" if run_status == "ok" else "",
                "failed_modes": "" if run_status == "ok" else "ifds-uninit",
                "timeout_modes": "ifds-uninit" if run_status == "timeout" else "",
                "raw_artifacts": run_evidence,
                "reason": "user_selected_from_result_txt",
                "excluded_reason": "",
                "notes": f"parsed_uses={len(parsed)};elapsed_sec={elapsed};validity_counts={dict(counts)};source_resolution_counts={dict(resolution_counts)}",
            }
        )
        stats["targets"][target] = {
            "parsed_uses": len(parsed),
            "useful": dict(useful_counts),
            "validity": dict(counts),
            "source_resolution": dict(resolution_counts),
            "run_status": run_status,
            "input_bc": input_bc,
            "report": str(report),
        }
    return cases, runs, stats


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_report(cases: list[dict[str, str]], runs: list[dict[str, str]], stats: dict[str, object]) -> None:
    by_target_priority: dict[str, Counter] = defaultdict(Counter)
    by_reason: Counter = Counter()
    for row in cases:
        by_target_priority[row["target"]][row["priority"]] += 1
        by_reason[row["priority_reason"]] += 1

    lines = [
        "# Phasar O2-g Useful Cases Collection Report",
        "",
        "## Scope",
        "",
        "- tool: `phasar`",
        "- universe: `O2-g`",
        "- mode: `ifds-uninit`",
        f"- selected reports: `{len(runs)}`",
        "- parser source: re-parsed `psr-report.txt`; did not trust stale `target_linecheck.csv` blindly.",
        "",
        "## Priority Counts",
        "",
        "| target | parsed uses | P0 | P1 | P2 | valid/non-useful | status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    targets = stats["targets"]  # type: ignore[index]
    for run in runs:
        target = run["target"]
        tstat = targets[target]  # type: ignore[index]
        validity = Counter(tstat["validity"])  # type: ignore[index]
        non_useful = validity.get("match_or_not_useful", 0)
        counts = by_target_priority[target]
        lines.append(
            f"| {target} | {tstat['parsed_uses']} | {counts.get('P0', 0)} | {counts.get('P1', 0)} | {counts.get('P2', 0)} | {non_useful} | {run['status']} |"
        )

    lines.extend(
        [
            "",
            "## Priority Reasons",
            "",
            "| reason | count |",
            "| --- | ---: |",
        ]
    )
    for reason, count in sorted(by_reason.items()):
        lines.append(f"| {reason} | {count} |")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `tool_cases.csv`: useful P0/P1/P2 cases only.",
            "- `tool_runs.csv`: selected report/run manifest.",
            "- `native_output_profile.md`: Phasar output format notes.",
            "- `collection_manifest.json`: parser statistics and input reports.",
        ]
    )
    (OUT_DIR / "case_collection_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_profile() -> None:
    text = """# Phasar Native Output Profile

- Native report: `psr-report.txt`.
- Native location fields: `File`, `Function`, `Line`, `Source code`.
- Line format variants observed:
  - standalone: `Line       : N`
  - inline in variables: `Variable(s): Line       : N`
- Collector rule: always re-parse `psr-report.txt` and validate against `CompilerOptimization/Target`.
- Do not blindly trust old `target_linecheck.csv`; older files can misparse inline `Line` fields as `0`.
- `/Result/<target>/phasar/phasar-O2-g/work/<target>/...` paths are remapped back to `CompilerOptimization/Target/<target>/...` when the corresponding target source exists.
- System/external header locations are not promoted to P0 merely because the host cannot resolve the container header path; they are kept as P2 weak evidence.
- P0 is limited to objective invalid project locations: line zero, line out of range, missing project file, empty/comment/preprocessor source line.
- `SourceTextMismatch` is P0 for Phasar because the native report directly prints both `Line` and `Source code`; if the reported source text differs from the actual source line, the report location is objectively inconsistent.
"""
    (OUT_DIR / "native_output_profile.md").write_text(text, encoding="utf-8")


def main() -> None:
    cases, runs, stats = build_case_rows()
    write_csv(OUT_DIR / "tool_cases.csv", CASE_FIELDS, cases)
    write_csv(OUT_DIR / "tool_runs.csv", RUN_FIELDS, runs)
    (OUT_DIR / "collection_manifest.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_profile()
    write_report(cases, runs, stats)
    print(f"wrote {len(cases)} useful cases from {len(runs)} reports to {OUT_DIR}")


if __name__ == "__main__":
    main()
