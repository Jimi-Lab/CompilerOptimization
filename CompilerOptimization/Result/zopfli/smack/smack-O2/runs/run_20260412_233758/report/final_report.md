# SMACK Final Report

## Input Information
- Input BC: `/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/zopfli/LLVM13-O2-g/artifacts/zopfli_O2_g.bc`
- Output Dir: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2/runs/run_20260412_233758`
- Docker Image: `smackers/smack:latest-full`
- LLVM/SMACK versions: see `log/00.toolchain_check.stdout.log`

## Scan Matrix
- `assertions_unbounded`: check=`assertions`, integer_encoding=`unbounded-integer`, unroll=`10`, verifier=`corral`, time_limit=`1800`
- `memory_safety_unbounded`: check=`memory-safety`, integer_encoding=`unbounded-integer`, unroll=`10`, verifier=`corral`, time_limit=`1800`
- `integer_overflow_unbounded`: check=`integer-overflow`, integer_encoding=`unbounded-integer`, unroll=`10`, verifier=`corral`, time_limit=`1800`
- `memory_safety_unbounded_unroll16`: check=`memory-safety`, integer_encoding=`unbounded-integer`, unroll=`16`, verifier=`corral`, time_limit=`1800`
- `assertions_bitvector`: check=`assertions`, integer_encoding=`bit-vector`, unroll=`10`, verifier=`corral`, time_limit=`1800`
- `memory_safety_bitvector`: check=`memory-safety`, integer_encoding=`bit-vector`, unroll=`10`, verifier=`corral`, time_limit=`1800`
- `integer_overflow_bitvector`: check=`integer-overflow`, integer_encoding=`bit-vector`, unroll=`10`, verifier=`corral`, time_limit=`1800`
- `memory_safety_unbounded_svcomp`: check=`memory-safety`, integer_encoding=`unbounded-integer`, unroll=`10`, verifier=`svcomp`, time_limit=`1800`

## Result Overview
- `verified`: 2
- `error`: 2
- `timeout`: 0
- `tool failure`: 1
- `backend failure`: 3
- `unsupported / translation failure`: 0
- `completed_with_warnings`: 0
- `completed`: 0

## Bug Candidate List
- `memory_safety_unbounded` check=`memory-safety` integer_encoding=`unbounded-integer` unroll=`10`
  - key line: `SMACK found an error: invalid pointer dereference.`
  - stdout: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2/runs/run_20260412_233758/log/11.memory_safety_unbounded.stdout.log`
  - stderr: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2/runs/run_20260412_233758/log/11.memory_safety_unbounded.stderr.log`
  - trace artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2/runs/run_20260412_233758/artifacts/memory_safety_unbounded.error.txt`
  - last trace lines:
```text
src/zopfli/util.c(33,31): 
src/zopfli/util.c(34,12): 
src/zopfli/util.c(34,30): 
src/zopfli/util.c(35,1): 
src/zopfli/zopfli_bin.c(151,3): RETURN from ZopfliInitOptions
src/zopfli/zopfli_bin.c(153,17): 
src/zopfli/zopfli_bin.c(153,3): 
src/zopfli/zopfli_bin.c(153,17): 
src/zopfli/zopfli_bin.c(153,3): 
src/zopfli/zopfli_bin.c(154,23): 
```
- `memory_safety_unbounded_unroll16` check=`memory-safety` integer_encoding=`unbounded-integer` unroll=`16`
  - key line: `SMACK found an error: invalid pointer dereference.`
  - stdout: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2/runs/run_20260412_233758/log/13.memory_safety_unbounded_unroll16.stdout.log`
  - stderr: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2/runs/run_20260412_233758/log/13.memory_safety_unbounded_unroll16.stderr.log`
  - trace artifact: `/home/jimi/PaperExperiment/CompilerOptimization/Result/zopfli/smack/smack-O2/runs/run_20260412_233758/artifacts/memory_safety_unbounded_unroll16.error.txt`
  - last trace lines:
