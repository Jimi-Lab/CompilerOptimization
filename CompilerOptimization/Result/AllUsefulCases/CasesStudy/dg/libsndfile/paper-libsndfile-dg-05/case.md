# paper-libsndfile-dg-05

## Identity

- repo: `libsndfile`
- tool: `dg`
- universe: `O2-g`
- selection_type: `unique-location`
- priority_reason: `LineZero`
- case_kind: `LocationInvalid`
- case_uid: `dg.libsndfile.O2g.0000001`

## Raw Evidence

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719`
- input_bc: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.bc`
- input_ll: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/work/libsndfile_convert.ll`
- raw_artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/log/cda_dod.lines.stdout.log`
- raw_row_or_line: `1`
- evidence_files: `/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/summary/line_hits.csv;/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/dg/dg-LLVM14-O2-g/high_precision_20260402_153719/log/cda_dod.lines.stdout.log`

## Reported Location

- reported_file: ``
- reported_line: `0`
- reported_column: `0`
- location_validity: `line_zero`
- source_region: `unknown`

## IR Anchor

- mode: `cda_dod`
- ir_function: ``
- ir_instruction: ``
- ir_line: ``
- ir_snippet:

```llvm

```

## Source / Message

- source_snippet:

```text

```

- message: `0:0 -> 313:15`
- root_cause_hint: `dg_c_lines_reported_invalid_source_location`
- inventory_confidence: `0.95`
- notes: `source_resolution=missing;summary_csv=line_hits.csv;summary_row=2;source_candidate_index=1;source_count=0;native_output_line=1`

## Manual Study Checklist

- [ ] Confirm all referenced artifacts exist.
- [ ] Validate why the reported location is invalid or drifted.
- [ ] Locate the IR instruction and debug metadata in the `.ll` file.
- [ ] Build 1-3 candidate recovered source locations.
- [ ] Run the LLM recovery prompt using `input.json`.
- [ ] Verify the LLM output manually.
- [ ] Write the paper-ready narrative below.

## Paper-Ready Narrative

TODO.
