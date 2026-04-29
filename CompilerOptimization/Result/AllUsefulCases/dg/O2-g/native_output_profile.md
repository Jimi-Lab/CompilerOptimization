# DG Native Output Profile

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
