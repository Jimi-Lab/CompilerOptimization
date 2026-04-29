# All-target PhASAR run (`-O2 -g`)

This batch run scans all projects under `CompilerOptimization/Target` with:

- compiler flags: `-O2 -g` (no `RelWithDebInfo`, no `-DNDEBUG`)
- analysis: `ifds-uninit` only
- timeout policy: `IFDS_TIMEOUT_SEC` (default 420s)
- resume policy: skip projects that already have `status/success.marker`.

## Entry scripts

- Host runner: `run_all_targets_phasar_O2_g.sh`
- Container runner: `run_all_targets_phasar_O2_g_in_container.sh`
- Core pipeline: `run_all_targets_phasar_o2_in_container.sh` (parameterized by env)

## Global logs and summaries

- Full batch log: `run_all_targets_phasar_O2_g.log`
- Cross-project linecheck summary: `phasar_O2_g_linecheck_summary.csv`
- Cross-project status summary: `phasar_O2_g_project_status.csv`

## Per-project output layout

For each project `<project>`:

- `CompilerOptimization/Result/<project>/phasar/phasar-O2-g/`
  - `log/commands.log` (all executed commands)
  - `log/project.log` (build + bc + linecheck process log)
  - `log/ifds-uninit.stdout.log`, `log/ifds-uninit.stderr.log`
  - `log/summary.csv`
  - `artifacts/<project>_O2_g.bc` and `.ll`
  - `runs/ifds-uninit/<timestamp>/psr-report.txt`
  - `runs/ifds-uninit/target_linecheck.csv`
  - `runs/ifds-uninit/target_linecheck.json`
  - `status/success.marker` or `status/failed.marker`