```text
src/zopfli/util.c(33,31): 
src/zopfli/util.c(34,12): 
src/zopfli/util.c(34,30): 
src/zopfli/util.c(35,1): 
src/zopfli/zopfli_bin.c(151,3): RETURN from ZopfliInitOptions
src/zopfli/zopfli_bin.c(153,17): 
src/zopfli/zopfli_bin.c(153,3): 
src/zopfli/zopfli_bin.c(153,17): 
src/zopfli/zopfli_bin.c(153,3): 
src/zopfli/zopfli_bin.c(154,23): 
```

## Non-bug Failure List
- `assertions_bitvector` -> `backend failure`: `10 type checking errors in /home/jimi/PaperExperiment/a-qeccdwmw.bpl`
- `memory_safety_bitvector` -> `backend failure`: `10 type checking errors in /home/jimi/PaperExperiment/a-yrl6fqsi.bpl`
- `integer_overflow_bitvector` -> `backend failure`: `10 type checking errors in /home/jimi/PaperExperiment/a-_3j5jtwl.bpl`
- `memory_safety_unbounded_svcomp` -> `tool failure`: `Traceback (most recent call last):`

## Approximation / Warning Notes
- src/zopfli/blocksplitter.c:127:45: SMACK warning: overapproximating floating-point operation fadd (can lead to false alarms); try adding all the flag(s) in: { --float }
- src/zopfli/blocksplitter.c:62:5: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/blocksplitter.c:73:32: SMACK warning: overapproximating bitwise operation shl (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/blocksplitter.c:95:3: SMACK warning: approximating llvm.lifetime.end.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/blocksplitter.c:132:3: SMACK warning: overapproximating call to llvm.ctpop.i64 (can lead to false alarms); try adding any flag(s) in: { --integer-encoding=bit-vector --rewrite-bitwise-ops }
- src/zopfli/blocksplitter.c:132:3: SMACK warning: overapproximating bitwise operation shl (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/blocksplitter.c:133:8: SMACK warning: approximating llvm.umax.i64 (can lead to both false alarms and missed detections);
- src/zopfli/blocksplitter.c:136:7: SMACK warning: overapproximating bitwise operation xor (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/blocksplitter.c:136:7: SMACK warning: overapproximating bitwise operation and (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/blocksplitter.c:161:9: SMACK warning: overapproximating call to llvm.ctpop.i64 (can lead to false alarms); try adding any flag(s) in: { --integer-encoding=bit-vector --rewrite-bitwise-ops }
- src/zopfli/blocksplitter.c:161:9: SMACK warning: overapproximating bitwise operation shl (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/deflate.c:598:36: SMACK warning: overapproximating bitwise operation shl (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/deflate.c:586:3: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:587:3: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:0:0: SMACK warning: overapproximating floating-point operation fadd (can lead to false alarms); try adding all the flag(s) in: { --float }
- src/zopfli/deflate.c:608:1: SMACK warning: approximating llvm.lifetime.end.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:414:5: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:415:5: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:387:27: SMACK warning: overapproximating bitwise operation or (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/symbols.h:227:10: SMACK warning: overapproximating bitwise operation shl (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/symbols.h:227:10: SMACK warning: overapproximating bitwise operation ashr (can lead to false alarms); try adding all the flag(s) in: { --integer-encoding=bit-vector }
- src/zopfli/deflate.c:419:3: SMACK warning: approximating llvm.lifetime.end.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:572:3: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:573:3: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:529:3: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:530:3: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:531:3: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:532:3: SMACK warning: approximating llvm.lifetime.start.p0i8 (can lead to both false alarms and missed detections);
- src/zopfli/deflate.c:554:17: SMACK warning: overapproximating floating-point operation fadd (can lead to false alarms); try adding all the flag(s) in: { --float }
- src/zopfli/deflate.c:554:40: SMACK warning: overapproximating floating-point operation fadd (can lead to false alarms); try adding all the flag(s) in: { --float }

## Final Conclusion
- Verdict: `PARTIAL PASS`
- Found bug candidates, but result quality is limited by approximation warnings and several backend/tool failures.
