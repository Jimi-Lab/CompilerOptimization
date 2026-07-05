# Verification: paper-zfp-yapall-20

## Verdict

- label: `function-only`  <!-- exact | nearby | function-only | wrong | unrecoverable -->
- verified_file: `/home/jimi/PaperExperiment/CompilerOptimization/Target/zfp/src/template/encodef.c`
- verified_line: `75`
- verified_source_text: `stream_write_bits(zfp->stream, 2 * e + 1, bits);`

## Checks

- [x] Raw artifact line/row matches `input.json`.
- [x] Reported location invalidity is independently confirmed.
- [x] IR instruction and debug metadata are located.
- [x] Recovered line is checked against the source tree.
- [x] If inline is claimed, caller/callee attribution is separated.
- [x] If evidence is insufficient, `unrecoverable` is justified rather than guessed.

## Evidence Notes

### Raw Issue Verification

Raw log line 35 confirms:
```
invalid_load	zfp_encode_block_float_2:zfp_encode_block_float_2:534:24	*null
```
Operand = `zfp_encode_block_float_2:zfp_encode_block_float_2:534:24` — block index 534 indicates deep inline expansion.

### IR Instruction

```
LLVM IR line 24451:
  %549 = load %struct.bitstream*, %struct.bitstream** %548, align 8, !dbg !12037, !tbaa !1267
```
Loads `zfp->stream` (field 4 of `zfp_stream` struct). Resolved via `resolved_exact_operand_instruction` (operand IS the instruction result).

### Debug Metadata Trace

```
!12037 = !DILocation(line: 0, scope: !12021, inlinedAt: !12023)
!12021 = DILexicalBlock(scope: !12012, file: !4911, line: 71, column: 7)
!12012 = DISubprogram(name: "encode_block_float_2", file: !4911, line: 63)
!12023 = DILocation(line: 98, column: 79, scope: !11598)
!11598 = DISubprogram(name: "zfp_encode_block_float_2", file: !4911, line: 96)
!4911 = DIFile("Target/zfp/src/template/encodef.c")
```

**关键发现**: scope function (`encode_block_float_2`) ≠ IR function (`zfp_encode_block_float_2`)。指令的 debug scope 指向被内联的 callee，但指令物理上在 caller 的 IR 函数中。

### 三个分类的根因

1. **Wanted-LineColumnMissing**: `DILocation(line: 0)` — LLVM 将 `zfp->stream` 加载从 `if (e)` 块内提升到分支之前，合并的指令失去单一源码行 → line:0
2. **InlineAttributionDrift**: `inlinedAt: !12023` — `encode_block_float_2` 被内联到 `zfp_encode_block_float_2:98`
3. **WrongFunctionAttribution**: `ir_function` ("zfp_encode_block_float_2") ≠ `scope_function` ("encode_block_float_2") — 因内联导致的函数归因偏离

### 对比验证

同一 inlined context 中，`zfp->maxprec` 的加载 (line 68) 保留了 `!dbg !12024 (line:68)` 因为它在 `if(e)` 之前、只被使用一次、未被合并。而 `zfp->stream` 在三个位置 (lines 75/79/83) 跨 if/else 被使用 → O2 合并提升 → line:0。这证明了 line:0 是由 hoisting 合并触发的。

### Correct Location Recovery

`zfp->stream` 在 `encode_block_float_2` 中被三处使用：line 75 (`stream_write_bits(zfp->stream, ...)`), line 79 (`encode_block(zfp->stream, ...)`), line 83 (`stream_write_bit(zfp->stream, ...)`)。合并后的指令服务于所有三处 → 精确列不可恢复。

**最佳恢复**: line 75 (`stream_write_bits(zfp->stream, 2 * e + 1, bits)`) — 这是 `zfp->stream` 最主要的语义使用。

## Paper Use

- include_in_main_table: `true` — 典型的多层叠加 case: 内联 + hoisting + 函数归因错误，三种分类同时触发
- include_as_failure_boundary: `false`
- caveats: `三种分类 (Wanted-LineColumnMissing, InlineAttributionDrift, WrongFunctionAttribution) 源于同一个根因的不同维度：(1) hoisting → line:0, (2) inlining → 跨函数边界, (3) scope≠IR function。这是 O2 -g 下 debug 信息质量逐层退化的典型示例。yapall 的 invalid_load (*null) 是指针分析精度过近似。`
