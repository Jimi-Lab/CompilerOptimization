# Root Cause Analysis: paper-zfp-yapall-20 — Triple Classification: LineZero + InlineDrift + WrongFunction

## Case Identity

| Field | Value |
|-------|-------|
| Case UID | `yapall.zfp.O2g.001940781` (candidate: `zfp_000000020`) |
| Repo | zfp |
| Tool | yapall |
| Pipeline | invalid_load → Wanted-LineColumnMissing + InlineAttributionDrift + WrongFunctionAttribution |
| Reported | `encodef.c:0` (line_zero) |
| IR function | `zfp_encode_block_float_2` |
| Scope function | `encode_block_float_2` |
| Verdict | **function-only** — 三层叠加: (1) 内联跨越函数边界, (2) code hoisting 导致 line:0, (3) 函数归因错误 |

---

## 1. 完整 Debug Metadata 链

```
!12037 = !DILocation(line: 0, scope: !12021, inlinedAt: !12023)    ← 目标指令的 debug loc
  │
  ├─ scope: !12021 = DILexicalBlock(scope: !12012, file: !4911, line: 71, column: 7)
  │     │              ↑ line 71 = "if (e) {" 在 encode_block_float_2 中
  │     └─ scope: !12012 = DISubprogram(name: "encode_block_float_2", file: !4911, line: 63)
  │           ↑ callee: 实际的编码逻辑 (line 63-90)
  │
  └─ inlinedAt: !12023 = DILocation(line: 98, column: 79, scope: !11598)
        └─ scope: !11598 = DISubprogram(name: "zfp_encode_block_float_2", file: !4911, line: 96)
              ↑ caller: 公共包装函数 (line 96-99)

!4911 = DIFile(filename: "Target/zfp/src/template/encodef.c")
```

### 元数据链解读

| 元素 | 函数 | 行 | 角色 |
|------|------|-----|------|
| **scope** | `encode_block_float_2` | line 71 `if (e)` 块 | 指令的"逻辑归属"（私有实现函数） |
| **inlinedAt** | `zfp_encode_block_float_2` | line 98 col 79 | 指令的"执行上下文"（公共包装调用点） |
| **DILocation.line** | — | **0** | LLVM 标记: "无单一源码位置" |

---

## 2. 源码分析

`encodef.c` 包含两个函数：私有实现 `encode_block_float_2` 和公共包装 `zfp_encode_block_float_2`：

**私有实现** (line 63-90):
```c
static uint
_t2(encode_block, Scalar, DIMS)(zfp_stream* zfp, const Scalar* fblock)
{
  uint bits = 1;
  int emax = _t1(exponent_block, Scalar)(fblock, BLOCK_SIZE);        // line 67
  uint maxprec = precision(emax, zfp->maxprec, zfp->minexp, DIMS);   // line 68 ← 有行号
  uint e = maxprec ? (uint)(emax + EBIAS) : 0;                       // line 69
  if (e) {                                                            // line 71 ← scope 所在
    cache_align_(Int iblock[BLOCK_SIZE]);
    bits += EBITS;
    stream_write_bits(zfp->stream, 2 * e + 1, bits);                 // line 75 ← zfp->stream 使用点1
    _t1(fwd_cast, Scalar)(iblock, fblock, BLOCK_SIZE, emax);
    bits += _t2(encode_block, Int, DIMS)(zfp->stream, ...);          // line 79 ← zfp->stream 使用点2
  }
  else {
    stream_write_bit(zfp->stream, 0);                                 // line 83 ← zfp->stream 使用点3
    ...
  }
  return bits;
}
```

**公共包装** (line 96-99):
```c
size_t
_t2(zfp_encode_block, Scalar, DIMS)(zfp_stream* zfp, const Scalar* fblock)
{
  return REVERSIBLE(zfp)                                             // line 98
    ? _t2(rev_encode_block, Scalar, DIMS)(zfp, fblock)
    : _t2(encode_block, Scalar, DIMS)(zfp, fblock);                 // ← col 79: 调用 encode_block_float_2
}
```

当 `Scalar=float, DIMS=2` 时，包装函数实例化为 `zfp_encode_block_float_2`。

---

## 3. 三层根因剖析

