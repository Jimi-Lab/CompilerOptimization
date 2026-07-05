# Redis PhASAR 3-universe run record

This directory stores full process, logs, and scan outputs for Redis under three compiler universes:

- `phasar_O0_DebInfo`
- `phasar_O2_noinline_RelWithDebInfo`
- `phasar_O2_RelWithDebInfo`

## Entry scripts

- Host runner: `run_redis_phasar_3universes.sh`
- Container pipeline: `run_redis_phasar_3universes_in_container.sh`

## Global logs and summary

- Full run log: `run_all.log`
- Cross-universe summary CSV: `redis_phasar_3universes_summary.csv`

## Per-universe full reports

- O0: `phasar_O0_DebInfo/readme.md`
- O2-noinline: `phasar_O2_noinline_RelWithDebInfo/readme.md`
- O2: `phasar_O2_RelWithDebInfo/readme.md`

Each per-universe folder contains:

- `artifacts/` (whole-program bitcode and disassembled IR)
- `runs/` (per-analysis output directories)
- `logs/` (build, dry-run, BC generation, per-analysis stdout/stderr, summary CSV)
- `work/` (writable source copy used for deterministic builds)
