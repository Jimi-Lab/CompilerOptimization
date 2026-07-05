# Root Cause Analysis: paper-libsndfile-cclyzerpp-07

## Case Identity

| Field | Value |
|-------|-------|
| Case UID | `cclyzerpp.libsndfile.O2g.014160` (raw: `015560`) |
| Repo | libsndfile |
| Tool | cclyzer++ |
| Pipeline | phi_instr → ColumnOutOfRange → Wanted-PhiMergeLocationDrift |
| Reported | `src/common.c:193:30` |
| Correct | `programs/common.c:193:30` |
| Verdict | **工具误报 (Tool False Positive)** — debug metadata 本身完全正确 |

---

## 1. 流水线全景图

```
LLVM IR (.ll)
  │
  ├─[1]─► cclyzer++ Soufflé 分析 ─► phi_instr.facts (Datalog relation)
  │                                        │
  │                                        ▼
  │                               phi_instr.csv.gz
  │                                 row: instr_id=4493, hash=fabfbb94...
  │
  └─[2]─► analyze_native_value_cases.py
              │
              ├─ parse_ll_metadata()      → DIFile/DILocation/DISubprogram 字典
              ├─ build_source_index()     → basename → [Path] 索引
              ├─ stream_ll_indexes_and_maps()
              │    └─ map_instruction_record()
              │         ├─ resolve_dilocation()     ← ★ 关键：解析 !dbg 元数据
              │         │    ├─ resolve_scope_file()  → 遍历 scope 链找到 DIFile
              │         │    │    └─ resolve_difile()  → ★ BUG 在此
              │         │    └─ format_inline_stack() → 展开 inlinedAt 链
              │         ├─ load_source_context()     ← 读取源码行
              │         └─ 列验证: col_no > len(line)+1 → ColumnOutOfRange
              │
              └─ native_fact_source_map.tsv  (file=src/common.c)
                       │
                       ▼
                  phi_instr 流水线:
                    ColumnOutOfRange → PhiMergeLocationDrift → Wanted-PhiMergeLocationDrift
                    root_cause_hint = Mem2Reg_or_Phi-node_merge_or_CFG_simplification
                       │
                       ▼
                  P0 优先级 → 人工筛选 → 本 case study
```

---

## 2. 第一层：cclyzer++ 原生输出

### 2.1 Datalog 分析

cclyzer++ 运行 Soufflé Datalog 引擎对 LLVM IR 进行静态分析。`phi_instr` 关系识别与 phi-node 合并模式关联的 IR 指令。对于本 case：

- **指令**: `<llvm-link>:sfe_apply_metadata_changes:271`
- **IR 行号**: 130122 (在 .ll 文件中)
- **opcode**: `store`
- **IR 文本**: `store i32 %209, i32* %210, align 4, !dbg !87358, !tbaa !33187`
- **phi_incoming_count**: 3 (基本块 %211 有 3 个前驱: %204, %199, %168)

该 store 指令位于基本块 `%204`，该块是包含 phi 节点 `%215 = phi i8* [...]` 的基本块 `%211` 的三个前驱之一。

### 2.2 为什么被 phi_instr 流水线捕获

cclyzer++ 的 phi_instr 分析流水线假设：Mem2Reg 过程中 phi-node 合并和 CFG 简化可能导致指令的 debug location 指向错误的源码位置。该 store 指令处于 phi-merge 上下文中（其所在基本块流向一个 phi 节点），因此被纳入候选。

### 2.3 phi_instr.csv.gz 原始行

```
instr_id: <llvm-link>:sfe_apply_metadata_changes:271
row_index: 4493
hash: fabfbb94c97292e99b8ecac0ae696cb2cc96fe67
ir_text: store i32 %209, i32* %210, align 4, !dbg !87358, !tbaa !33187
```

---

## 3. 第二层：Debug Metadata 解析

### 3.1 元数据提取

`parse_ll_metadata()` 扫描 .ll 文件，提取所有 `!N = !DI...(fields)` 形式的元数据节点。与本 case 相关的节点：

```llvm
; DIFile — 文件定义
!3908 = !DIFile(
    filename: "Target/libsndfile/programs/common.c",     ← ★ 正确文件
    directory: "/home/jimi/PaperExperiment/CompilerOptimization"
)

; 外层函数
!87069 = !DISubprogram(
    name: "sfe_apply_metadata_changes",
    file: !3908,                                          ← 引用 !3908
    line: 234
)

; 内层函数（被内联）
!87165 = !DISubprogram(
    name: "merge_broadcast_info",
    file: !3908,                                          ← 引用 !3908
    line: 105
)

; 词法块 — else 分支 (programs/common.c:189)
!87203 = !DILexicalBlock(
    scope: !87199,
    file: !3908,                                          ← 引用 !3908
    line: 189
)

; 内联调用点 (programs/common.c:265, merge_broadcast_info 的调用处)
!87205 = !DILocation(line: 265, column: 31, scope: !87158)

; 目标指令的 debug location
!87358 = !DILocation(
    line: 193,                                            ← 行号
    column: 30,                                           ← 列号
    scope: !87203,                                        ← 在 else 分支内
    inlinedAt: !87205                                     ← 从调用点内联而来
)
```

