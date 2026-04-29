# Phasar Native Output Profile

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
