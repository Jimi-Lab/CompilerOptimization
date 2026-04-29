#!/usr/bin/env python3

import hashlib
import re
import shlex
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: generate_bc_from_make_dryrun.py <o2dir> <srcdir> <dryrun_relpath> <bc_list_relpath>",
            file=sys.stderr,
        )
        return 2

    o2dir = Path(sys.argv[1])
    srcdir = Path(sys.argv[2])
    dryrun = o2dir / sys.argv[3]
    list_path = o2dir / sys.argv[4]
    objdir = o2dir / "artifacts" / "bc_objs"

    text = dryrun.read_text(encoding="utf-8", errors="ignore").splitlines()
    clang_frag_re = re.compile(r"(?:^|;)\s*(?:/usr/bin/)?clang(?:\+\+)?-?16\b[^;]*\s-c\s[^;]*")
    link_frag_re = re.compile(r"(?:^|;)\s*(?:/usr/bin/)?clang(?:\+\+)?-?16\b[^;]*\s-o\s+[^;]+")

    link_objs = []
    for line in text:
        for m in link_frag_re.finditer(line):
            frag = m.group(0).lstrip(";").strip()
            try:
                toks = shlex.split(frag)
            except Exception:
                continue
            objs = [Path(t).name for t in toks if t.endswith(".o")]
            if objs:
                link_objs.append(objs)

    selected_obj_set = set(max(link_objs, key=len)) if link_objs else None

    exclude_marks = (
        "/test/",
        "/tests/",
        "/benchmark/",
        "/bench/",
        "/examples/",
        "/example/",
        "/docs/",
        "/fuzz/",
    )
    seen_src = set()
    outs = []

    for i, line in enumerate(text):
        for m in clang_frag_re.finditer(line):
            frag = m.group(0).lstrip(";").strip()
            try:
                toks = shlex.split(frag)
            except Exception:
                continue

            out_obj = None
            for j, t in enumerate(toks):
                if t == "-o" and j + 1 < len(toks):
                    out_obj = Path(toks[j + 1]).name
                    break
                if t.startswith("-o") and t != "-o":
                    out_obj = Path(t[2:]).name
                    break

            if selected_obj_set and out_obj and out_obj not in selected_obj_set:
                continue

            src = None
            for t in reversed(toks):
                if t.endswith((".c", ".cc", ".cpp", ".cxx")):
                    src = t
                    break
            if not src:
                continue

            src_abs = str((srcdir / src).resolve()) if not Path(src).is_absolute() else str(Path(src).resolve())
            lsrc = src_abs.lower()
            if any(m in lsrc for m in exclude_marks):
                continue
            if src_abs in seen_src:
                continue
            seen_src.add(src_abs)

            out_bc = objdir / (hashlib.sha1((str(i) + "|" + src_abs).encode()).hexdigest()[:16] + ".bc")

            new = []
            skip = False
            for t in toks:
                if skip:
                    skip = False
                    continue
                if t == "-o":
                    skip = True
                    continue
                if t.startswith("-o") and t != "-o":
                    continue
                if t in ("-MMD", "-MD"):
                    continue
                if t in ("-MF", "-MT", "-MQ"):
                    skip = True
                    continue
                new.append(t)

            if "-c" not in new:
                new.append("-c")
            new.extend(["-emit-llvm", "-o", str(out_bc)])

            try:
                subprocess.run(new, cwd=srcdir, check=True)
                outs.append(str(out_bc))
            except subprocess.CalledProcessError:
                pass

    with list_path.open("w") as f:
        for p in outs:
            f.write(p + "\n")

    print("dryrun_lines", len(text))
    print("selected_obj_count", len(selected_obj_set) if selected_obj_set else 0)
    print("selected_sources", len(seen_src))
    print("generated_bc", len(outs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