**关键事实**: 元数据链完全一致，所有节点通过 `!3908` 引用同一个 DIFile，该 DIFile 的文件名明确是 `programs/common.c`，不是 `src/common.c`。

### 3.2 元数据链追踪

```
!87358 (DILocation, line=193, col=30)
  ├─ scope → !87203 (DILexicalBlock, file=!3908, line=189)
  │   └─ scope → !87199 (DILexicalBlock, file=!3908)
  │       └─ scope → !87200 (DILexicalBlock, file=!3908)
  │           └─ scope → !87201 (DILexicalBlock, file=!3908, line=179)
  │               └─ scope → !87165 (DISubprogram:"merge_broadcast_info", file=!3908)
  └─ inlinedAt → !87205 (DILocation, line=265, col=31)
      └─ scope → !87158 (DILexicalBlock, file=!3908, line=265)
          └─ scope → !87069 (DISubprogram:"sfe_apply_metadata_changes", file=!3908)

!3908 = DIFile(filename="Target/libsndfile/programs/common.c", ...)
```

全部指向 `programs/common.c`。内联关系：`merge_broadcast_info` (line 105) 被内联到 `sfe_apply_metadata_changes` (line 265)。

---

## 4. 第三层：`resolve_difile()` — 根因所在

### 4.1 函数逻辑 (`analyze_native_value_cases.py:1520-1552`)

```python
def resolve_difile(file_id, metadata, source_index, target_root):
    meta = metadata.get(file_id, {})
    filename = meta.get("filename", "")        # "Target/libsndfile/programs/common.c"
    directory = meta.get("directory", "")      # "/home/jimi/.../CompilerOptimization"
    
    # Step A: 拼接 DIFile 自身的完整路径
    raw = Path(directory) / filename
    # raw = /home/jimi/.../Target/libsndfile/programs/common.c  ← 正确!
    
    candidates = []
    
    # Step B: /src/ 特殊处理
    if "/src/" in raw_str:                    # ★ raw 包含 /programs/，不包含 /src/
        ...                                   # ★ 此分支不触发
    
    # Step C: source_index basename 匹配 (is_under 过滤)
    basename = "common.c"
    for candidate in source_index["common.c"]:
        if is_under(candidate, target_root):  # ★ src/common.c ✓, programs/common.c ✓
            candidates.append(candidate)      # ★ src/common.c 先被加入 (字母序)
    
    # Step D: 路径字符串替换
    replaced = raw_str.replace("/work/PaperExperiment", REPO_ROOT)
    # ★ raw 中没有 /work/PaperExperiment → replaced == raw
    
    # Step E: raw.exists() 检查
    if raw.exists():                          # ★ raw 存在!
        candidates.append(raw)                # ★ 但已是第3个候选
    
    # Step F: source_index 二次遍历 (无 is_under 过滤)
    for candidate in source_index["common.c"]:
        candidates.append(candidate)          # ★ src/common.c, programs/common.c 再次加入
    
    # Step G: 去重后取第一个
    return str(dedup_paths(candidates)[0])    # ★ 返回 src/common.c (第一个!)
```

### 4.2 候选列表实际顺序

```
candidates = [
    # Step C (is_under=true):
    Path("/home/jimi/.../Target/libsndfile/src/common.c"),       # index 0 ← 字母序第一
    Path("/home/jimi/.../Target/libsndfile/programs/common.c"),  # index 1
    # Step E (raw.exists()):
    Path("/home/jimi/.../Target/libsndfile/programs/common.c"),  # index 2 (同 index 1)
    # Step F:
    Path("/home/jimi/.../Target/libsndfile/src/common.c"),       # index 3 (同 index 0)
    Path("/home/jimi/.../Target/libsndfile/programs/common.c"),  # index 4 (同 index 1)
]

dedup 后: [src/common.c, programs/common.c]
dedup_paths(...)[0] = src/common.c  ← 错误!
```

### 4.3 Bug 的构成因素

| 因素 | 说明 |
|------|------|
| **Basename 冲突** | 项目中有两个 `common.c` 文件 (`src/` 和 `programs/`) |
| **字母序优先** | `os.walk` 按字母序先遍历 `src/`，`source_index["common.c"][0]` 永远是 `src/common.c` |
| **优先级倒置** | `resolve_difile()` 将 source_index 的 basename 匹配结果放在 DIFile 自身解析结果 (`raw`) 之前 |
| **`dedup_paths()[0]`** | 永远返回第一个候选，而第一个候选是(错误的) basename 匹配结果 |

### 4.4 为什么 `programs/sndfile-convert.c` 没有被错误解析

`sndfile-convert.c` 在项目中只有一个，没有 basename 冲突。`source_index["sndfile-convert.c"]` 只有一个条目，所以无论优先级如何都能正确解析。

---

