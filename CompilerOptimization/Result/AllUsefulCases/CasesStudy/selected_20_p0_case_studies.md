# Selected 20 P0 Case Studies

This file is a human-readable index for `selected_20_p0_case_studies.csv`.

| no | case id | repo | tool | selection | reason | reported location | IR function | root cause hint |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `paper-libsndfile-phasar-01` | `libsndfile` | `phasar` | `unique-location` | `SourceTextMismatch` | `CompilerOptimization/Target/libsndfile/src/common.h:974:` | `dpcm_read_dsc2s` | `debug_location_or_source_attribution_drift_candidate` |
| 2 | `paper-libsndfile-phasar-02` | `libsndfile` | `phasar` | `unique-location` | `LineOutOfRange` | `CompilerOptimization/Target/libsndfile/src/GSM610/gsm610_priv.h:616:` | `Gsm_Long_Term_Predictor` | `debug_location_or_source_attribution_drift_candidate` |
| 3 | `paper-libsndfile-seahorn-03` | `libsndfile` | `seahorn` | `unique-location` | `LineZero` | `Target/libsndfile/src/GSM610/short_term.c:0:0` | `` | `location_invalid_or_untrusted_debug_location` |
| 4 | `paper-libsndfile-seahorn-04` | `libsndfile` | `seahorn` | `unique-location` | `LineZero` | `Target/libsndfile/src/alaw.c:0:0` | `` | `location_invalid_or_untrusted_debug_location` |
| 5 | `paper-libsndfile-dg-05` | `libsndfile` | `dg` | `unique-location` | `LineZero` | `:0:0` | `` | `dg_c_lines_reported_invalid_source_location` |
| 6 | `paper-libsndfile-dg-06` | `libsndfile` | `dg` | `repeat-location-variant` | `LineZero` | `:0:0` | `` | `dg_c_lines_reported_invalid_source_location` |
| 7 | `paper-libsndfile-cclyzerpp-07` | `libsndfile` | `cclyzer++` | `unique-location` | `ColumnOutOfRange` | `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.c:193:30` | `<llvm-link>:sfe_apply_metadata_changes` | `Mem2Reg_or_Phi-node_merge_or_CFG_simplification` |
| 8 | `paper-libsndfile-cclyzerpp-08` | `libsndfile` | `cclyzer++` | `unique-location` | `ColumnOutOfRange` | `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.c:289:22` | `<llvm-link>:sfe_apply_metadata_changes` | `Mem2Reg_or_Phi-node_merge_or_CFG_simplification` |
| 9 | `paper-libsndfile-yapall-09` | `libsndfile` | `yapall` | `unique-location` | `LineZero` | `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/programs/common.c:0:` | `sfe_apply_metadata_changes` | `DWARF location drift` |
| 10 | `paper-libsndfile-yapall-10` | `libsndfile` | `yapall` | `unique-location` | `LineZero` | `/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/programs/sndfile-convert.c:0:` | `main` | `DWARF location drift` |
| 11 | `paper-zfp-phasar-11` | `zfp` | `phasar` | `unique-location` | `SourceTextMismatch` | `CompilerOptimization/Target/zfp/src/template/encode.c:244:` | `encode_ints_uint32.29` | `debug_location_or_source_attribution_drift_candidate` |
| 12 | `paper-zfp-phasar-12` | `zfp` | `phasar` | `unique-location` | `SourceTextMismatch` | `CompilerOptimization/Target/zfp/src/template/encode.c:26:` | `zfp_encode_block_float_2` | `debug_location_or_source_attribution_drift_candidate` |
| 13 | `paper-zfp-seahorn-13` | `zfp` | `seahorn` | `unique-location` | `LineZero` | `Target/zfp/include/zfp/bitstream.inl:0:0` | `` | `location_invalid_or_untrusted_debug_location` |
| 14 | `paper-zfp-seahorn-14` | `zfp` | `seahorn` | `repeat-location-variant` | `LineZero` | `Target/zfp/include/zfp/bitstream.inl:0:0` | `` | `location_invalid_or_untrusted_debug_location` |
| 15 | `paper-zfp-dg-15` | `zfp` | `dg` | `unique-location` | `LineZero` | `:0:0` | `` | `dg_c_lines_reported_invalid_source_location` |
| 16 | `paper-zfp-dg-16` | `zfp` | `dg` | `repeat-location-variant` | `LineZero` | `:0:0` | `` | `dg_c_lines_reported_invalid_source_location` |
| 17 | `paper-zfp-cclyzerpp-17` | `zfp` | `cclyzer++` | `unique-location` | `ColumnOutOfRange` | `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/zfp.c:34:23` | `print_error` | `SROA_or_Mem2Reg_or_Phi-node_merge_or_GVN` |
| 18 | `paper-zfp-cclyzerpp-18` | `zfp` | `cclyzer++` | `unique-location` | `ColumnOutOfRange` | `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/zfp.c:35:23` | `print_error` | `SROA_or_Mem2Reg_or_Phi-node_merge_or_GVN` |
| 19 | `paper-zfp-yapall-19` | `zfp` | `yapall` | `unique-location` | `LineZero` | `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/template/decodei.c:0:` | `zfp_decode_block_int64_2` | `DWARF location drift` |
| 20 | `paper-zfp-yapall-20` | `zfp` | `yapall` | `unique-location` | `LineZero` | `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/template/encodef.c:0:` | `zfp_encode_block_float_2` | `DWARF location drift;inline` |
