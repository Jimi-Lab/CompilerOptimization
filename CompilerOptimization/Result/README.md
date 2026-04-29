# Analyzer Results

This directory contains analyzer runs and paper evidence. Raw analyzer output
can be very large, so most target-specific raw runs remain outside Git.

Track in GitHub:

- the entire `AllUsefulCases/` directory;
- case collection reports and audit notes;
- `collection_manifest.json`;
- `tool_runs.csv`;
- focused summary CSV/JSON files;
- scripts used to collect or normalize cases.

Do not track in normal GitHub:

- target-specific raw run trees outside `AllUsefulCases/`;
- raw logs and `psr-raw-results.txt` outside `AllUsefulCases/`;
- relation dumps and native fact indexes outside `AllUsefulCases/`;
- analyzer build directories and run directories outside `AllUsefulCases/`;
- generated binaries or databases outside `AllUsefulCases/`.

Raw evidence remains important. Preserve it in timestamped full snapshots with
checksums and reference those snapshots from paper notes when needed.
