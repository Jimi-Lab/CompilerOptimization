# SeaHorn Native Output Profile

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