## 5. 第四层：ColumnOutOfRange 的产生

### 5.1 源码读取

`map_instruction_record()` 调用 `load_source_context()` 读取已解析文件的指定行：

```python
source_file = "/home/jimi/.../Target/libsndfile/src/common.c"  # ← 错误的文件
line = 193
column = 30
```

### 5.2 src/common.c 第 193 行

```c
   191:                        if (lead_char != '0' && left_align == SF_FALSE)
   192:                            width_specifier -- ;
>> 193:                                                              ← 空行!
   194:                        u = - ((unsigned) d) ;
   195:                        }
```

第 193 行是 `case 'd':` 整型格式化代码块中的一个空行，用于分隔 `if` 块和赋值语句。该行内容为空字符串，长度 0。

### 5.3 列验证

```python
line_no = 193          # 1 ≤ 193 ≤ 1849 ✓ (行号在范围内)
col_no = 30            # 30 > len("") + 1 = 1  → ColumnOutOfRange ✗
```

`ColumnOutOfRange` 的判定条件是 `col_no > len(source_line_text) + 1`。对于空行，`len("") + 1 = 1`，所以任何 col_no > 1 都会触发该判定。col_no=30 远远超出。

### 5.4 如果文件正确解析

`programs/common.c:193`:
```c
   193:            binfo.coding_history_size = (uint32_t) slen ;
                 ^                                    ^
                 1                                   57
                               ^
                              30 = 'o' (in "coding_history_size")
```

- `len(line) = 56`（注意源码中用 tab 缩进，但 .ll 中的 DIFile column 是基于原始字节偏移）
- `col_no = 30 ≤ 57` → **MappedExact** ✓

---

## 6. 第五层：Wanted-PhiMergeLocationDrift 分类

### 6.1 分类流程

`analyze_native_value_cases.py` 输出的 `mapping_status = ColumnOutOfRange` 被 phi_instr 分析流水线消费：

```
mapping_status: ColumnOutOfRange
  → phenomenon: PhiMergeLocationDrift
    → classification: Wanted-PhiMergeLocationDrift
      → root_cause_hint: Mem2Reg_or_Phi-node_merge_or_CFG_simplification
        → priority: P0
```

### 6.2 分类为何是误导性的

`Wanted-PhiMergeLocationDrift` 暗示 debug location 的漂移是由 phi-node 合并（Mem2Reg/CFG 简化）导致的。但实际上：

1. **Debug metadata 本身没有漂移**：`!87358` 正确地指向 `programs/common.c:193:30`
2. **漂移发生在工具层**：cclyzer++ 的文件解析将 `programs/common.c` 错误地映射为 `src/common.c`
3. **Phi-node 合并不是根因**：即使该指令不在 phi-merge 上下文中，只要 debug metadata 引用 `programs/common.c`，文件解析错误仍然会导致 `ColumnOutOfRange`

phi_instr 流水线正确地识别了指令处于 phi-merge 上下文（`phi_incoming_count=3`），但错误地将 ColumnOutOfRange 归因于 phi-merge 的副作用。

---

## 7. 根因总结

```
┌─────────────────────────────────────────────────────────────────┐
│                        根因链                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  触发条件: 项目中有两个同名 basename 的源文件                         │
│           (src/common.c 和 programs/common.c)                     │
│                                                                  │
│  直接原因: resolve_difile() 的候选优先级设计缺陷                      │
│           1. basename 索引匹配 (source_index)                      │
│           2. DIFile 自身路径 (raw) ← 本应排在第一位                  │
│           dedup_paths()[0] 永远取第一个 → basename 匹配获胜           │
│                                                                  │
│  环境因素: os.walk 按字母序遍历，src/ 先于 programs/                  │
│           source_index["common.c"][0] 固定为 src/common.c          │
│                                                                  │
│  表现:     ColumnOutOfRange @ src/common.c:193 (空行)              │
│           映射为 Wanted-PhiMergeLocationDrift (误导性标签)           │
│                                                                  │
│  实质:     Debug metadata 完全正确，工具层文件解析错误导致误报           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 与 phi-node merge 的关系

该 store 指令恰好位于 phi-merge 上下文（基本块 %204 → %211 phi），所以被 phi_instr 流水线捕获。但 debug location 的"无效"并非由于 phi-merge 导致的元数据损坏——而是工具的文件解析层在解析正确的 debug 元数据时出了错。**phi-merge 上下文是巧合，不是原因。**

### 修复建议

在 `resolve_difile()` 中，应将 DIFile 自身的 `raw` 路径作为最高优先级候选（如果该路径存在），其次才是 source_index 的 basename 匹配：

```python
# 修正后的优先级:
candidates = []
if raw.exists():
    candidates.append(raw)           # ★ DIFile 自身路径优先
# 然后才是 source_index 匹配 (作为 fallback)
for candidate in source_index.get(basename, []):
    ...
```

或者，对 source_index 中的多个同名文件，使用 DIFile 的 directory 字段进行路径后缀匹配来消除歧义。
