#!/usr/bin/env python3
"""Collect value cases from cclyzer++ native outputs."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path("/home/jimi/PaperExperiment")
DEFAULT_SOURCE_ROOT = REPO_ROOT / "CompilerOptimization/Target"
SCRIPT_PATH = REPO_ROOT / "CompilerOptimization/Tools/cclyzerpp/analyze_native_value_cases.py"
csv.field_size_limit(1024 * 1024 * 128)


@dataclass
class InstructionRecord:
    instr_id: str
    function: str
    function_dbg: str | None
    index: int
    ll_line_no: int
    text: str
    opcode: str
    result_var: str
    dbg_id: str | None


@dataclass
class FunctionRecord:
    name: str
    dbg_id: str | None
    start_line: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--run-list", type=Path)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--input-ll", type=Path, help="Existing textual LLVM IR for a single --run-dir")
    parser.add_argument("--reuse-existing-maps", action="store_true", help="Reuse existing ir/map indexes under ValueCases")
    parser.add_argument("--min-points-to", type=int, default=5)
    parser.add_argument("--min-alias-bucket", type=int, default=5)
    parser.add_argument("--min-phi-incoming", type=int, default=2)
    parser.add_argument("--source-context", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dirs = collect_run_dirs(args)
    for run_dir in run_dirs:
        analyze_run(run_dir.resolve(), args)


def collect_run_dirs(args: argparse.Namespace) -> list[Path]:
    if args.run_dir and args.run_list:
        raise SystemExit("choose only one of --run-dir or --run-list")
    if args.input_ll and not args.run_dir:
        raise SystemExit("--input-ll is only supported with a single --run-dir")
    if not args.run_dir and not args.run_list:
        raise SystemExit("one of --run-dir or --run-list is required")
    if args.run_dir:
        return [args.run_dir]
    run_dirs: list[Path] = []
    with open(args.run_list, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            run_dirs.append(Path(line))
    return run_dirs


def analyze_run(run_dir: Path, args: argparse.Namespace) -> None:
    status = read_status(run_dir / "status/run_status.tsv")
    if status.get("status") != "reported":
        raise SystemExit(f"{run_dir}: status is not reported")

    target = status["target"]
    universe = status["universe"]
    input_bc = Path(status["input_bc"]).resolve()
    source_root = args.source_root.resolve()
    target_root = resolve_target_root(source_root, target)
    value_root = run_dir / "ValueCases"
    ensure_dirs(
        value_root,
        [
            "inventory",
            "index",
            "map",
            "casebook",
            "snippets",
            "report",
            "ir",
        ],
    )

    command_path = run_dir / "commands/command.txt"
    command_text = command_path.read_text(encoding="utf-8").strip()
    input_bc_from_command = parse_input_bc_from_command(command_text)
    if input_bc_from_command.resolve() != input_bc:
        raise SystemExit(f"{run_dir}: input_bc mismatch between status and command")

    input_bc_sha256 = sha256_file(input_bc)
    provided_input_ll = args.input_ll.resolve() if args.input_ll else None
    input_ll = value_root / "ir" / (input_bc.stem + ".ll")
    ensure_ll_from_bc(input_bc, input_ll, provided_input_ll)
    input_ll_sha256 = sha256_file(input_ll)
    llvm_text_generation = (
        f"copied from provided --input-ll {provided_input_ll}"
        if provided_input_ll
        else "docker opt -S ghcr.io/galoisinc/cclyzerpp-dev:main"
    )

    rel_dir = run_dir / "relations"
    source_index = build_source_index(target_root)

    relation_inventory = build_relation_inventory(rel_dir)
    write_tsv(
        value_root / "inventory/run_inventory.tsv",
        [
            {
                "target": target,
                "universe": universe,
                "run_dir": str(run_dir),
                "status": status["status"],
                "input_bc": str(input_bc),
                "input_ll": str(input_ll),
                "source_root": str(source_root),
                "target_root": str(target_root),
            }
        ],
        ["target", "universe", "run_dir", "status", "input_bc", "input_ll", "source_root", "target_root"],
    )
    write_tsv(
        value_root / "inventory/relation_inventory.tsv",
        relation_inventory,
        ["relation_file", "relation_name", "rows", "columns"],
    )
    write_tsv(
        value_root / "inventory/relation_row_counts.tsv",
        relation_inventory,
        ["relation_file", "relation_name", "rows", "columns"],
    )
    write_tsv(
        value_root / "index/relation_anchor_index.tsv",
        build_relation_anchor_rows(relation_inventory),
        ["relation_name", "primary_anchor_type", "secondary_anchor_type", "notes"],
    )
    write_tsv(
        value_root / "inventory/relation_schema_index.tsv",
        build_relation_schema_rows(relation_inventory),
        ["relation_name", "columns", "schema_hint"],
    )

    instr_pos = load_instr_pos(rel_dir / "instr_pos.csv.gz")
    phi_instr_rows = load_relation_rows(rel_dir / "phi_instr.csv.gz")
    callgraph_rows = load_relation_rows(rel_dir / "subset.callgraph.callgraph_edge.csv.gz")
    alloc_by_instr_rows = load_relation_rows(rel_dir / "subset_lift.allocation_by_instr_ctx.csv.gz")
    phi_pair_value_rows = load_relation_rows(rel_dir / "phi_instr_pair_value.csv.gz")
    phi_pair_label_rows = load_relation_rows(rel_dir / "phi_instr_pair_label.csv.gz")
    variable_debug_name = load_key_value_relation(rel_dir / "variable_has_debug_source_name.csv.gz")
    points_to_by_var, vars_by_alloc, points_to_metric_rows, points_to_alloc_metric_rows = build_points_to_indexes_from_path(
        rel_dir / "subset.var_points_to.csv.gz"
    )
    var_to_instr = load_instr_assigns_for_vars(rel_dir / "instr_assigns_to.csv.gz", set(points_to_by_var))
    alloc_origin = build_allocation_origin_index(alloc_by_instr_rows)
    phi_values = build_phi_pair_index(phi_pair_value_rows)
    phi_labels = build_phi_pair_index(phi_pair_label_rows)
    callgraph_by_instr = build_callgraph_index(callgraph_rows)
    source_cache: dict[str, list[str]] = {}

    candidate_instr_ids = collect_candidate_instr_ids(callgraph_rows, alloc_by_instr_rows, phi_instr_rows, var_to_instr, points_to_by_var)
    if args.reuse_existing_maps:
        mapping_cache = load_candidate_mappings_from_existing_outputs(
            value_root=value_root,
            candidate_instr_ids=candidate_instr_ids,
            source_cache=source_cache,
            target_root=target_root,
            context_lines=args.source_context,
        )
    else:
        metadata = parse_ll_metadata(input_ll)
        write_tsv(
            value_root / "index/ir_debug_index.tsv",
            build_ir_debug_index_rows(metadata),
            ["metadata_id", "kind", "line", "column", "file_ref", "scope_ref", "inlined_at_ref"],
        )
        mapping_cache = stream_ll_indexes_and_maps(
            ll_path=input_ll,
            module_prefix=infer_module_prefix(run_dir),
            metadata=metadata,
            instr_pos=instr_pos,
            source_index=source_index,
            source_cache=source_cache,
            target_root=target_root,
            context_lines=args.source_context,
            value_root=value_root,
            candidate_instr_ids=candidate_instr_ids,
        )

    all_cases: list[dict[str, str]] = []
    casebook_rows: list[dict[str, str]] = []
    case_counter = 0
    seen_case_keys: set[tuple[str, str, str]] = set()

    def add_case(
        phenomenon_label: str,
        case_kind: str,
        relation_name: str,
        relation_file: str,
        row_number: int,
        row_hash: str,
        raw_row: str,
        anchor_type: str,
        anchor_id: str,
        anchor_role: str,
        metric_name: str,
        metric_value: int | str,
        mapping: dict[str, str],
        source_ir_consistency: str,
        root_cause_hint: str,
        confidence: str,
        priority: str,
        variable_id: str = "",
        variable_debug_source_name: str = "",
        allocation_id: str = "",
        callee_function: str = "",
        evidence_suffix: str = "",
        manual_notes: str = "",
    ) -> None:
        nonlocal case_counter
        case_key = (phenomenon_label, relation_name, anchor_id)
        if case_key in seen_case_keys:
            return
        seen_case_keys.add(case_key)
        case_counter += 1
        case_id = f"cclyzerpp_{target}_O2g_{case_counter:06d}"
        demangled_callee = demangle_function(callee_function) if callee_function else ""
        evidence_paths = write_case_evidence(
            value_root=value_root,
            case_id=case_id,
            mapping=mapping,
            raw_row=raw_row,
            evidence_suffix=evidence_suffix or anchor_id,
        )
        row = {
            "case_id": case_id,
            "target": target,
            "run_dir": str(run_dir),
            "input_bc": str(input_bc),
            "input_ll": str(input_ll),
            "relation_file": relation_file,
            "relation_name": relation_name,
            "relation_row_number": str(row_number),
            "relation_row_hash": row_hash,
            "raw_row": raw_row,
            "anchor_type": anchor_type,
            "anchor_id": anchor_id,
            "anchor_role": anchor_role,
            "function_id": mapping.get("function_id", ""),
            "demangled_function": mapping.get("demangled_function", ""),
            "ir_instruction_id": mapping.get("instr_id", ""),
            "ir_opcode": mapping.get("ir_opcode", ""),
            "ir_snippet": mapping.get("ir_snippet", ""),
            "source_file": mapping.get("source_file", ""),
            "line": mapping.get("line", ""),
            "column": mapping.get("column", ""),
            "source_line_text": mapping.get("source_line_text", ""),
            "source_context": mapping.get("source_context", ""),
            "debug_line": mapping.get("debug_line", ""),
            "debug_column": mapping.get("debug_column", ""),
            "inline_stack": mapping.get("inline_stack", ""),
            "variable_id": variable_id,
            "variable_debug_source_name": variable_debug_source_name,
            "allocation_id": allocation_id,
            "callee_function": callee_function,
            "demangled_callee": demangled_callee,
            "metric_name": metric_name,
            "metric_value": str(metric_value),
            "mapping_status": mapping.get("mapping_status", ""),
            "case_kind": case_kind,
            "phenomenon_label": phenomenon_label,
            "source_ir_consistency": source_ir_consistency,
            "root_cause_hint": root_cause_hint,
            "confidence": confidence,
            "priority": priority,
            "manual_verdict": "",
            "manual_notes": manual_notes,
            "evidence_files": ",".join(evidence_paths),
        }
        all_cases.append(row)
        casebook_rows.append(
            {
                "case_id": case_id,
                "phenomenon_label": phenomenon_label,
                "case_kind": case_kind,
                "priority": priority,
                "mapping_status": mapping.get("mapping_status", ""),
                "source_file": mapping.get("source_file", ""),
                "line": mapping.get("line", ""),
                "function_id": mapping.get("function_id", ""),
            }
        )
        write_case_markdown(value_root / "casebook" / f"{case_id}.md", row)

    # Wanted-LineColumnMissing
    for relation_rows, anchor_role, priority in [
        (callgraph_rows, "callsite", "P0"),
        (alloc_by_instr_rows, "allocation_origin", "P0"),
        (phi_instr_rows, "phi", "P1"),
    ]:
        for entry in relation_rows:
            row = entry["row"]
            instr_id = ""
            metric_name = ""
            metric_value = 1
            allocation_id = ""
            if anchor_role == "callsite":
                instr_id = row[3]
                metric_name = "callgraph_callee_count"
                metric_value = len(callgraph_by_instr.get(instr_id, []))
            elif anchor_role == "allocation_origin":
                instr_id = row[1]
                allocation_id = row[3]
                metric_name = "allocation_user_count"
                metric_value = len(vars_by_alloc.get(allocation_id, set()))
            else:
                instr_id = row[0]
                metric_name = "phi_incoming_count"
                metric_value = len(phi_values.get(instr_id, []))
            mapping = mapping_cache.get(instr_id)
            if not mapping or mapping["mapping_status"] != "NoDebugLoc":
                continue
            add_case(
                phenomenon_label="Wanted-LineColumnMissing",
                case_kind="LocationDrift",
                relation_name=entry["relation_name"],
                relation_file=entry["relation_file"],
                row_number=entry["row_number"],
                row_hash=entry["row_hash"],
                raw_row=entry["raw_row"],
                anchor_type="instruction",
                anchor_id=instr_id,
                anchor_role=anchor_role,
                metric_name=metric_name,
                metric_value=metric_value,
                mapping=mapping,
                source_ir_consistency="unknown",
                root_cause_hint="debug_location_loss_or_optimized_IR",
                confidence="high",
                priority=priority,
                allocation_id=allocation_id,
            )

    for var_id, allocs in sorted(points_to_by_var.items(), key=lambda item: (-len(item[1]), item[0])):
        instr_id = var_to_instr.get(var_id)
        if not instr_id:
            continue
        mapping = mapping_cache.get(instr_id)
        if not mapping or mapping["mapping_status"] != "NoDebugLoc":
            continue
        variable_name = variable_debug_name.get(var_id, "")
        rep = points_to_metric_rows[var_id]
        add_case(
            phenomenon_label="Wanted-LineColumnMissing",
            case_kind="LocationDrift",
            relation_name=rep["relation_name"],
            relation_file=rep["relation_file"],
            row_number=rep["row_number"],
            row_hash=rep["row_hash"],
            raw_row=rep["raw_row"],
            anchor_type="instruction",
            anchor_id=instr_id,
            anchor_role="points_to_variable",
            metric_name="points_to_count",
            metric_value=len(allocs),
            mapping=mapping,
            source_ir_consistency="unknown",
            root_cause_hint="debug_location_loss_or_optimized_IR",
            confidence="high",
            priority="P0" if len(allocs) >= args.min_points_to else "P1",
            variable_id=var_id,
            variable_debug_source_name=variable_name,
        )

    # Wanted-CodeMismatch: callsites and allocation origins.
    for entry in callgraph_rows:
        row = entry["row"]
        callee_function = row[1]
        instr_id = row[3]
        mapping = mapping_cache.get(instr_id)
        if not mapping or mapping["mapping_status"] not in {"MappedExact", "MappedLineOnly"}:
            continue
        if not is_callsite_mismatch(mapping["source_line_text"], mapping["source_context"], demangle_function(callee_function)):
            continue
        add_case(
            phenomenon_label="Wanted-CodeMismatch",
            case_kind="LocationDrift",
            relation_name=entry["relation_name"],
            relation_file=entry["relation_file"],
            row_number=entry["row_number"],
            row_hash=entry["row_hash"],
            raw_row=entry["raw_row"],
            anchor_type="instruction",
            anchor_id=instr_id,
            anchor_role="callsite",
            metric_name="callgraph_callee_count",
            metric_value=len(callgraph_by_instr.get(instr_id, [])),
            mapping=override_mapping_status(mapping, "SourceExistsCodeMismatch"),
            source_ir_consistency="inconsistent",
            root_cause_hint="DWARF_location_drift_or_inline_attribution",
            confidence="medium",
            priority="P0",
            callee_function=callee_function,
        )

    for allocation_id, origin_instr in alloc_origin.items():
        mapping = mapping_cache.get(origin_instr)
        if not mapping or mapping["mapping_status"] not in {"MappedExact", "MappedLineOnly"}:
            continue
        if not is_allocation_semantics_mismatch(mapping["source_line_text"], mapping["source_context"], mapping["ir_opcode"]):
            continue
        rep_row = first_relation_row_for_value(alloc_by_instr_rows, allocation_id)
        if rep_row is None:
            continue
        add_case(
            phenomenon_label="Wanted-CodeMismatch",
            case_kind="LocationDrift",
            relation_name=rep_row["relation_name"],
            relation_file=rep_row["relation_file"],
            row_number=rep_row["row_number"],
            row_hash=rep_row["row_hash"],
            raw_row=rep_row["raw_row"],
            anchor_type="instruction",
            anchor_id=origin_instr,
            anchor_role="allocation_origin",
            metric_name="allocation_user_count",
            metric_value=len(vars_by_alloc.get(allocation_id, set())),
            mapping=override_mapping_status(mapping, "SourceExistsCodeMismatch"),
            source_ir_consistency="inconsistent",
            root_cause_hint="DWARF_location_drift_or_inline_attribution",
            confidence="medium",
            priority="P1",
            allocation_id=allocation_id,
        )

    # Wanted-AliasCollapseWithBadLocation
    for var_id, allocs in sorted(points_to_by_var.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(allocs) < args.min_points_to:
            continue
        instr_id = var_to_instr.get(var_id, "")
        if not instr_id:
            continue
        mapping = mapping_cache.get(instr_id)
        if not mapping:
            continue
        bad_mapping = mapping["mapping_status"] in {"NoDebugLoc", "SourceFileMissing", "LineOutOfRange", "ColumnOutOfRange", "SourceExistsCodeMismatch"}
        if not bad_mapping:
            continue
        rep = points_to_metric_rows[var_id]
        add_case(
            phenomenon_label="Wanted-AliasCollapseWithBadLocation",
            case_kind="AliasCollapse",
            relation_name=rep["relation_name"],
            relation_file=rep["relation_file"],
            row_number=rep["row_number"],
            row_hash=rep["row_hash"],
            raw_row=rep["raw_row"],
            anchor_type="variable",
            anchor_id=var_id,
            anchor_role="points_to_variable",
            metric_name="points_to_count",
            metric_value=len(allocs),
            mapping=mapping,
            source_ir_consistency="unknown" if mapping["mapping_status"] == "NoDebugLoc" else "inconsistent",
            root_cause_hint="SROA_or_Mem2Reg_or_Phi-node_merge_or_GVN",
            confidence="medium",
            priority="P1" if len(allocs) < 10 else "P0",
            variable_id=var_id,
            variable_debug_source_name=variable_debug_name.get(var_id, ""),
        )

    for allocation_id, vars_for_alloc in sorted(vars_by_alloc.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(vars_for_alloc) < args.min_alias_bucket:
            continue
        origin_instr = alloc_origin.get(allocation_id, "")
        if not origin_instr:
            continue
        mapping = mapping_cache.get(origin_instr)
        if not mapping:
            continue
        bad_mapping = mapping["mapping_status"] in {"NoDebugLoc", "SourceFileMissing", "LineOutOfRange", "ColumnOutOfRange", "SourceExistsCodeMismatch"}
        debug_names = sorted({variable_debug_name.get(var, "") for var in vars_for_alloc if variable_debug_name.get(var, "")})
        if not bad_mapping and len(debug_names) <= 1:
            continue
        rep_row = points_to_alloc_metric_rows.get(allocation_id)
        if rep_row is None:
            continue
        add_case(
            phenomenon_label="Wanted-AliasCollapseWithBadLocation",
            case_kind="AliasCollapse",
            relation_name=rep_row["relation_name"],
            relation_file=rep_row["relation_file"],
            row_number=rep_row["row_number"],
            row_hash=rep_row["row_hash"],
            raw_row=rep_row["raw_row"],
            anchor_type="allocation",
            anchor_id=allocation_id,
            anchor_role="alias_bucket",
            metric_name="alias_bucket_size",
            metric_value=len(vars_for_alloc),
            mapping=mapping,
            source_ir_consistency="unknown" if mapping["mapping_status"] == "NoDebugLoc" else "inconsistent",
            root_cause_hint="SROA_or_Mem2Reg_or_Phi-node_merge_or_GVN",
            confidence="medium",
            priority="P1" if len(vars_for_alloc) < 10 else "P0",
            allocation_id=allocation_id,
            manual_notes=f"debug_names={';'.join(debug_names[:6])}",
        )

    # Wanted-AllocationSiteDrift
    for allocation_id, origin_instr in alloc_origin.items():
        if allocation_id.endswith("__rep"):
            continue
        mapping = mapping_cache.get(origin_instr)
        if not mapping:
            continue
        bad_mapping = mapping["mapping_status"] in {"NoDebugLoc", "SourceFileMissing", "LineOutOfRange", "ColumnOutOfRange"}
        mismatch = is_allocation_semantics_mismatch(mapping["source_line_text"], mapping["source_context"], mapping["ir_opcode"])
        if not bad_mapping and not mismatch:
            continue
        rep_row = first_relation_row_for_value(alloc_by_instr_rows, allocation_id)
        if rep_row is None:
            continue
        final_mapping = mapping
        consistency = "unknown"
        if mismatch and mapping["mapping_status"] in {"MappedExact", "MappedLineOnly"}:
            final_mapping = override_mapping_status(mapping, "SourceExistsCodeMismatch")
            consistency = "inconsistent"
        add_case(
            phenomenon_label="Wanted-AllocationSiteDrift",
            case_kind="AllocationSiteDrift",
            relation_name=rep_row["relation_name"],
            relation_file=rep_row["relation_file"],
            row_number=rep_row["row_number"],
            row_hash=rep_row["row_hash"],
            raw_row=rep_row["raw_row"],
            anchor_type="allocation",
            anchor_id=allocation_id,
            anchor_role="allocation_origin",
            metric_name="allocation_user_count",
            metric_value=len(vars_by_alloc.get(allocation_id, set())),
            mapping=final_mapping,
            source_ir_consistency=consistency,
            root_cause_hint="allocation_attribution_drift_or_inline_or_SROA",
            confidence="high" if bad_mapping else "medium",
            priority="P0" if bad_mapping else "P1",
            allocation_id=allocation_id,
        )

    # Wanted-PhiMergeLocationDrift
    for entry in phi_instr_rows:
        instr_id = entry["row"][0]
        incoming_values = phi_values.get(instr_id, [])
        incoming_labels = phi_labels.get(instr_id, [])
        incoming_count = max(len(incoming_values), len(incoming_labels))
        if incoming_count < args.min_phi_incoming:
            continue
        mapping = mapping_cache.get(instr_id)
        if not mapping:
            continue
        incoming_debug_names = sorted(
            {
                variable_debug_name.get(value, "")
                for _, value in incoming_values
                if variable_debug_name.get(value, "")
            }
        )
        distinct_sources = len(set(incoming_debug_names))
        mismatch = is_phi_merge_mismatch(mapping["source_line_text"], mapping["source_context"], incoming_debug_names, incoming_count)
        bad_mapping = mapping["mapping_status"] in {"NoDebugLoc", "SourceFileMissing", "LineOutOfRange", "ColumnOutOfRange"}
        if not bad_mapping and not mismatch and distinct_sources <= 1:
            continue
        final_mapping = mapping
        consistency = "unknown"
        if mismatch and mapping["mapping_status"] in {"MappedExact", "MappedLineOnly"}:
            final_mapping = override_mapping_status(mapping, "SourceExistsCodeMismatch")
            consistency = "inconsistent"
        add_case(
            phenomenon_label="Wanted-PhiMergeLocationDrift",
            case_kind="PhiMergeLocationDrift",
            relation_name=entry["relation_name"],
            relation_file=entry["relation_file"],
            row_number=entry["row_number"],
            row_hash=entry["row_hash"],
            raw_row=entry["raw_row"],
            anchor_type="instruction",
            anchor_id=instr_id,
            anchor_role="phi",
            metric_name="phi_incoming_count",
            metric_value=incoming_count,
            mapping=final_mapping,
            source_ir_consistency=consistency,
            root_cause_hint="Mem2Reg_or_Phi-node_merge_or_CFG_simplification",
            confidence="medium",
            priority="P0" if bad_mapping or incoming_count >= 4 else "P1",
            manual_notes=f"incoming_debug_names={';'.join(incoming_debug_names[:6])}",
        )

    all_cases.sort(key=lambda row: (priority_rank(row["priority"]), row["phenomenon_label"], row["case_id"]))
    all_case_fields = [
        "case_id",
        "target",
        "run_dir",
        "input_bc",
        "input_ll",
        "relation_file",
        "relation_name",
        "relation_row_number",
        "relation_row_hash",
        "raw_row",
        "anchor_type",
        "anchor_id",
        "anchor_role",
        "function_id",
        "demangled_function",
        "ir_instruction_id",
        "ir_opcode",
        "ir_snippet",
        "source_file",
        "line",
        "column",
        "source_line_text",
        "source_context",
        "debug_line",
        "debug_column",
        "inline_stack",
        "variable_id",
        "variable_debug_source_name",
        "allocation_id",
        "callee_function",
        "demangled_callee",
        "metric_name",
        "metric_value",
        "mapping_status",
        "case_kind",
        "phenomenon_label",
        "source_ir_consistency",
        "root_cause_hint",
        "confidence",
        "priority",
        "manual_verdict",
        "manual_notes",
        "evidence_files",
    ]
    write_csv(
        value_root / "all_cases.csv",
        all_cases,
        all_case_fields,
    )
    write_tsv(
        value_root / "case_triage.tsv",
        all_cases,
        [
            "case_id",
            "priority",
            "phenomenon_label",
            "case_kind",
            "mapping_status",
            "confidence",
            "metric_name",
            "metric_value",
            "relation_name",
            "anchor_type",
            "anchor_id",
            "anchor_role",
            "function_id",
            "source_file",
            "line",
            "column",
            "root_cause_hint",
        ],
    )
    write_tsv(
        value_root / "casebook/case_index.tsv",
        casebook_rows,
        ["case_id", "phenomenon_label", "case_kind", "priority", "mapping_status", "source_file", "line", "function_id"],
    )
    write_tsv(
        value_root / "map/location_drift_candidates.tsv",
        [r for r in all_cases if r["case_kind"] in {"LocationDrift", "AllocationSiteDrift", "PhiMergeLocationDrift"}],
        [
            "case_id",
            "phenomenon_label",
            "relation_name",
            "anchor_id",
            "function_id",
            "source_file",
            "line",
            "column",
            "mapping_status",
            "priority",
        ],
    )

    manifest = {
        "tool": "cclyzer++",
        "universe": universe,
        "run_status": status["status"],
        "target": target,
        "compiler_universe": universe,
        "run_dir": str(run_dir),
        "input_bc": str(input_bc),
        "input_bc_from_status": status["input_bc"],
        "input_bc_from_command": str(input_bc_from_command),
        "input_bc_sha256": input_bc_sha256,
        "input_ll": str(input_ll),
        "provided_input_ll": str(provided_input_ll) if provided_input_ll else "",
        "input_ll_sha256": input_ll_sha256,
        "command_path": str(command_path),
        "command_line": command_text,
        "log_path": status["log_path"],
        "source_root": str(source_root),
        "target_root": str(target_root),
        "analysis_script": str(SCRIPT_PATH),
        "analysis_time": datetime.now().isoformat(),
        "llvm_dis_version": llvm_text_generation,
        "llvm_text_generation": llvm_text_generation,
        "relation_file_count": len(relation_inventory),
        "case_count": len(all_cases),
    }
    (value_root / "analysis_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(value_root / "report/final_native_output_analysis.md", manifest, relation_inventory, all_cases)


def read_status(path: Path) -> dict[str, str]:
    with open(path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = list(reader)
    if len(rows) != 1:
        raise SystemExit(f"expected one status row in {path}")
    return rows[0]


def resolve_target_root(source_root: Path, target: str) -> Path:
    direct = source_root / target
    if direct.exists():
        return direct
    for child in source_root.iterdir():
        if child.is_dir() and child.name.lower() == target.lower():
            return child
    if target.endswith("_sndfile_convert"):
        fallback = source_root / "libsndfile"
        if fallback.exists():
            return fallback
    raise SystemExit(f"cannot resolve target root for {target}")


def ensure_dirs(root: Path, children: list[str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for child in children:
        (root / child).mkdir(parents=True, exist_ok=True)


def parse_input_bc_from_command(command_text: str) -> Path:
    matches = re.findall(r"'(/work/[^']+\.bc)'", command_text)
    if not matches:
        raise SystemExit("cannot parse input bc from command")
    return Path(matches[-1].replace("/work", str(REPO_ROOT)))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def ensure_ll_from_bc(input_bc: Path, output_ll: Path, provided_ll: Path | None = None) -> None:
    if provided_ll:
        if not provided_ll.exists():
            raise SystemExit(f"provided --input-ll does not exist: {provided_ll}")
        if output_ll.exists() and sha256_file(output_ll) == sha256_file(provided_ll):
            return
        shutil.copy2(provided_ll, output_ll)
        return
    if output_ll.exists():
        return
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{REPO_ROOT}:/work",
        "-w",
        "/work",
        "--entrypoint",
        "/bin/bash",
        "ghcr.io/galoisinc/cclyzerpp-dev:main",
        "-lc",
        f"mkdir -p '{to_work_path(output_ll.parent)}' && opt -S '{to_work_path(input_bc)}' -o '{to_work_path(output_ll)}'",
    ]
    subprocess.run(command, check=True)


def to_work_path(path: Path) -> str:
    resolved = path.resolve()
    prefix = str(REPO_ROOT)
    if not str(resolved).startswith(prefix):
        raise SystemExit(f"path outside repo root: {path}")
    return "/work" + str(resolved)[len(prefix):]


def build_source_index(target_root: Path) -> dict[str, list[Path]]:
    by_basename: dict[str, list[Path]] = defaultdict(list)
    for root, _, files in os.walk(target_root):
        for name in files:
            if name.endswith((".c", ".cc", ".cpp", ".h", ".hpp")):
                by_basename[name].append(Path(root) / name)
    return by_basename


def infer_module_prefix(run_dir: Path) -> str:
    instr_func_path = run_dir / "relations/instr_func.csv.gz"
    with gzip.open(instr_func_path, "rt", encoding="utf-8", errors="replace") as fh:
        first = fh.readline().strip()
    if not first:
        return "<llvm-link>"
    instr_id = first.split("\t", 1)[0]
    match = re.match(r"^(<[^>]+>):", instr_id)
    return match.group(1) if match else "<llvm-link>"


def collect_candidate_instr_ids(
    callgraph_rows: list[dict[str, object]],
    alloc_by_instr_rows: list[dict[str, object]],
    phi_instr_rows: list[dict[str, object]],
    var_to_instr: dict[str, str],
    points_to_by_var: dict[str, set[str]],
) -> set[str]:
    candidate_instr_ids: set[str] = set()
    for entry in callgraph_rows:
        row = entry["row"]
        if len(row) >= 4:
            candidate_instr_ids.add(str(row[3]))
    for entry in alloc_by_instr_rows:
        row = entry["row"]
        if len(row) >= 2:
            candidate_instr_ids.add(str(row[1]))
    for entry in phi_instr_rows:
        row = entry["row"]
        if row:
            candidate_instr_ids.add(str(row[0]))
    for var_id in points_to_by_var:
        instr_id = var_to_instr.get(var_id)
        if instr_id:
            candidate_instr_ids.add(instr_id)
    return candidate_instr_ids


def parse_ll_metadata(ll_path: Path) -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}
    with open(ll_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            stripped = line.strip()
            meta = parse_metadata_line(stripped)
            if meta:
                metadata[meta["id"]] = meta
    return metadata


def stream_ll_indexes_and_maps(
    ll_path: Path,
    module_prefix: str,
    metadata: dict[str, dict[str, str]],
    instr_pos: dict[str, tuple[str, str]],
    source_index: dict[str, list[Path]],
    source_cache: dict[str, list[str]],
    target_root: Path,
    context_lines: int,
    value_root: Path,
    candidate_instr_ids: set[str],
) -> dict[str, dict[str, str]]:
    mapping_cache: dict[str, dict[str, str]] = {}
    current_function: str | None = None
    current_dbg: str | None = None
    current_index = 0
    with (
        open(ll_path, encoding="utf-8", errors="replace") as fh,
        open_tsv_writer(
            value_root / "index/ir_instruction_index.tsv",
            ["instr_id", "function_id", "ll_line_no", "opcode", "result_var", "dbg_id", "text"],
        ) as instr_writer,
        open_tsv_writer(
            value_root / "index/ir_function_index.tsv",
            ["function_id", "dbg_id", "start_line"],
        ) as func_writer,
        open_tsv_writer(
            value_root / "map/native_fact_source_map.tsv",
            [
                "instr_id",
                "function_id",
                "demangled_function",
                "ir_opcode",
                "ir_result_variable",
                "cclyzer_line",
                "cclyzer_column",
                "source_file",
                "line",
                "column",
                "mapping_status",
                "inline_stack",
            ],
        ) as source_map_writer,
        open_tsv_writer(
            value_root / "map/native_fact_classification.tsv",
            ["instr_id", "mapping_status", "source_file", "line", "column", "inline_stack", "ir_opcode"],
        ) as classification_writer,
    ):
        for lineno, line in enumerate(fh, start=1):
            stripped = line.strip()
            if stripped.startswith("define "):
                name_match = re.search(r"@([^(]+)\(", stripped)
                dbg_match = re.search(r"!dbg !(\d+)", stripped)
                if name_match:
                    current_function = name_match.group(1)
                    current_dbg = dbg_match.group(1) if dbg_match else None
                    current_index = 0
                    func_writer.writerow(
                        {
                            "function_id": current_function,
                            "dbg_id": current_dbg or "",
                            "start_line": str(lineno),
                        }
                    )
                continue
            if current_function and stripped == "}":
                current_function = None
                current_dbg = None
                current_index = 0
                continue
            if not current_function or not is_instruction_line(stripped):
                continue
            dbg_match = re.search(r"!dbg !(\d+)", stripped)
            dbg_id = dbg_match.group(1) if dbg_match else None
            result_var = ""
            rhs = stripped
            if " = " in stripped:
                result_var, rhs = stripped.split(" = ", 1)
                result_var = result_var.strip()
            opcode = extract_opcode(rhs)
            instr_id = f"{module_prefix}:{current_function}:{current_index}"
            record = InstructionRecord(
                instr_id=instr_id,
                function=current_function,
                function_dbg=current_dbg,
                index=current_index,
                ll_line_no=lineno,
                text=stripped,
                opcode=opcode,
                result_var=result_var,
                dbg_id=dbg_id,
            )
            current_index += 1
            instr_writer.writerow(
                {
                    "instr_id": instr_id,
                    "function_id": record.function,
                    "ll_line_no": str(record.ll_line_no),
                    "opcode": record.opcode,
                    "result_var": record.result_var,
                    "dbg_id": record.dbg_id or "",
                    "text": record.text,
                }
            )
            mapping = map_instruction_record(
                record=record,
                instr_pos=instr_pos,
                metadata=metadata,
                source_index=source_index,
                source_cache=source_cache,
                target_root=target_root,
                context_lines=context_lines,
            )
            mapping["function_id"] = record.function
            mapping["demangled_function"] = demangle_function(record.function)
            source_map_writer.writerow(
                {
                    "instr_id": instr_id,
                    "function_id": mapping["function_id"],
                    "demangled_function": mapping["demangled_function"],
                    "ir_opcode": mapping["ir_opcode"],
                    "ir_result_variable": mapping["ir_result_variable"],
                    "cclyzer_line": mapping["debug_line"],
                    "cclyzer_column": mapping["debug_column"],
                    "source_file": mapping["source_file"],
                    "line": mapping["line"],
                    "column": mapping["column"],
                    "mapping_status": mapping["mapping_status"],
                    "inline_stack": mapping["inline_stack"],
                }
            )
            classification_writer.writerow(
                {
                    "instr_id": instr_id,
                    "mapping_status": mapping["mapping_status"],
                    "source_file": mapping["source_file"],
                    "line": mapping["line"],
                    "column": mapping["column"],
                    "inline_stack": mapping["inline_stack"],
                    "ir_opcode": mapping["ir_opcode"],
                }
            )
            if instr_id in candidate_instr_ids:
                mapping_cache[instr_id] = mapping
    return mapping_cache


def load_candidate_mappings_from_existing_outputs(
    value_root: Path,
    candidate_instr_ids: set[str],
    source_cache: dict[str, list[str]],
    target_root: Path,
    context_lines: int,
) -> dict[str, dict[str, str]]:
    record_by_instr: dict[str, dict[str, str]] = {}
    with open(value_root / "index/ir_instruction_index.tsv", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            instr_id = row["instr_id"]
            if instr_id not in candidate_instr_ids:
                continue
            record_by_instr[instr_id] = row

    mapping_cache: dict[str, dict[str, str]] = {}
    with open(value_root / "map/native_fact_source_map.tsv", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            instr_id = row["instr_id"]
            if instr_id not in candidate_instr_ids:
                continue
            ir_row = record_by_instr.get(instr_id, {})
            source_file = row["source_file"]
            line = row["line"]
            column = row["column"]
            source_line_text, source_context = load_source_context(
                source_file=source_file,
                line=line,
                column=column,
                source_cache=source_cache,
                target_root=target_root,
                context_lines=context_lines,
            )
            mapping_cache[instr_id] = {
                "instr_id": instr_id,
                "function_id": row["function_id"],
                "demangled_function": row["demangled_function"],
                "ir_opcode": row["ir_opcode"],
                "ir_result_variable": ir_row.get("result_var", ""),
                "ir_snippet": ir_row.get("text", ""),
                "debug_line": row["cclyzer_line"],
                "debug_column": row["cclyzer_column"],
                "source_file": source_file,
                "line": line,
                "column": column,
                "inline_stack": row["inline_stack"],
                "source_line_text": source_line_text,
                "source_context": source_context,
                "mapping_status": row["mapping_status"],
            }
    return mapping_cache


def is_instruction_line(stripped: str) -> bool:
    if not stripped:
        return False
    if stripped.startswith(";"):
        return False
    if re.match(r"^[A-Za-z0-9_.%-]+:\s*(;.*)?$", stripped):
        return False
    return True


def extract_opcode(rhs: str) -> str:
    tokens = rhs.split()
    modifiers = {
        "tail",
        "musttail",
        "notail",
        "fast",
        "nnan",
        "ninf",
        "nsz",
        "arcp",
        "contract",
        "afn",
        "reassoc",
        "nuw",
        "nsw",
        "exact",
        "inbounds",
        "volatile",
        "atomic",
    }
    for token in tokens:
        if token in modifiers:
            continue
        return token
    return tokens[0] if tokens else ""


def parse_metadata_line(line: str) -> dict[str, str] | None:
    match = re.match(r"^!(\d+)\s*=\s*(?:distinct\s+)?!(\w+)\((.*)\)$", line)
    if not match:
        return None
    meta_id, kind, body = match.groups()
    data = {"id": meta_id, "kind": kind, "body": body}
    for key in ["filename", "directory", "name", "line", "column"]:
        string_match = re.search(rf"{key}: \"([^\"]*)\"", body)
        if string_match:
            data[key] = string_match.group(1)
        else:
            number_match = re.search(rf"{key}: (-?\d+)", body)
            if number_match:
                data[key] = number_match.group(1)
    for key in ["file", "scope", "inlinedAt"]:
        ref_match = re.search(rf"{key}: !(\d+)", body)
        if ref_match:
            data[key] = ref_match.group(1)
    return data


def build_relation_inventory(rel_dir: Path) -> list[dict[str, str]]:
    rows = []
    for path in sorted(rel_dir.glob("*.csv.gz")):
        row_count = 0
        column_count = 0
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line:
                    continue
                row_count += 1
                if column_count == 0:
                    column_count = len(line.split("\t"))
        rows.append(
            {
                "relation_file": path.name,
                "relation_name": path.name.removesuffix(".csv.gz"),
                "rows": str(row_count),
                "columns": str(column_count),
            }
        )
    return rows


def build_relation_anchor_rows(relation_inventory: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for rel in relation_inventory:
        name = rel["relation_name"]
        primary = "unknown"
        secondary = ""
        notes = ""
        if name in {"instr_pos", "instr_func", "instr_assigns_to", "call_instr", "load_instr", "store_instr", "alloca_instr", "phi_instr", "getelementptr_instr"}:
            primary = "instruction"
        elif name == "subset.callgraph.callgraph_edge":
            primary = "instruction"
            secondary = "function"
            notes = "caller call instruction + callee function"
        elif name in {"subset.var_points_to", "subset.operand_points_to"}:
            primary = "variable_or_operand"
            secondary = "allocation"
        elif name == "subset.ptr_points_to":
            primary = "allocation"
            secondary = "allocation"
        elif name == "subset_lift.allocation_by_instr_ctx":
            primary = "instruction"
            secondary = "allocation"
        elif name.startswith("phi_instr_pair_"):
            primary = "instruction"
            secondary = "value_or_block"
        elif name.startswith("variable_has_debug_"):
            primary = "variable"
        rows.append(
            {
                "relation_name": name,
                "primary_anchor_type": primary,
                "secondary_anchor_type": secondary,
                "notes": notes,
            }
        )
    return rows


def build_relation_schema_rows(relation_inventory: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for rel in relation_inventory:
        name = rel["relation_name"]
        schema_hint = ""
        if name == "instr_pos":
            schema_hint = "instruction,line,column"
        elif name == "instr_func":
            schema_hint = "instruction,function"
        elif name == "instr_assigns_to":
            schema_hint = "instruction,variable"
        elif name == "subset.callgraph.callgraph_edge":
            schema_hint = "callee_ctx,callee,caller_ctx,caller_instr"
        elif name == "subset.var_points_to":
            schema_hint = "alloc_ctx,alloc,var_ctx,variable"
        elif name == "subset.ptr_points_to":
            schema_hint = "alloc_ctx,alloc,ptr_ctx,ptr"
        elif name == "subset_lift.allocation_by_instr_ctx":
            schema_hint = "ctx,instruction,alloc_ctx,allocation"
        elif name == "phi_instr_pair_value":
            schema_hint = "phi,pair_index,value"
        elif name == "phi_instr_pair_label":
            schema_hint = "phi,pair_index,label"
        rows.append({"relation_name": name, "columns": rel["columns"], "schema_hint": schema_hint})
    return rows


def load_instr_pos(path: Path) -> dict[str, tuple[str, str]]:
    data: dict[str, tuple[str, str]] = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for raw_line in fh:
            raw_row = raw_line.rstrip("\n")
            if not raw_row:
                continue
            row = raw_row.split("\t")
            if len(row) >= 3:
                data[row[0]] = (row[1], row[2])
    return data


def load_key_value_relation(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for raw_line in fh:
            raw_row = raw_line.rstrip("\n")
            if not raw_row:
                continue
            row = raw_row.split("\t")
            if len(row) >= 2:
                data[row[0]] = row[1]
    return data


def load_relation_rows(path: Path) -> list[dict[str, object]]:
    relation_name = path.name.removesuffix(".csv.gz")
    rows: list[dict[str, object]] = []
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for row_number, raw_line in enumerate(fh, start=1):
            raw_row = raw_line.rstrip("\n")
            if not raw_row:
                continue
            row = raw_row.split("\t")
            rows.append(
                {
                    "relation_file": path.name,
                    "relation_name": relation_name,
                    "row_number": row_number,
                    "raw_row": raw_row,
                    "row_hash": hashlib.sha1(raw_row.encode("utf-8")).hexdigest(),
                    "row": row,
                }
            )
    return rows


def build_points_to_indexes_from_path(
    path: Path,
) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    by_var: dict[str, set[str]] = defaultdict(set)
    by_alloc: dict[str, set[str]] = defaultdict(set)
    rep_by_var: dict[str, dict[str, object]] = {}
    rep_by_alloc: dict[str, dict[str, object]] = {}
    relation_name = path.name.removesuffix(".csv.gz")
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for row_number, raw_line in enumerate(fh, start=1):
            raw_row = raw_line.rstrip("\n")
            if not raw_row:
                continue
            row = raw_row.split("\t")
            if len(row) < 4:
                continue
            alloc = str(row[1])
            var = str(row[3])
            entry = {
                "relation_file": path.name,
                "relation_name": relation_name,
                "row_number": row_number,
                "raw_row": raw_row,
                "row_hash": hashlib.sha1(raw_row.encode("utf-8")).hexdigest(),
                "row": row,
            }
            by_var[var].add(alloc)
            by_alloc[alloc].add(var)
            rep_by_var.setdefault(var, entry)
            rep_by_alloc.setdefault(alloc, entry)
    return by_var, by_alloc, rep_by_var, rep_by_alloc


def load_instr_assigns_for_vars(path: Path, interesting_vars: set[str]) -> dict[str, str]:
    by_var: dict[str, str] = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for raw_line in fh:
            raw_row = raw_line.rstrip("\n")
            if not raw_row:
                continue
            row = raw_row.split("\t")
            if len(row) < 2:
                continue
            instr_id, var_id = row[0], row[1]
            if var_id in interesting_vars:
                by_var[var_id] = instr_id
    return by_var


def build_ptr_points_index(rows: list[dict[str, object]]) -> dict[str, set[str]]:
    by_ptr: dict[str, set[str]] = defaultdict(set)
    for entry in rows:
        row = entry["row"]
        if len(row) >= 4:
            by_ptr[str(row[3])].add(str(row[1]))
    return by_ptr


def build_allocation_origin_index(rows: list[dict[str, object]]) -> dict[str, str]:
    index: dict[str, str] = {}
    for entry in rows:
        row = entry["row"]
        if len(row) >= 4:
            instr = str(row[1])
            alloc = str(row[3])
            index.setdefault(alloc, instr)
    return index


def build_phi_pair_index(rows: list[dict[str, object]]) -> dict[str, list[tuple[str, str]]]:
    data: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for entry in rows:
        row = entry["row"]
        if len(row) >= 3:
            data[str(row[0])].append((str(row[1]), str(row[2])))
    return data


def build_callgraph_index(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    data: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in rows:
        row = entry["row"]
        if len(row) >= 4:
            data[str(row[3])].append(entry)
    return data


def map_instruction_record(
    record: InstructionRecord,
    instr_pos: dict[str, tuple[str, str]],
    metadata: dict[str, dict[str, str]],
    source_index: dict[str, list[Path]],
    source_cache: dict[str, list[str]],
    target_root: Path,
    context_lines: int,
) -> dict[str, str]:
    instr_id = record.instr_id
    debug_line, debug_column = instr_pos.get(instr_id, ("", ""))
    source_file = ""
    line = ""
    column = ""
    inline_stack = ""
    source_line_text = ""
    source_context = ""
    mapping_status = "Unknown"
    if record:
        dbg_loc = resolve_dilocation(record.dbg_id, metadata, source_index, target_root)
        if dbg_loc:
            source_file = dbg_loc["source_file"]
            line = dbg_loc["line"]
            column = dbg_loc["column"]
            inline_stack = dbg_loc["inline_stack"]
    if debug_line == "0" and debug_column == "0":
        mapping_status = "NoDebugLoc"
    elif not source_file:
        mapping_status = "SourceFileMissing"
    else:
        source_line_text, source_context = load_source_context(
            source_file=source_file,
            line=line,
            column=column,
            source_cache=source_cache,
            target_root=target_root,
            context_lines=context_lines,
        )
        source_path = Path(source_file)
        if not source_path.exists():
            mapping_status = "SourceFileMissing"
        else:
            lines = source_cache.setdefault(source_file, source_path.read_text(encoding="utf-8", errors="replace").splitlines())
            line_no = int(line or "0")
            col_no = int(column or "0")
            if line_no <= 0 or line_no > len(lines):
                mapping_status = "LineOutOfRange"
            elif col_no > 0 and col_no > len(source_line_text) + 1:
                mapping_status = "ColumnOutOfRange"
            elif col_no == 0:
                mapping_status = "MappedLineOnly"
            else:
                mapping_status = "MappedExact"
    return {
        "instr_id": instr_id,
        "function_id": record.function,
        "ir_opcode": record.opcode,
        "ir_result_variable": record.result_var,
        "ir_snippet": record.text,
        "debug_line": debug_line,
        "debug_column": debug_column,
        "source_file": source_file,
        "line": line,
        "column": column,
        "inline_stack": inline_stack,
        "source_line_text": source_line_text,
        "source_context": source_context,
        "mapping_status": mapping_status,
    }


def load_source_context(
    source_file: str,
    line: str,
    column: str,
    source_cache: dict[str, list[str]],
    target_root: Path,
    context_lines: int,
) -> tuple[str, str]:
    if not source_file:
        return "", ""
    source_path = Path(source_file)
    if not source_path.exists():
        return "", ""
    lines = source_cache.setdefault(source_file, source_path.read_text(encoding="utf-8", errors="replace").splitlines())
    line_no = int(line or "0")
    if line_no <= 0 or line_no > len(lines):
        return "", ""
    source_line_text = lines[line_no - 1]
    start = max(1, line_no - context_lines)
    end = min(len(lines), line_no + context_lines)
    context_parts = []
    for idx in range(start, end + 1):
        prefix = ">>" if idx == line_no else "  "
        context_parts.append(f"{prefix} {idx}: {lines[idx - 1]}")
    return source_line_text, "\\n".join(context_parts)


def resolve_dilocation(
    dbg_id: str | None,
    metadata: dict[str, dict[str, str]],
    source_index: dict[str, list[Path]],
    target_root: Path,
) -> dict[str, str] | None:
    if not dbg_id or dbg_id not in metadata:
        return None
    meta = metadata[dbg_id]
    if meta.get("kind") != "DILocation":
        return None
    line = meta.get("line", "")
    column = meta.get("column", "")
    source_file = resolve_scope_file(meta.get("scope", ""), metadata, source_index, target_root)
    inline_stack = format_inline_stack(meta.get("inlinedAt", ""), metadata, source_index, target_root)
    return {
        "line": line,
        "column": column,
        "source_file": source_file,
        "inline_stack": inline_stack,
    }


def resolve_scope_file(scope_id: str, metadata: dict[str, dict[str, str]], source_index: dict[str, list[Path]], target_root: Path) -> str:
    seen: set[str] = set()
    current = scope_id
    while current and current not in seen:
        seen.add(current)
        meta = metadata.get(current, {})
        kind = meta.get("kind", "")
        file_ref = meta.get("file", "")
        if kind == "DISubprogram" and file_ref:
            return resolve_difile(file_ref, metadata, source_index, target_root)
        if kind in {"DILexicalBlock", "DILexicalBlockFile"}:
            if file_ref:
                resolved = resolve_difile(file_ref, metadata, source_index, target_root)
                if resolved:
                    return resolved
            current = meta.get("scope", "")
            continue
        current = meta.get("scope", "")
    return ""


def resolve_difile(file_id: str, metadata: dict[str, dict[str, str]], source_index: dict[str, list[Path]], target_root: Path) -> str:
    meta = metadata.get(file_id, {})
    filename = meta.get("filename", "")
    directory = meta.get("directory", "")
    if not filename:
        return ""
    raw = Path(filename if filename.startswith("/") else str(Path(directory) / filename))
    candidates = []
    raw_str = str(raw)

    # Prefer the canonical target source tree over stale rebuild/work paths that
    # may still exist from other analyzer runs.
    if "/src/" in raw_str:
        suffix = raw_str.split("/src/", 1)[1]
        candidate = target_root / "src" / suffix
        if candidate.exists():
            candidates.append(candidate)
    basename = Path(filename).name
    for candidate in source_index.get(basename, []):
        if is_under(candidate, target_root):
            candidates.append(candidate)
    replaced = raw_str.replace("/work/PaperExperiment", str(REPO_ROOT))
    if replaced != raw_str:
        replaced_path = Path(replaced)
        if replaced_path.exists():
            candidates.append(replaced_path)
    if raw.exists():
        candidates.append(raw)
    for candidate in source_index.get(basename, []):
        candidates.append(candidate)
    if candidates:
        return str(dedup_paths(candidates)[0])
    return replaced


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def dedup_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    result = []
    for path in paths:
        text = str(path.resolve() if path.exists() else path)
        if text in seen:
            continue
        seen.add(text)
        result.append(Path(text))
    return result


def format_inline_stack(inlined_at: str, metadata: dict[str, dict[str, str]], source_index: dict[str, list[Path]], target_root: Path) -> str:
    if not inlined_at:
        return ""
    parts = []
    current = inlined_at
    seen: set[str] = set()
    while current and current not in seen:
        seen.add(current)
        meta = metadata.get(current, {})
        if meta.get("kind") != "DILocation":
            break
        source_file = resolve_scope_file(meta.get("scope", ""), metadata, source_index, target_root)
        parts.append(f"{Path(source_file).name if source_file else '?'}:{meta.get('line', '')}:{meta.get('column', '')}")
        current = meta.get("inlinedAt", "")
    return " <- ".join(parts)


def build_ir_instruction_index_rows(records: dict[str, InstructionRecord]) -> list[dict[str, str]]:
    rows = []
    for instr_id in sorted(records):
        rec = records[instr_id]
        rows.append(
            {
                "instr_id": instr_id,
                "function_id": rec.function,
                "ll_line_no": str(rec.ll_line_no),
                "opcode": rec.opcode,
                "result_var": rec.result_var,
                "dbg_id": rec.dbg_id or "",
                "text": rec.text,
            }
        )
    return rows


def build_ir_function_index_rows(records: dict[str, FunctionRecord]) -> list[dict[str, str]]:
    rows = []
    for func in sorted(records):
        rec = records[func]
        rows.append({"function_id": func, "dbg_id": rec.dbg_id or "", "start_line": str(rec.start_line)})
    return rows


def build_ir_debug_index_rows(metadata: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for meta_id in sorted(metadata, key=lambda x: int(x)):
        meta = metadata[meta_id]
        rows.append(
            {
                "metadata_id": meta_id,
                "kind": meta.get("kind", ""),
                "line": meta.get("line", ""),
                "column": meta.get("column", ""),
                "file_ref": meta.get("file", ""),
                "scope_ref": meta.get("scope", ""),
                "inlined_at_ref": meta.get("inlinedAt", ""),
            }
        )
    return rows


@lru_cache(maxsize=None)
def demangle_function(name: str) -> str:
    if not name:
        return ""
    proc = subprocess.run(["/usr/bin/c++filt", name], capture_output=True, text=True, check=False)
    text = proc.stdout.strip()
    return text or name


def first_relation_row_for_value(rows: list[dict[str, object]], value: str, column: int = 3) -> dict[str, object] | None:
    for entry in rows:
        row = entry["row"]
        if len(row) > column and str(row[column]) == value:
            return entry
    return None


def is_callsite_mismatch(source_line: str, source_context: str, demangled_callee: str) -> bool:
    if not source_line:
        return False
    normalized = source_line.strip()
    low = normalized.lower()
    if "(" not in normalized:
        return True
    callee_hint = demangled_callee.split("(")[0].split("::")[-1].strip("~")
    if callee_hint and callee_hint in normalized:
        return False
    if any(token in low for token in ["assert", "calloc", "malloc", "realloc", "free", "exit", "return", "for", "while", "if", "switch"]):
        return False
    if re.search(r"[A-Za-z_][A-Za-z0-9_]*\s*\(", normalized):
        return False
    return True


def is_allocation_semantics_mismatch(source_line: str, source_context: str, opcode: str) -> bool:
    if not source_line:
        return False
    text = f"{source_line}\n{source_context}".lower()
    if any(token in text for token in ["malloc", "calloc", "realloc", "free", "alloc", "new ", "size_t ", "unsigned ", "char ", "int ", "double ", "struct ", "array"]):
        return False
    if opcode == "alloca" and re.search(r"\b(size_t|int|char|double|struct|unsigned)\b", source_line):
        return False
    return True


def is_phi_merge_mismatch(source_line: str, source_context: str, debug_names: list[str], incoming_count: int) -> bool:
    if not source_line:
        return False
    text = f"{source_line}\n{source_context}"
    low = text.lower()
    if any(keyword in low for keyword in ["if", "else", "for", "while", "switch", "case", "?:"]):
        return False
    for name in debug_names:
        if name and name in text:
            return False
    return incoming_count >= 2


def override_mapping_status(mapping: dict[str, str], status: str) -> dict[str, str]:
    updated = dict(mapping)
    updated["mapping_status"] = status
    return updated


def priority_rank(priority: str) -> int:
    return {"P0": 0, "P1": 1, "P2": 2}.get(priority, 9)


def write_case_evidence(value_root: Path, case_id: str, mapping: dict[str, str], raw_row: str, evidence_suffix: str) -> list[str]:
    paths = []
    source_path = value_root / "snippets" / f"{case_id}.source.txt"
    ir_path = value_root / "snippets" / f"{case_id}.ir.txt"
    raw_path = value_root / "snippets" / f"{case_id}.row.txt"
    if not source_path.exists():
        source_path.write_text(mapping.get("source_context", "") + "\n", encoding="utf-8")
    if not ir_path.exists():
        ir_path.write_text(mapping.get("ir_snippet", "") + "\n", encoding="utf-8")
    if not raw_path.exists():
        raw_path.write_text(raw_row + "\n", encoding="utf-8")
    paths.extend([str(source_path), str(ir_path), str(raw_path)])
    return paths


def write_case_markdown(path: Path, row: dict[str, str]) -> None:
    if path.exists():
        return
    text = (
        f"# {row['case_id']}\n\n"
        f"- phenomenon_label: {row['phenomenon_label']}\n"
        f"- case_kind: {row['case_kind']}\n"
        f"- priority: {row['priority']}\n"
        f"- relation: {row['relation_name']}\n"
        f"- anchor: {row['anchor_type']} {row['anchor_id']}\n"
        f"- function: {row['demangled_function'] or row['function_id']}\n"
        f"- source: {row['source_file']}:{row['line']}:{row['column']}\n"
        f"- mapping_status: {row['mapping_status']}\n"
        f"- root_cause_hint: {row['root_cause_hint']}\n\n"
        f"## Source\n\n```\n{row['source_context']}\n```\n\n"
        f"## IR\n\n```\n{row['ir_snippet']}\n```\n\n"
        f"## Raw Relation Row\n\n```\n{row['raw_row']}\n```\n"
    )
    path.write_text(text, encoding="utf-8")


def write_report(path: Path, manifest: dict[str, object], relation_inventory: list[dict[str, str]], cases: list[dict[str, str]]) -> None:
    counts = Counter(row["phenomenon_label"] for row in cases)
    priorities = Counter(row["priority"] for row in cases)
    mapping_status = Counter(row["mapping_status"] for row in cases)
    lines = [
        f"# {manifest['target']} cclyzer++ Value Case Analysis",
        "",
        "## Summary",
        f"- target: {manifest['target']}",
        f"- run_dir: {manifest['run_dir']}",
        f"- input_bc: {manifest['input_bc']}",
        f"- input_ll: {manifest['input_ll']}",
        f"- relation_file_count: {manifest['relation_file_count']}",
        f"- case_count: {manifest['case_count']}",
        "",
        "## Cases by Phenomenon",
    ]
    for key, value in sorted(counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Cases by Priority"])
    for key, value in sorted(priorities.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Mapping Status"])
    for key, value in sorted(mapping_status.items()):
        lines.append(f"- {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@contextmanager
def open_tsv_writer(path: Path, fieldnames: list[str]) -> Iterable[csv.DictWriter]:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        yield writer


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    main()