### Layer 1: 内联 (InlineAttributionDrift)

`encode_block_float_2` 被内联到 `zfp_encode_block_float_2` 的调用点 (line 98, col 79)。

优化前的调用链：
```
zfp_encode_block_float_2(zfp, fblock)
  └─ encode_block_float_2(zfp, fblock)
       ├─ zfp->maxprec  (line 68)
       ├─ zfp->stream   (line 75, 79, 83)  ← 在 if(e) 块内外
       └─ ...
```

优化后（内联 + hoisting）：
```llvm
; === zfp_encode_block_float_2 的 prologue（内联后的混合代码）===
; line 68 的指令保留行号：
%535 = getelementptr ... %0, i32 2     ; &zfp->maxprec    !dbg !12024 (line:68)
%536 = load i32, i32* %535              ; zfp->maxprec      !dbg !12024 (line:68)

; ★ 但 zfp->stream 被提升到 if(e) 之前，失去行号：
%548 = getelementptr ... %0, i32 4     ; &zfp->stream      !dbg !12037 (line:0)  ← TARGET
%549 = load %struct.bitstream*, ... %548 ; zfp->stream      !dbg !12037 (line:0)  ← TARGET

; if(e) 检查保留行号：
br i1 %547, label %932, label %550     ;                    !dbg !12038 (line:71)
```

### Layer 2: Hoisting 导致 line:0 (Wanted-LineColumnMissing)

`zfp->stream` 在 `encode_block_float_2` 中被使用了三次：line 75 `stream_write_bits(zfp->stream, ...)`, line 79 `encode_block(zfp->stream, ...)`, line 83 `stream_write_bit(zfp->stream, ...)`。这些使用分布在 `if (e)` 和 `else` 两个分支中。

O2 优化将 `zfp->stream` 的加载提升到 `if (e)` 分支之前，变成一条共享指令。因为：
- 合并后的指令不再属于 line 75/79/83 中的任何一个
- 也不在 `if (e)` 的 line 71 范围内
- LLVM 将 debug location 设为 `line: 0`

对比：`zfp->maxprec` 的加载 (line 68) 保留了行号，因为它只在 `if (e)` 之前被使用一次，没有被合并。

### Layer 3: 函数归因错误 (WrongFunctionAttribution)

`build_yapall_valuecases.py` 的分类逻辑：
```python
ir_function = row.get("ir_function")     # "zfp_encode_block_float_2"
source_func = row.get("source_enclosing_function")  # "encode_block_float_2" (从 scope line 71 回溯)
scope_func = row.get("scope_function")   # "encode_block_float_2" (从 !12012)

if source_func and ir_function and source_func != ir_function:
    classes.append("WrongFunctionAttribution")  # ← 触发!
```

这是因为 `source_enclosing_function` 函数从源码 line 71 向上搜索，找到 `encode_block_float_2`（定义在 line 63），而不是外层的 `zfp_encode_block_float_2`（定义在 line 96）。scope 指向 callee，但 IR instruction 在 caller 中 → 函数归因不匹配。

### 三层叠加的完整 IR 上下文

```
IR 函数: zfp_encode_block_float_2  (包装函数，line 96)
  │
  ├─ [line:68] %536 = load zfp->maxprec    ← 保留行号（未合并）
  │
  ├─ [line:0]  %543 = compute e value      ← 合并后失去行号
  ├─ [line:0]  %548 = &zfp->stream         ← scope: encode_block_float_2, line:0
  ├─ [line:0]  %549 = load zfp->stream     ← ★ TARGET: scope callee, line 0
  │
  └─ [line:71] br i1 %547, ...             ← 保留行号（if(e) 检查）
       │
       ├─ block %932: else path (e==0)
       └─ block %550: if path  (e!=0), 包含 stream_write_bits 的内联代码
```

---

## 4. 三种分类的触发条件详解

| 分类 | 触发条件 | 本 case 的值 | 说明 |
|------|----------|-------------|------|
| **Wanted-LineColumnMissing** | `source_status == "source_line_missing"` | line=0 → `source_line_missing` | DILocation 明确为 line:0 |
| **InlineAttributionDrift** | `loc.has_inlined_at == True` | inlinedAt → `!12023` | 指令有非空 inlinedAt 链 |
| **WrongFunctionAttribution** | `ir_function != source_enclosing_function` | `zfp_encode_block_float_2` ≠ `encode_block_float_2` | scope 指向 callee, IR 在 caller |

