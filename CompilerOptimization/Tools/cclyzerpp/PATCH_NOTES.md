# cclyzer++ Local Patch Notes

## 2026-04-30: dbg.declare null address guard

- Scope: local experiment patch for `zfp` and `redis` LLVM14-O2-g cclyzer++ runs.
- Base image: `ghcr.io/galoisinc/cclyzerpp-dev:main`.
- Patched image tag: `paperexperiment/cclyzerpp-dev:llvm14-dbgdeclare-nullguard`.
- Base image id: `sha256:3e5a3f8817c27d5b90754006a7ce83a07317b0744e8813c6a498aef037782f13`.
- Patched image digest: `paperexperiment/cclyzerpp-dev@sha256:f07aacab8eaee4aef22f491f620ca7834434fd18187cf4b218807b27edb0bfa7`.
- Source file: `cclyzerpp/FactGenerator/src/InstructionVisitor.cpp`.
- Change: `visitDbgDeclareInst` now skips a debug declaration when `DDI.getAddress()` returns `nullptr`, matching the existing behavior for `llvm::UndefValue`.
- Rationale: LLVM 14 optimized `-O2 -g` bitcode can contain `dbg.declare` intrinsics whose address operand is unavailable after optimization/debug-info salvage. Upstream cclyzer++ calls `isa<llvm::UndefValue>(address)` without a null check, triggering LLVM's `isa<> used on a null pointer` assertion.
- Rebuilt pass artifacts after patch:
  - `cclyzerpp/build/libSoufflePA.so`: `sha256:9af4e888b25b4f0498cb1bc8746c7cf500f2b8f2240ba75908b45e249dbfb9da`.
  - `cclyzerpp/build/libPAPass.so`: `sha256:cc053271bf1a7f0492509c17bb8d53580945469fec0b1db12150db9463165085`.
- Evidence before patch:
  - `CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260427_132609_zfp_O2_g`: `tool failure`, return code `139`.
  - `CompilerOptimization/Result/redis/cclyzerpp/LLVM14-O2-g/run_20260427_132609_redis-server_O2_g`: `tool failure`, return code `139`.
- Evidence after patch:
  - `CompilerOptimization/Result/zfp/cclyzerpp/LLVM14-O2-g/run_20260430_174927`: `reported`, return code `0`, elapsed `289` seconds.
- Interpretation: runs produced with this patch should be reported as patched-cclyzer++ runs and compared against the preserved upstream tool-failure runs.
