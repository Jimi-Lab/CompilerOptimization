# Flatbuffers CDA Timeout Retry

- run_dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/dg/dg-LLVM14-O2-g/cda_timeout_retry_20260331_074712`
- This run continues the staged long-timeout CDA retry plan.
- Every executed command is preserved in `commands.log`.

## Final Outcome Per Case
- `cda_standard`: lines `timeout` at pass 2 timeout 3600s; dot `completed` at pass 1 timeout 1800s
- `cda_ntscd`: lines `timeout` at pass 2 timeout 3600s; dot `completed` at pass 1 timeout 1800s
- `cda_ntscd2`: lines `timeout` at pass 2 timeout 3600s; dot `completed` at pass 1 timeout 1800s
- `cda_dod`: lines `completed` at pass 1 timeout 1800s; dot `completed` at pass 1 timeout 1800s
- `cda_dod_ntscd`: lines `timeout` at pass 2 timeout 3600s; dot `completed` at pass 1 timeout 1800s
- `cda_ntscd_ranganath`: lines `timeout` at pass 2 timeout 3600s; dot `completed` at pass 1 timeout 1800s
- `cda_dod_ranganath`: lines `completed` at pass 1 timeout 7200s; dot `completed` at pass 1 timeout 7200s
