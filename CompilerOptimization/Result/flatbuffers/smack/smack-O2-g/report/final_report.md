# SMACK Static Scan Final Report

## 1. Input Information
- Bitcode: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM13-O2-g/artifacts/flatbuffers_flatc_O2_g.bc`
- Requested output directory: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/smack/smack-O2-g`
- Actual output directory: `/home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/smack/smack-O2-g`
- Docker image: `smackers/smack:latest-full`
- LLVM/SMACK versions: clang13=`Ubuntu clang version 13.0.1-2ubuntu2.2`; llvm-link13=`Ubuntu LLVM version 13.0.1`; llvm-dis13=`Ubuntu LLVM version 13.0.1`; smack=`SMACK version 2.8.0`
- boogie/corral/z3 in PATH: boogie=`/home/user/.dotnet/tools/boogie`, corral=`/home/user/.dotnet/tools/corral`, z3=`/usr/bin/z3`

## 2. Scan Matrix
- A1: check=assertions, integer_encoding=unbounded-integer, verifier=corral, unroll=10, time_limit=1800, status=translation failure
- A2: check=memory-safety, integer_encoding=unbounded-integer, verifier=corral, unroll=10, time_limit=1800, status=translation failure
- A3: check=integer-overflow, integer_encoding=unbounded-integer, verifier=corral, unroll=10, time_limit=1800, status=translation failure
- A4: check=memory-safety, integer_encoding=unbounded-integer, verifier=corral, unroll=16, time_limit=1800, status=translation failure
- A5: check=assertions, integer_encoding=bit-vector, verifier=corral, unroll=10, time_limit=1800, status=translation failure
- A6: check=memory-safety, integer_encoding=bit-vector, verifier=corral, unroll=10, time_limit=1800, status=translation failure
- A7: check=integer-overflow, integer_encoding=bit-vector, verifier=corral, unroll=10, time_limit=1800, status=translation failure
- A8: check=memory-safety, integer_encoding=unbounded-integer, verifier=svcomp, unroll=10, time_limit=1800, status=translation failure

## 3. Overall Result
- verified: 0
- error: 0
- timeout: 0
- tool failure: 0
- backend failure: 0
- unsupported / translation failure: 0
- translation failure: 8
- translation stage: unsupported / translation failure (llvm2bpl assertion crash during translation)

## 4. Bug Candidates
- No `SMACK found an error:` lines were observed.

## 5. Non-bug Failures and Diagnostics
- A1: status=translation failure, reason=scan skipped: translation failure in translate_probe, stdout=`log/scan_A1.stdout.log`, stderr=`log/scan_A1.stderr.log`
- A2: status=translation failure, reason=scan skipped: translation failure in translate_probe, stdout=`log/scan_A2.stdout.log`, stderr=`log/scan_A2.stderr.log`
- A3: status=translation failure, reason=scan skipped: translation failure in translate_probe, stdout=`log/scan_A3.stdout.log`, stderr=`log/scan_A3.stderr.log`
- A4: status=translation failure, reason=scan skipped: translation failure in translate_probe, stdout=`log/scan_A4.stdout.log`, stderr=`log/scan_A4.stderr.log`
- A5: status=translation failure, reason=scan skipped: translation failure in translate_probe, stdout=`log/scan_A5.stdout.log`, stderr=`log/scan_A5.stderr.log`
- A6: status=translation failure, reason=scan skipped: translation failure in translate_probe, stdout=`log/scan_A6.stdout.log`, stderr=`log/scan_A6.stderr.log`
- A7: status=translation failure, reason=scan skipped: translation failure in translate_probe, stdout=`log/scan_A7.stdout.log`, stderr=`log/scan_A7.stderr.log`
- A8: status=translation failure, reason=scan skipped: translation failure in translate_probe, stdout=`log/scan_A8.stdout.log`, stderr=`log/scan_A8.stderr.log`
- BC `main` present: True
- Undefined symbols count: 159
- No approximation warning pattern captured by this run parser.
- Translation crash details: see `log/translate_probe.stdout.log` and `log/translate_probe.stderr.log` (llvm2bpl assertion).

## 6. Final Conclusion
- No verified bug candidates; translation/backend failures prevent strong conclusions
