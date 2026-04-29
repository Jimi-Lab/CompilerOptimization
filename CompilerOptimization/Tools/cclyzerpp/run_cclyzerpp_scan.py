#!/usr/bin/env python3
"""Run cclyzer++ on LLVM bitcode and extract paper-friendly candidates.

cclyzer++ is a pointer-analysis engine, not a CWE bug checker. This wrapper
keeps the raw Datalog relations and derives high-volume candidate reports that
are useful for manual case hunting: broad points-to sets, callgraph fanout,
large alias buckets, phi-heavy sites, tail-call sites, and missing debug
locations.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import os
import re
import shlex
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


WORK_ROOT = Path("/home/jimi/PaperExperiment")
DEFAULT_TOOL_ROOT = WORK_ROOT / "CompilerOptimization/Tools/cclyzerpp/cclyzerpp"
DEFAULT_IMAGE = "ghcr.io/galoisinc/cclyzerpp-dev:main"


@dataclass(frozen=True)
class Job:
    target: str
    universe: str
    input_bc: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run cclyzer++ over one or more .bc files and summarize candidate reports."
    )
    parser.add_argument("--target", help="Target name for a single --input-bc run.")
    parser.add_argument("--universe", help="Compilation universe label, e.g. LLVM14-O2-g.")
    parser.add_argument("--input-bc", action="append", help="Input LLVM bitcode path. May repeat.")
    parser.add_argument(
        "--input-list",
        help="TSV manifest with columns: target, universe, input_bc. Header is optional.",
    )
    parser.add_argument("--result-root", default=str(WORK_ROOT / "CompilerOptimization/Result"))
    parser.add_argument("--tool-root", default=str(DEFAULT_TOOL_ROOT))
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--analysis", default="subset", choices=["subset", "debug", "unification"])
    parser.add_argument("--context-sensitivity", default="insensitive")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--pt-threshold", type=int, default=20)
    parser.add_argument("--ptr-threshold", type=int, default=20)
    parser.add_argument("--alias-threshold", type=int, default=25)
    parser.add_argument("--call-fanout-threshold", type=int, default=5)
    parser.add_argument("--phi-threshold", type=int, default=4)
    parser.add_argument("--max-candidates-per-kind", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def die(message: str) -> None:
    print(f"[ERR] {message}", file=sys.stderr)
    raise SystemExit(2)


def host_to_container(path: Path) -> str:
    path = path.resolve()
    try:
        return "/work/" + str(path.relative_to(WORK_ROOT))
    except ValueError:
        die(f"path is outside {WORK_ROOT}: {path}")


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]+", "_", text)[:80]


def load_jobs(args: argparse.Namespace) -> list[Job]:
    jobs: list[Job] = []
    if args.input_list:
        with open(args.input_list, newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh, delimiter="\t"))
        for row in rows:
            if not row or row[0].startswith("#"):
                continue
            if row[:3] == ["target", "universe", "input_bc"]:
                continue
            if len(row) < 3:
                die(f"bad manifest row: {row}")
            jobs.append(Job(row[0], row[1], Path(row[2]).resolve()))

    if args.input_bc:
        if not args.target or not args.universe:
            die("--target and --universe are required with --input-bc")
        for input_bc in args.input_bc:
            jobs.append(Job(args.target, args.universe, Path(input_bc).resolve()))

    if not jobs:
        die("provide --input-bc or --input-list")

    for job in jobs:
        if not job.input_bc.exists():
            die(f"missing input bitcode: {job.input_bc}")
        if job.input_bc.suffix != ".bc":
            die(f"expected .bc input: {job.input_bc}")
    return jobs


def relation_path(rel_dir: Path, name: str) -> Path:
    gz = rel_dir / f"{name}.csv.gz"
    if gz.exists():
        return gz
    plain = rel_dir / f"{name}.csv"
    return plain


def read_relation(rel_dir: Path, name: str) -> Iterable[list[str]]:
    path = relation_path(rel_dir, name)
    if not path.exists():
        return []

    def rows() -> Iterable[list[str]]:
        if path.suffix == ".gz":
            fh = gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="")
        else:
            fh = open(path, newline="", encoding="utf-8", errors="replace")
        try:
            with fh:
                for row in csv.reader(fh, delimiter="\t"):
                    if row:
                        yield row
        except (EOFError, gzip.BadGzipFile, OSError, UnicodeDecodeError):
            return

    return rows()


def count_relation_lines(path: Path) -> int:
    opener = gzip.open if path.suffix == ".gz" else open
    mode = "rt"
    count = 0
    try:
        with opener(path, mode, encoding="utf-8", errors="replace") as fh:
            for _ in fh:
                count += 1
    except (EOFError, gzip.BadGzipFile, OSError, UnicodeDecodeError):
        return count
    return count


def parse_entity(entity: str) -> tuple[str, str]:
    match = re.match(r"^<([^>]+)>:([^:]+)", entity)
    if match:
        return match.group(1), match.group(2)
    return "NA", "NA"


def build_indexes(rel_dir: Path) -> dict[str, dict[str, tuple[str, ...] | str]]:
    instr_pos: dict[str, tuple[str, str]] = {}
    instr_func: dict[str, str] = {}
    func_name: dict[str, str] = {}
    var_name: dict[str, str] = {}
    var_debug_name: dict[str, str] = {}
    var_debug_pos: dict[str, tuple[str, str]] = {}

    for row in read_relation(rel_dir, "instr_pos"):
        if len(row) >= 3:
            instr_pos[row[0]] = (row[1], row[2])
    for row in read_relation(rel_dir, "instr_func"):
        if len(row) >= 2:
            instr_func[row[0]] = row[1]
    for row in read_relation(rel_dir, "func_name"):
        if len(row) >= 2:
            func_name[row[0]] = row[1]
    for row in read_relation(rel_dir, "variable_has_name"):
        if len(row) >= 2:
            var_name[row[0]] = row[1]
    for row in read_relation(rel_dir, "variable_has_debug_source_name"):
        if len(row) >= 2:
            var_debug_name[row[0]] = row[1]
    for row in read_relation(rel_dir, "variable_has_debug_decl_pos"):
        if len(row) >= 3:
            var_debug_pos[row[0]] = (row[1], row[2])

    return {
        "instr_pos": instr_pos,
        "instr_func": instr_func,
        "func_name": func_name,
        "var_name": var_name,
        "var_debug_name": var_debug_name,
        "var_debug_pos": var_debug_pos,
    }


def instr_location(indexes: dict[str, dict[str, tuple[str, ...] | str]], instr: str) -> tuple[str, str, str, str]:
    instr_pos = indexes["instr_pos"]
    instr_func = indexes["instr_func"]
    func_name = indexes["func_name"]
    file_guess, func_guess = parse_entity(instr)
    line, col = instr_pos.get(instr, ("0", "0"))  # type: ignore[arg-type]
    func_id = instr_func.get(instr)
    function = func_name.get(func_id, func_guess) if isinstance(func_id, str) else func_guess
    return file_guess, line, col, str(function)


def var_location(indexes: dict[str, dict[str, tuple[str, ...] | str]], var: str) -> tuple[str, str, str, str, str]:
    var_name = indexes["var_name"].get(var, "")
    debug_name = indexes["var_debug_name"].get(var, "")
    display = str(debug_name or var_name or var)
    file_guess, func_guess = parse_entity(var)
    line, col = indexes["var_debug_pos"].get(var, ("0", "0"))  # type: ignore[arg-type]
    return file_guess, line, col, func_guess, display


def add_candidate(
    out: list[dict[str, str]],
    target: str,
    universe: str,
    input_bc: Path,
    run_dir: Path,
    kind: str,
    subject: str,
    file_: str,
    line: str,
    col: str,
    function: str,
    metric: int,
    detail: str,
    evidence_relation: str,
) -> None:
    out.append(
        {
            "target": target,
            "universe": universe,
            "input_bc": str(input_bc),
            "kind": kind,
            "subject": subject,
            "file": file_,
            "line": line,
            "col": col,
            "function": function,
            "metric": str(metric),
            "detail": detail,
            "evidence_relation": evidence_relation,
            "run_dir": str(run_dir),
        }
    )


def derive_candidates(
    job: Job,
    run_dir: Path,
    rel_dir: Path,
    args: argparse.Namespace,
) -> list[dict[str, str]]:
    indexes = build_indexes(rel_dir)
    candidates: list[dict[str, str]] = []
    per_kind = Counter()

    def allowed(kind: str) -> bool:
        return per_kind[kind] < args.max_candidates_per_kind

    call_targets: dict[str, set[str]] = defaultdict(set)
    for row in read_relation(rel_dir, "subset.callgraph.callgraph_edge"):
        if len(row) >= 4:
            call_targets[row[3]].add(row[1])
    for instr, callees in sorted(call_targets.items(), key=lambda item: -len(item[1])):
        kind = "CallgraphFanout"
        if len(callees) < args.call_fanout_threshold or not allowed(kind):
            continue
        file_, line, col, function = instr_location(indexes, instr)
        add_candidate(
            candidates,
            job.target,
            job.universe,
            job.input_bc,
            run_dir,
            kind,
            instr,
            file_,
            line,
            col,
            function,
            len(callees),
            "many possible callees; useful for indirect-call / devirtualization drift review",
            "subset.callgraph.callgraph_edge",
        )
        per_kind[kind] += 1

    var_allocs: dict[str, set[str]] = defaultdict(set)
    alloc_vars: dict[str, set[str]] = defaultdict(set)
    for row in read_relation(rel_dir, "subset.var_points_to"):
        if len(row) >= 4:
            alloc = row[1]
            var = row[3]
            if "null" in alloc.lower():
                continue
            var_allocs[var].add(alloc)
            alloc_vars[alloc].add(var)
    for var, allocs in sorted(var_allocs.items(), key=lambda item: -len(item[1])):
        kind = "PointsToFanout"
        if len(allocs) < args.pt_threshold or not allowed(kind):
            continue
        file_, line, col, function, display = var_location(indexes, var)
        add_candidate(
            candidates,
            job.target,
            job.universe,
            job.input_bc,
            run_dir,
            kind,
            display,
            file_,
            line,
            col,
            function,
            len(allocs),
            "variable has a broad points-to set; candidate over-approximation / phi merge",
            "subset.var_points_to",
        )
        per_kind[kind] += 1

    for alloc, vars_ in sorted(alloc_vars.items(), key=lambda item: -len(item[1])):
        kind = "AliasBucketFanout"
        if len(vars_) < args.alias_threshold or not allowed(kind):
            continue
        file_, function = parse_entity(alloc)
        add_candidate(
            candidates,
            job.target,
            job.universe,
            job.input_bc,
            run_dir,
            kind,
            alloc,
            file_,
            "0",
            "0",
            function,
            len(vars_),
            "one allocation reaches many variables; candidate alias collapse hotspot",
            "subset.var_points_to",
        )
        per_kind[kind] += 1

    ptr_allocs: dict[str, set[str]] = defaultdict(set)
    for row in read_relation(rel_dir, "subset.ptr_points_to"):
        if len(row) >= 4:
            ptr_allocs[row[3]].add(row[1])
    for ptr, allocs in sorted(ptr_allocs.items(), key=lambda item: -len(item[1])):
        kind = "PointerObjectFanout"
        if ptr in {"*unknown*", "*null*"} or len(allocs) < args.ptr_threshold or not allowed(kind):
            continue
        file_, function = parse_entity(ptr)
        add_candidate(
            candidates,
            job.target,
            job.universe,
            job.input_bc,
            run_dir,
            kind,
            ptr,
            file_,
            "0",
            "0",
            function,
            len(allocs),
            "memory object has a broad points-to set",
            "subset.ptr_points_to",
        )
        per_kind[kind] += 1

    for row in read_relation(rel_dir, "phi_instr_npairs"):
        if len(row) >= 2:
            try:
                n_pairs = int(row[1])
            except ValueError:
                continue
            kind = "PhiMergeHotspot"
            if n_pairs < args.phi_threshold or not allowed(kind):
                continue
            file_, line, col, function = instr_location(indexes, row[0])
            add_candidate(
                candidates,
                job.target,
                job.universe,
                job.input_bc,
                run_dir,
                kind,
                row[0],
                file_,
                line,
                col,
                function,
                n_pairs,
                "phi with many incoming values; candidate Mem2Reg/GVN merge site",
                "phi_instr_npairs",
            )
            per_kind[kind] += 1

    for row in read_relation(rel_dir, "call_instr_tail_opt"):
        if not row:
            continue
        kind = "TailCallSite"
        if not allowed(kind):
            continue
        file_, line, col, function = instr_location(indexes, row[0])
        add_candidate(
            candidates,
            job.target,
            job.universe,
            job.input_bc,
            run_dir,
            kind,
            row[0],
            file_,
            line,
            col,
            function,
            1,
            "tail call in optimized IR; candidate call/return stack mismatch review",
            "call_instr_tail_opt",
        )
        per_kind[kind] += 1

    pos = indexes["instr_pos"]
    for row in read_relation(rel_dir, "instr_func"):
        if len(row) < 2:
            continue
        instr = row[0]
        line_col = pos.get(instr)
        if line_col and line_col != ("0", "0"):
            continue
        kind = "MissingDebugLoc"
        if not allowed(kind):
            continue
        file_, line, col, function = instr_location(indexes, instr)
        add_candidate(
            candidates,
            job.target,
            job.universe,
            job.input_bc,
            run_dir,
            kind,
            instr,
            file_,
            line,
            col,
            function,
            1,
            "instruction has no usable source location; candidate DWARF drift / optimized-debug loss",
            "instr_func/instr_pos",
        )
        per_kind[kind] += 1

    return candidates


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(
    job: Job,
    run_dir: Path,
    args: argparse.Namespace,
    status: str,
    return_code: int,
    elapsed: int,
    command: list[str],
    candidates: list[dict[str, str]],
    relation_counts: list[dict[str, str]],
) -> None:
    final_report = run_dir / "report/final_report.md"
    counts = Counter(row["kind"] for row in candidates)
    with open(final_report, "w", encoding="utf-8") as out:
        out.write("# cclyzer++ Scan Final Report\n\n")
        out.write("## Metadata\n")
        out.write(f"- target: {job.target}\n")
        out.write(f"- universe: {job.universe}\n")
        out.write(f"- input_bc: {job.input_bc}\n")
        out.write(f"- docker_image: {args.image}\n")
        out.write(f"- analysis: {args.analysis}\n")
        out.write(f"- context_sensitivity: {args.context_sensitivity}\n")
        out.write(f"- run_dir: {run_dir}\n")
        out.write(f"- status: {status}\n")
        out.write(f"- return_code: {return_code}\n")
        out.write(f"- elapsed_sec: {elapsed}\n\n")
        out.write("## Important Interpretation Note\n")
        out.write(
            "- cclyzer++ is a global pointer-analysis engine. Rows in `extract/candidates.tsv` are high-signal "
            "candidate anomalies for manual review, not verified CWE bug reports.\n"
        )
        out.write(
            "- Promote a row to a paper case only after O0/O2/O2-noinline comparison and source/IR inspection.\n\n"
        )
        out.write("## Candidate Counts\n")
        out.write("| kind | count |\n| --- | ---: |\n")
        for kind, count in counts.most_common():
            out.write(f"| {kind} | {count} |\n")
        out.write("\n## Top Candidates\n")
        out.write("| kind | metric | file | line | function | subject | detail |\n")
        out.write("| --- | ---: | --- | ---: | --- | --- | --- |\n")
        for row in sorted(candidates, key=lambda r: (-int(r["metric"]), r["kind"]))[:30]:
            subject = row["subject"].replace("|", "\\|")[:120]
            detail = row["detail"].replace("|", "\\|")
            out.write(
                f"| {row['kind']} | {row['metric']} | {row['file']} | {row['line']} | "
                f"{row['function']} | {subject} | {detail} |\n"
            )
        out.write("\n## Largest Relations\n")
        out.write("| relation | rows |\n| --- | ---: |\n")
        for row in sorted(relation_counts, key=lambda r: -int(r["rows"]))[:20]:
            out.write(f"| {row['relation']} | {row['rows']} |\n")
        out.write("\n## Command\n")
        out.write("```bash\n")
        out.write(shlex.join(command))
        out.write("\n```\n")


def run_job(job: Job, args: argparse.Namespace, batch_stamp: str, index: int, total: int) -> Path:
    result_root = Path(args.result_root).resolve()
    tool_root = Path(args.tool_root).resolve()
    stem = safe_name(job.input_bc.stem)
    suffix = f"_{stem}" if total > 1 else ""
    run_dir = result_root / job.target / "cclyzerpp" / job.universe / f"run_{batch_stamp}{suffix}"
    rel_dir = run_dir / "relations"
    log_dir = run_dir / "log"
    status_dir = run_dir / "status"
    extract_dir = run_dir / "extract"
    report_dir = run_dir / "report"
    command_dir = run_dir / "commands"
    for directory in [rel_dir, log_dir, status_dir, extract_dir, report_dir, command_dir]:
        directory.mkdir(parents=True, exist_ok=False)

    required = [tool_root / "build/libSoufflePA.so", tool_root / "build/libPAPass.so"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        die("missing cclyzer++ build artifact(s): " + ", ".join(missing))

    tool_cont = host_to_container(tool_root)
    bc_cont = host_to_container(job.input_bc)
    rel_cont = host_to_container(rel_dir)
    inner = (
        "set -euo pipefail; "
        "opt --disable-output -enable-new-pm=0 "
        "--load=build/libSoufflePA.so --load=build/libPAPass.so "
        "-cclyzer -debug-datalog=true "
        f"-debug-datalog-dir='{rel_cont}' "
        f"-context-sensitivity='{args.context_sensitivity}' "
        f"-datalog-analysis='{args.analysis}' "
        f"'{bc_cont}'"
    )
    command = [
        "timeout",
        "-s",
        "KILL",
        "-k",
        "5",
        str(args.timeout),
        "docker",
        "run",
        "--rm",
        "-v",
        f"{WORK_ROOT}:/work",
        "-w",
        tool_cont,
        "--entrypoint",
        "/bin/bash",
        args.image,
        "-lc",
        inner,
    ]
    (command_dir / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")
    with open(log_dir / "preflight.log", "w", encoding="utf-8") as out:
        out.write(f"target={job.target}\n")
        out.write(f"universe={job.universe}\n")
        out.write(f"input_bc={job.input_bc}\n")
        out.write(f"tool_root={tool_root}\n")
        out.write(f"image={args.image}\n")
        for path in required:
            out.write(f"tool_artifact={path} size={path.stat().st_size}\n")

    start = time.time()
    if args.dry_run:
        return_code = 0
        status = "dry-run"
    else:
        with open(log_dir / "cclyzerpp.log", "w", encoding="utf-8", errors="replace") as log:
            proc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
        return_code = proc.returncode
        if return_code == 0:
            status = "reported"
        elif return_code in {124, 137, -9}:
            status = "timeout"
        else:
            status = "tool failure"
    elapsed = int(time.time() - start)

    relation_counts: list[dict[str, str]] = []
    if rel_dir.exists():
        for path in sorted(rel_dir.glob("*.csv*")):
            relation = path.name
            relation = relation.removesuffix(".gz").removesuffix(".csv")
            relation_counts.append({"relation": relation, "rows": str(count_relation_lines(path))})
    write_tsv(extract_dir / "relation_counts.tsv", relation_counts, ["relation", "rows"])

    candidates: list[dict[str, str]] = []
    if status == "reported":
        candidates = derive_candidates(job, run_dir, rel_dir, args)
    candidate_fields = [
        "target",
        "universe",
        "input_bc",
        "kind",
        "subject",
        "file",
        "line",
        "col",
        "function",
        "metric",
        "detail",
        "evidence_relation",
        "run_dir",
    ]
    write_tsv(extract_dir / "candidates.tsv", candidates, candidate_fields)

    status_row = {
        "target": job.target,
        "universe": job.universe,
        "status": status,
        "return_code": str(return_code),
        "input_bc": str(job.input_bc),
        "run_dir": str(run_dir),
        "log_path": str(log_dir / "cclyzerpp.log"),
        "start_time": datetime.fromtimestamp(start).isoformat(),
        "end_time": datetime.now().isoformat(),
        "elapsed_sec": str(elapsed),
    }
    write_tsv(
        status_dir / "run_status.tsv",
        [status_row],
        [
            "target",
            "universe",
            "status",
            "return_code",
            "input_bc",
            "run_dir",
            "log_path",
            "start_time",
            "end_time",
            "elapsed_sec",
        ],
    )
    write_report(job, run_dir, args, status, return_code, elapsed, command, candidates, relation_counts)
    print(f"[{index}/{total}] {job.target} {job.universe} {status}: {run_dir}")
    return run_dir


def main() -> None:
    args = parse_args()
    jobs = load_jobs(args)
    batch_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dirs = []
    for idx, job in enumerate(jobs, start=1):
        run_dirs.append(run_job(job, args, batch_stamp, idx, len(jobs)))
    print("run_dirs:")
    for run_dir in run_dirs:
        print(run_dir)


if __name__ == "__main__":
    main()