三个分类全部正确触发，反映了同一个根因的三个不同维度。

---

## 5. yapall `invalid_load` 语义

与 case 19 相同：yapall 的 k=0, flow-insensitive 分析将 `zfp->stream` 的加载关联到 `*null` allocation。`Null.loadable() = false` → 触发 `invalid_load`。这是指针分析精度过近似，不是真正的程序 bug。

---

## 6. 正确位置恢复

### 恢复分析

`zfp->stream` 的加载指令服务于 `encode_block_float_2` 中的三处使用：
- Line 75: `stream_write_bits(zfp->stream, ...)` — `if (e)` 路径
- Line 79: `encode_block(zfp->stream, ...)` — `if (e)` 路径
- Line 83: `stream_write_bit(zfp->stream, ...)` — `else` 路径

由于指令被提升到 `if (e)` 分叉之前，它为两个分支中的所有使用服务，精确列不可恢复。

**最近的单一源码锚点**：
- **scope 行**: line 71 `if (e) {` — DILexicalBlock 的入口行
- **inlinedAt**: line 98, col 79 — `encode_block_float_2(zfp, fblock)` 的调用点

### Recovery Verdict

- **File**: `Target/zfp/src/template/encodef.c`
- **Granularity**: `function-only` — 最精确的恢复是 scope function `encode_block_float_2` 的定义行 (line 63)，或 inlinedAt caller 的调用行 (line 98)
- **推荐恢复**: line 75 (`stream_write_bits(zfp->stream, ...)`) 作为最可能的语义位置，但 confidence 仅为 `function-only`，因为指令服务于多个源码行

---

## 7. 与 Case 19 的对比

| 维度 | Case 19 (decodei.c) | Case 20 (encodef.c) |
|------|---------------------|---------------------|
| 模板文件 | `decodei.c` (整数解码) | `encodef.c` (浮点编码) |
| 函数结构 | 单层: wrapper → ternary | 两层: wrapper → ternary → encode_block |
| 分类数 | 1 (LineColumnMissing) | **3** (LineColumnMissing + InlineDrift + WrongFunction) |
| line:0 层数 | 1 (ternary hoisting) | **2** (ternary hoisting + if(e) hoisting) |
| 跨函数归因 | 否 (scope=wrapper) | **是** (scope=callee encode_block, IR=caller wrapper) |
| Recovery | function-only (1 个源码行) | function-only (多行，跨 if/else) |
| 复杂度 | 简单 hoisting | **嵌套内联 + 多层 hoisting + 函数归因错误** |

---

## 8. 根因总结

```
┌──────────────────────────────────────────────────────────────────┐
│              三层根因叠加 (Triple Root Cause)                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Layer 1 — 内联 (Inline):                                        │
│    encode_block_float_2 (私有实现) 被内联到                         │
│    zfp_encode_block_float_2 (公共包装) 的 line 98 调用点            │
│    → scope 指向 callee, IR 在 caller → 跨函数边界                  │
│                                                                   │
│  Layer 2 — Hoisting (代码提升):                                    │
│    zfp->stream 在 callee 中被 if/else 两个分支共同使用              │
│    O2 将 shared loads 提升到分支之前 → line: 0                     │
│    注意：zfp->maxprec (line 68) 未被合并 → 保留了行号               │
│                                                                   │
│  Layer 3 — 函数归因 (Attribution):                                 │
│    source_enclosing_function 回溯到 scope 所在函数                  │
│    (encode_block_float_2 @ line 63)                                │
│    ir_function = zfp_encode_block_float_2 (IR 中的外层函数)         │
│    → WrongFunctionAttribution 分类触发                             │
│                                                                   │
│  结果:                                                             │
│    三个分类同时触发, 对应同一个根因现象的三个维度                     │
│    - Wanted-LineColumnMissing: DILocation line:0                   │
│    - InlineAttributionDrift: 内联跨函数边界                         │
│    - WrongFunctionAttribution: scope/IR 函数不匹配                  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```
