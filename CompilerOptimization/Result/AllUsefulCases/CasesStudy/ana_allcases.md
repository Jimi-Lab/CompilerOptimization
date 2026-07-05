!image.png

# Cases Study

20-cases

这个表格的信息密度是不是太大了

# 20个cases  Studty

cases的表现；为什么报错？LLM如何恢复至正确的行号？

### paper-libsndfile-phasar-01

输出的file不对 ；At IR Statement和uninit value对应不到.ll文件，！dbg信息不对

IR链条中有inline，说明这个cases的发生与inline有关

源输出：/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/phasar/phasar-O2-g/runs/ifds-uninit/libsndfile_O2_g-Mon-Mar-16-07:39:03-2026/psr-report.txt

```bash

---------------------------------  309. Use  ---------------------------------

Variable(s): last_val
Line       : 974                                     正确
Source code: {	last_val += src [k] ;                正确
Function   : dpcm_read_dsc2s                         正确
File       : /work/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.h  错误

Corresponding IR Statements and uninit. Values
At IR Statement: %49 = add i8 %48, %42, !dbg !136051, !psr.id !136073 | ID: 66118
   Uninit Value: %42 = add i8 %41, %38, !dbg !136051, !psr.id !136052 | ID: 66104

```

file错误，！dbg ！xxxx错误

实际源码：

/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/common.h

!image.png

报告的可能实际位置：

/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/src/xi.c

!image.png

源码中Source code的函数为dsc2f_array，与report提到的dpcm_read_dsc2s不是一个函数，源码中真实的调用过程为：源码last_val += src [k]—>dsc2s_array—>dpcm_read_dsc2s

查看report的IR：

Corresponding IR Statements and uninit. Values
At IR Statement: %49 = add i8 %48, %42, !dbg !136051, !psr.id !136073 | ID: 66118
Uninit Value: %42 = add i8 %41, %38, !dbg !136051, !psr.id !136052 | ID: 66104

在这个report IR中，可以一步步追溯到正确的源码。

这个report仅错误报告了file，其余都正确

感觉这个好像是  phasar的bug呀：file路径报错

```bash
Line       : 974                       // 来自 instruction !dbg，xi.c:974
Source code: { last_val += src [k] ;   // 来自 instruction !dbg，xi.c:974
Function   : dpcm_read_dsc2s           // 来自 IR 宿主函数
File       : common.h                  // 来自 dbg.value 关联变量 x 的 DILocalVariable file
```

这个file为什么错误？究竟是什么原因？！dbg信息也不对

原因分析：

与phasar的实现函数有关，也可能与编译优化有关

### paper-libsndfile-phasar-02

输出的File不对，!dbg也不对

原始输出

```bash
---------------------------------  267. Use  ---------------------------------

Variable(s): L_max
Line       : 616
Source code: R = SASR_L (L_max << temp, 16) ;
Function   : Gsm_Long_Term_Predictor
File       : /work/PaperExperiment/CompilerOptimization/Target/libsndfile/src/GSM610/gsm610_priv.h

Corresponding IR Statements and uninit. Values
At IR Statement: %2334 = shl i32 %2251, %2333, !dbg !159835, !psr.id !159836 | ID: 79559
   Uninit Value: %2251 = ashr i32 %2249, %2250, !dbg !159727, !psr.id !159728 | ID: 79472

```

对应file+line：

CompilerOptimization/Target/libsndfile/src/GSM610/gsm610_priv.h根本就不存在616行

对应source code：

!image.png

能找到这个src，src对应的行号也对。

分析一下为什么dbg和file报错了：

这是report的：

```bash
Corresponding IR Statements and uninit. Values
At IR Statement: %2334 = shl i32 %2251, %2333, !dbg !159835, !psr.id !159836 | ID: 79559
   Uninit Value: %2251 = ashr i32 %2249, %2250, !dbg !159727, !psr.id !159728 | ID: 79472
```

真实.ll中为：

```bash
%2334 = shl i32 %2251, %2333, !dbg !80276
%2251 = ashr i32 %2249, %2250, !dbg !80255
```

可以看到！dbg信息是不一致的，report的！dbg的！xxx在ll中根本就不存在

看一下真实的调用流程是什么

追%2334 = shl i32 %2251, %2333, !dbg !80276

| %2334 = shl i32 %2251, %2333, !dbg !80276 | !80276 = !DILocation(line: 616, column: 20, scope: !80055, inlinedAt: !80102) | !80055 = distinct !DISubprogram(name: "Calculation_of_the_LTP_parameters", scope: !7292, file: !7292, line: 462, type: !79883, scopeLine: 467, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !10572, retainedNodes: !80056)
 | !7292 = !DIFile(filename: "Target/libsndfile/src/GSM610/long_term.c", directory: "/work/PaperExperiment/CompilerOptimization", checksumkind: CSK_MD5, checksum: "efd337a6be6bdabb4ce53bc7a4573b13")

|  |  |                                                                    |                                                                                     |  |
| - | - | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------- | - |
|  |  | !80102 = distinct !DILocation(line: 884, column: 4, scope: !79878) | !79878 = distinct !DILexicalBlock(scope: !79821, file: !7292, line: 869, column: 6) |  |

追%2251 = ashr i32 %2249, %2250, !dbg !80255

| %2251 = ashr i32 %2249, %2250, !dbg !80255 | !80255 = !DILocation(line: 586, column: 16, scope: !80055, inlinedAt: !80102) | !80055 = distinct !DISubprogram(name: "Calculation_of_the_LTP_parameters", scope: !7292, file: !7292, line: 462, type: !79883, scopeLine: 467, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !10572, retainedNodes: !80056)
 | !7292 = !DIFile(filename: "Target/libsndfile/src/GSM610/long_term.c", directory: "/work/PaperExperiment/CompilerOptimization", checksumkind: CSK_MD5, checksum: "efd337a6be6bdabb4ce53bc7a4573b13")

|                                                                                     |  |                                                                    |  |
| ----------------------------------------------------------------------------------- | - | ------------------------------------------------------------------ | - |
|                                                                                     |  | !80102 = distinct !DILocation(line: 884, column: 4, scope: !79878) |  |
| !79878 = distinct !DILexicalBlock(scope: !79821, file: !7292, line: 869, column: 6) |  |                                                                    |  |

按照这两个！dbg来说，是根本与gsm610_priv.h无关的

与gsm610_priv.h文件有关的dbg语句：（就一句）

!77403 = !DIFile(filename: "Target/libsndfile/src/GSM610/gsm610_priv.h", directory: "/work/PaperExperiment/CompilerOptimization", checksumkind: CSK_MD5, checksum: "01f8aa95e5cf7d71046f8685d153bd71")
调用！77403的直接调用点有344个

在这个cases中，file错误是因为phasar在生成报告的时候，有逻辑缺陷：

phasar代码：

```bash
NewUR.Line = getLineFromIR(User.first);
NewUR.FuncName = getFunctionNameFromIR(User.first);
NewUR.FilePath = getFilePathFromIR(User.first);
NewUR.SrcCode = getSrcCodeFromIR(User.first);
```

- Line 来自 getLineFromIR(%2334)，读 %2334 自己的 !dbg !80276，所以得到 616。
- SrcCode 来自 getSrcCodeFromIR(%2334)，也走 %2334 的 DILocation，所以读到 long_term.c:616 的 R = SASR_L...。
- 但 FilePath 来自 getFilePathFromIR(%2334)，这里 Phasar 先看这条 instruction 是否被 debug metadata 使用。

在/phasar/lib/PhasarLLVM/Utils/LLVMIRToSrc.cpp中：

```bash
} else if (const auto *I = llvm::dyn_cast<llvm::Instruction>(V)) {
  if (I->isUsedByMetadata()) {
    if (auto *LocVar = getDILocalVariable(I)) {
      return LocVar->**getFile**();
    }
  } else if (I->getMetadata(llvm::LLVMContext::MD_dbg)) {
    return I->getDebugLoc()->getFile();
  }
```

在ll中，%2334的下一行直接就被使用了

```bash
%2334 = shl i32 %2251, %2333, !dbg !80276
call void @llvm.dbg.value(metadata i32 %2334, metadata !80277, metadata !DIExpression()), !dbg !80281
call void @llvm.dbg.value(metadata i16 16, metadata !80280, metadata !DIExpression()), !dbg !80281

...

!80276 = !DILocation(line: 616, column: 20, scope: !80055, inlinedAt: !80102)
!80277 = !DILocalVariable(name: "x", arg: 1, scope: !80278, file: !77403, line: 66, type: !407)
!80278 = distinct !DISubprogram(name: "SASR_L", scope: !77403, file: !77403, line: 66, type: !77404, scopeLine: 67, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !10572, retainedNodes: !80279)
!80279 = !{!80277, !80280}

...

!77403 = !DIFile(filename: "Target/libsndfile/src/GSM610/gsm610_priv.h", directory: "/work/PaperExperiment/CompilerOptimization", checksumkind: CSK_MD5, checksum: "01f8aa95e5cf7d71046f8685d153bd71")

```

%2334 被一个 llvm.dbg.value 当作内联函数 SASR_L 的参数 x 使用了。Phasar 的 getFilePathFromIR(%2334) 因为看到 %2334->isUsedByMetadata()，优先取了这个 DILocalVariable x 的 file，于是得到 gsm610_priv.h。

所以，这个cases，属于是phasar的bug，在report的时候，source mapping的错误，也不能直接说是clang -O2 -g优化造成的。但是有间接关系，优化/inline 是触发条件：SASR_L 是 static inline，在 O2-g IR 中内联后，%2334 同时代表 caller 表达式 L_max << temp 和 callee 参数 x 的 debug value。没有这种 inline/debug metadata 叠加，Phasar 不容易走到这个错误分支。

### paper-zfp-phasar-11

report的结果：

```bash

---------------------------------  32. Use  ---------------------------------

Variable(s): s, s
Line       : 244
Source code: if (++s->bits == wsize) {
Function   : encode_ints_uint32.29
File       : /work/PaperExperiment/CompilerOptimization/Target/zfp/src/template/encode.c

Corresponding IR Statements and uninit. Values
At IR Statement: %256 = add i64 %250, 1, !dbg !18796, !psr.id !18797 | ID: 10893
   Uninit Value: %250 = phi i64 [ %337, %335 ], [ %235, %244 ], !psr.id !18776 | ID: 10879
At IR Statement: %257 = icmp eq i64 %256, 64, !dbg !18799, !psr.id !18800 | ID: 10895
   Uninit Value: %256 = add i64 %250, 1, !dbg !18796, !psr.id !18797 | ID: 10893
At IR Statement: br i1 %257, label %258, label %260, !dbg !18801, !psr.id !18802 | ID: 10896
   Uninit Value: %257 = icmp eq i64 %256, 64, !dbg !18799, !psr.id !18800 | ID: 10895
```

对应file+line：

!image.png

对应src code：

!image.png

这个cases的原因跟上一个一样，不赘述了。

### paper-zfp-phasar-12

src和line能对应，file对应不上

```bash

---------------------------------  168. Use  ---------------------------------

Variable(s): z, x, z
Line       : 26
Source code: w -= z; z -= y;
Function   : zfp_encode_block_float_2
File       : /work/PaperExperiment/CompilerOptimization/Target/zfp/src/template/encode.c

Corresponding IR Statements and uninit. Values
At IR Statement: %264 = sub i32 %262, %263, !dbg !30918, !psr.id !30919 | ID: 18727
   Uninit Value: %262 = sub i32 %261, %260, !dbg !30912, !psr.id !30913 | ID: 18722
   Uninit Value: %263 = sub i32 %260, %238, !dbg !30908, !psr.id !30915 | ID: 18724
At IR Statement: %265 = add i32 %262, %261, !dbg !30910, !psr.id !30921 | ID: 18729
   Uninit Value: %261 = extractelement <2 x i32> %250, i64 1, !dbg !30910, !psr.id !30911 | ID: 18721
   Uninit Value: %262 = sub i32 %261, %260, !dbg !30912, !psr.id !30913 | ID: 18722

```

- **是 Phasar report/source mapping 的错误。**
- **不是源码 bug。**
- **不是 %264 的 instruction !dbg 错误。**
- **优化/inline 是触发条件，因为 O2-g 让一个 SSA value 同时服务多个 inlined debug variable。**
- **直接根因是 Phasar 把 instruction location 和 DILocalVariable file 混用了。**

### paper-libsndfile-seahorn-03

sea smc-checks --print-smc-stats --smc-check-threshold=100000 --sea-dsa-type-aware ...

也就是 run 里的 smc_typeon，不是后续 sea horn --solve 的证明结果。后续 horn_smc_* 在这个 run 中是 error 247，所以
这条不能解读成 SeaHorn 已经用 Horn solver 证明了真实 bug。

原生输出raw：/home/jimi/PaperExperiment/CompilerOptimization/Result/libsndfile/seahorn/seahorn-O2-g/result/run_20260322_101107_fixed_fullmatrix/log/sea.smc.instrument.stderr.log

```bash
Possible read of undefined value at 
--- File   : Target/libsndfile/src/GSM610/short_term.c
--- Line   : 0
--- Column : 0
--- Bitcode:   %51 = insertelement <8 x float> poison, float %13, i64 0, !dbg !6786
```

seahorn类型是未定义读，它报了line和column全是0

Target/libsndfile/src/GSM610/short_term.c

!image.png

真实ir：/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/artifacts/libsndfile_sndfile_convert_O2_g.ll

!image.png

与报告的！dbg ！6786不一样，这是因为seahorn在报告的时候会重新编号，不要把！6786当作跨文件稳定id

```bash
一条条追：拿到源码中的函数名Fast_Short_term_synthesis_filtering
!79748 = distinct !DISubprogram(name: "Fast_Short_term_synthesis_filtering", scope: !78917, file: !78917, line: 293, type: !79699, scopeLine: 300, flags: DIFlagPrototyped | DIFlagAllCallsDescribed, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !6694, retainedNodes: !79749)
!79763 = !DILocation(line: 0, scope: !79748)
!79764 = !DILocation(line: 308, column: 13, scope: !79765)
!79771 = !DILocation(line: 311, column: 2, scope: !79748)

%51 = insertelement <8 x float> poison, float %13, i64 0, !dbg !79763
%52 = shufflevector <2 x float> %25, <2 x float> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>, !dbg !79763
%53 = shufflevector <8 x float> %51, <8 x float> %52, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>, !dbg !79763
%54 = shufflevector <4 x float> %45, <4 x float> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>, !dbg !79763
%55 = shufflevector <8 x float> %53, <8 x float> %54, <8 x i32> <i32 0, i32 1, i32 2, i32 8, i32 9, i32 10, i32 11, i32 undef>, !dbg !79763
```

为什么 line=0, column=0？讲解：
SeaHorn 直接读取 LLVM debug location 的 line 和 column。本地原始 .ll 中同一条语义指令是：
!79763 = !DILocation(line: 0, scope: !79748)
!79748 = distinct !DISubprogram(name: "Fast_Short_term_synthesis_filtering",
file: Target/libsndfile/src/GSM610/short_term.c, line: 293, ... DISPFlagOptimized)
也就是说 file 来自函数 scope，所以 SeaHorn 能打印 short_term.c；但这条优化生成的 IR 指令本身没有具体源码行列，只
带了 line: 0，column 也自然是 0。

对应的真实源码：

```bash
for (i = 0 ; i < 8 ; ++i)
{   va [i]  = v [i] ;                                                 // V = S -> v, 类型i16[]
    rrpa [i] = (float) rrp [i] * scalef ;
    }
while (k--) {
```

report对应源码的关系：

O2 将此循环完全展开并向量化。编译器从 S->v[0..7] 加载数据，分批打包成向量：

!image.png

然后编译器用 shufflevector 链将这些碎片拼装成 va[1..7] 的 <8 x float>（注意不含 va[0]，因为内层循环只需要 va[1..7]）：

```bash
  %51 = insertelement <8 x float> poison, float %13, i64 0
       → [va[1], poison, poison, poison, poison, poison, poison, poison]

  %52 = shufflevector <2 x float> %25, <2 x float> poison,
       <8 x i32> <0, 1, undef, undef, undef, undef, undef, undef>
       → [va[2], va[3], undef, undef, undef, undef, undef, undef]

  %54 = shufflevector <4 x float> %45, <4 x float> poison,
       <8 x i32> <0, 1, 2, 3, undef, undef, undef, undef>
       → [va[4], va[5], va[6], va[7], undef, undef, undef, undef]

  %55 = shufflevector ... → [va[1], va[2], va[3], va[4], va[5], va[6], va[7], undef]
```

SeaHorn 触发告警的原因

SeaHorn 看到了 5 条 "possible read of undefined value"：

!image.png

结论

▎ SeaHorn 不是在说"某个 C 变量没初始化"。 它看到的是 O2 向量化过程中，编译器用 poison/undef
▎ 作为向量拼装时的临时占位符，然后把这些占位符当作"未定义值读取"报了警。

所有 8 个 va[i] 在源码层面都被正确初始化了——for (i=0; i<8; ++i) 全覆盖。但编译器选择用 poison 起步、逐块 shuffle 的方式构造向量，SeaHorn
的抽象解释器不理解这种"先 poison 再填充"的向量化惯用手法，于是爆出 FP。

论文标签：这应该是 FP-Vectorization（向量化误报），根因与"时空错乱"族的 line-zero 坍缩共享同一个上游病理（O2 pass 破坏调试信息），但具体触发机制是
向量化 poison/undef 传播，而非 inline。

### paper-libsndfile-seahorn-04

```bash
Possible read of undefined value at 
--- File   : Target/libsndfile/src/alaw.c
--- Line   : 0
--- Column : 0
--- Bitcode:   %29 = insertelement <4 x float> poison, float %28, i64 0, !dbg !7174
```

真实ir：

```bash
%28 = fmul float %9, %26, !dbg !19110
%29 = insertelement <4 x float> poison, float %28, i64 0, !dbg !19110
%30 = call i32 @llvm.x86.sse.cvtss2si(<4 x float> %29) #48, !dbg !19110

!19110 = !DILocation(line: 0, scope: !19107, inlinedAt: !19101)
!19107 = distinct !DILexicalBlock(scope: !19108, file: !947, line: 342, column: 8)
!19108 = distinct !DILexicalBlock(scope: !19104, file: !947, line: 342, column: 2)
!19101 = distinct !DILocation(line: 518, column: 3, scope: !19088)
!947 = !DIFile(filename: "Target/libsndfile/src/alaw.c", ...)
```

ir对应的源码：

!image.png

原因：

```bash
一：为什么报警
  源码调用链是：
  alaw_write_f2alaw → f2alaw_array → psf_lrintf(normfact * ptr[i])
                                        → _mm_cvtss_si32(_mm_load_ss(&x))
  
  O2 把这三层全部内联。_mm_load_ss 编译为：
  %29 = insertelement <4 x float> poison, float %28, i64 0

  poison 表示"向量高位 1-3 我不关心"——SSE ISA 规定 cvtss2si 只读 XMM 寄存器最低 32 位，高位随便是什么。这是完全正确的 SSE 惯用法。

  但 SeaHorn 不懂。 它的 CanReadUndef pass 检测到 poison operand，当成"未定义的变量被读取"报了警。SeaHorn 源码里连 poison 这个词都没出现过——它对所有 SSE intrinsic 的占位符语义一无所知。
  
二：为什么报line=0
  同一个 SSE intrinsic 在只内联一层时（_mm_load_ss → psf_lrintf，出现在 common.h:967），debug metadata 完好保留，SeaHorn 报了 324 个行号完全正确的同类告警。

  但 case-04 内联了三层，编译器在跨越三层 inline 后无法把向量指令精确映射回某一源代码行，便在 debug metadata 里写了：
  
  !19110 = !DILocation(line: 0, ...)   // ← "我不知道该归到哪行"
  
  SeaHorn 无条件信任 LLVM 的 debug metadata——line: 0 就报 line: 0。它不做任何行号修复。
```

### paper-zfp-seahorn-13

```bash
Possible read of undefined value at 
--- File   : Target/zfp/include/zfp/bitstream.inl
--- Line   : 0
--- Column : 0
--- Bitcode:   %31 = phi i64 [ %22, %25 ], [ %22, %24 ], [ poison, %28 ], !dbg !401
```

应该对应的源码：

```bash
stream_read_bits (bitstream.inl:253-285)
  ─────────────────────────────────────────
  253  inline_ uint64
  254  stream_read_bits(bitstream* s, bitstream_count n)
  255  {
  256    uint64 value = s->buffer;
  257    if (s->bits < n) {                           ← block %12: 判断 s->bits < 64 ?
  258      do {
  261        s->buffer = stream_read_word(s);           ← block %16: 读 word
  262        value += (uint64)s->buffer << s->bits;     ← block %16: 拼入 value → 算出 %22
  263        s->bits += wsize;
  264      } while (...);
  266      s->bits -= n;
  267      if (!s->bits) {
  269        s->buffer = 0;                            ← block %24: 路径A → phi 传 %22
  270      }
  271      else {
  273        s->buffer >>= wsize - s->bits;             ← block %25: 路径B → phi 传 %22
  275        value &= ((uint64)2 << (n - 1)) - 1;
  276      }
  277    }
  278    else {                                        ← block %28: 死代码！！
  280      s->bits -= n;                                ← 只更新了 bits，没算 value
  281      s->buffer >>= n;
  282      value &= ((uint64)1 << n) - 1;               ← n=64 时 (1<<64) 是 UB
  283    }
  284    return value;                                  ← block %30: phi 汇合点
  285  }
  
    三条路汇聚到 return value（block %30）：

  phi:  路径A (line 269)  → value = %22   ✓ 编译器正常算
        路径B (line 275)  → value = %22   ✓ 编译器正常算
        路径C (line 282)  → value = poison  ✗ 死代码, 编译器填 poison
```

为什么报在行号 0？：

这个 phi node 经过了两层内联：

```bash
stream_read_bits (bitstream.inl:257)    ← 内联函数
      ↓ 被内联到
  stream_copy (bitstream.inl:416)         ← 调用者
      ↓ 被内联到
  更上层的调用者
```

O2 在这个深层内联 + DCE 的组合下，丢掉了这条 phi 指令的精确行号映射，在 debug metadata 里写了 line: 0：

!4775 = !DILocation(line: 0, scope: !4438, ...)

SeaHorn 忠实地报：bitstream.inl:0:0 ——文件来自 scope 链解析，行号就是 0。

误报原因：

```bash
  源码层面                           IR 层面                  SeaHorn 视角
  ─────────                        ────────                  ────────────
  stream_read_bits(src, 64)
      │
      ├─ if (s->bits < 64)  ───→  block %16/%24/%25        ✓ 正常执行
      │    (永真)                     value = %22
      │
      └─ else                  ───→  block %28              ✗ 死代码！
           (永假, 含UB)              编译器填 poison
                                         │
                                         ▼
                                    phi: [%22, %22, poison]  → SeaHorn 报警！
                                         │                    "possible read of
                                         ▼                    undefined value at
                                    !dbg = line: 0            bitstream.inl:0:0"

解释：O2 在编译时发现：当 n=64 时，else 分支的条件 s->bits >= 64 在 bitstream 不变式约束下永远为假。于是 O2 把这条分支当作死代码消除。但因为 SSA 的 phi node 必须给每个前驱基本块一个值，编译器就在那条死边上填了 poison（"反正走不到，随便填"）。SeaHorn 不懂路径可行性，看见 poison 就当未定义使用报了警。

关键点在于 poison 不是 LLVM 对"死代码"的标记，而是对"这条 phi 入边永远走不到"的占位。死代码本身已经被 DCE 删了，但 phi node 的入边还在，需要一个值——编译器懒得算，填了 poison。
```

## paper-libsndfile-dg-05

dg没有行号映射逻辑，它无条件相信IR的debug metadata

dg也不会输出bug，它输出的

```bash
  程序源码 (.c)
      │
      ▼ clang -O2 -g -emit-llvm
  LLVM bitcode (.bc)
      │
      ├── PTA ──→ 指针指向关系 (谁指向谁)
      │              │
      │              ▼
      ├── DDA ──→ 数据依赖关系 (值从哪来) —— 依赖 PTA 的结果
      │
      └── CDA ──→ 控制依赖关系 (谁控制谁) —— 不依赖 PTA

一、PTA（Points-To Analysis）—— "这个指针指向谁？"
  
  输出格式（--c-lines 模式）：
  
  46:13                     ← 源码位置：某指针
    -> 46:13                ← 指向自己（alloca 出来的局部变量）
    -> null                 ← 也可能指向 null
    -> fun 'sds_2byte_read' ← 也可能指向某个函数的返回值

  含义：对 line:col 处的每个指针/内存操作，列出它可能指向的所有内存对象——另一个 alloca、一个全局变量、malloc 的返回值、甚至 null。

  用来干什么：
  - 别名分析的基础：判断两个指针是否可能指向同一块内存
  - 给 DDA 提供"这个 store 可能写到哪些内存"的信息
  - 给切片器提供"哪些指令可能影响这个值"的信息
  
  ---
二、DDA（Data Dependence Analysis）—— "这个值是从哪来的？"

  输出格式：

  use_line:col  <-  def_line:col
  读操作          写操作（值的来源）

  含义：每条"读内存"的操作，列出所有可能给它写入了当前值的"写内存"操作。本质是 Memory SSA——把 flat 的内存访问组织成 def-use 链。

  用来干什么：
  - 程序切片：从 sink 点回溯到 source 点
  - 污点分析：追踪污染数据从输入到危险操作的路径
  - 漏洞检测：判断未初始化内存是否被读取
  
  ---
三、CDA（Control Dependence Analysis）—— "这段代码受谁控制？"

  输出格式：

  controlling_branch  ->  dependent_instruction
  控制者（分支）           被控制者

  例如 case-05 的输出：
  0:0 -> 313:15       ← 一个未知位置的分支，控制着 313:15 是否执行
  314:2 -> 313:15     ← 314 行的代码，控制着 313:15 是否执行
  318:13 -> 313:15    ← 318 行的代码，控制着 313:15 是否执行

  含义：313:15 处的指令是否执行，取决于这三个位置的条件分支的结果。
  
  用来干什么：
  - 程序切片：找到所有影响目标语句执行的条件
  - 理解程序控制结构
  - 测试用例生成：找到覆盖某行代码需要满足的所有条件
```

搞清楚dg输出的内容，再来看case：

raw的原生输出：

!image.png

```bash
第一步：DG 是怎么拿到行号的
  
  DG 三个 dump 工具里的代码完全一样：

  // llvm-cda-dump.cpp:120-124
  const auto &DL = I->getDebugLoc();     // ← 直接读 LLVM debug metadata
  if (DL) {
      ro << DL.getLine() << ":" << DL.getCol();  // ← line=0 → 输出 "0:0"
  }
  
  DG 没有自己的行号计算逻辑。 它无条件信任 IR 上的 debug metadata。metadata 写 line: 0，DG 就输出 0:0。

第二步：metadata 里为什么是 line: 0

  整个 libsndfile 的 .ll 文件里有 2535 个 line: 0 的 DILocation。但其中只有 4 个是条件分支指令（CDA 追踪控制依赖就是追踪到条件分支上）。

  这 4 个的 metadata 结构完全一致：

  !42042 = !DILocation(line: 0, scope: !41936, inlinedAt: !42036)
                      ^^^^^^            ^^^^^^           ^^^^^^
                      行号=0          被内联的函数      被内联到的位置

  展开追踪：

  !42042 = !DILocation(line: 0, scope: !41936, inlinedAt: !42036)

  scope: !41936 = DISubprogram(
      name: "aiff_read_header",          ← 被内联的函数
      file: "Target/libsndfile/src/aiff.c",
      line: 398,
      spFlags: DISPFlagOptimized)        ← 被 O2 优化过的标志

  inlinedAt: !42036 = DILocation(
      line: 249, column: 17,             ← 被内联到的调用位置
      scope: aiff.c:249)
  
  翻译成人话：

O2 把 aiff_read_header（定义在 aiff.c:398）内联到了 aiff.c:249。内联后 O2 对这个函数的控制流做了变换（CFG Simplify/InstCombine/Jump Threading），变换后的一个条件分支无法被精确映射回 aiff_read_header 中的某一行源码，编译器就在 metadata 里写了 line: 0。

第三步：为什么是 0:0 -> 313:15
  
  CDA 追踪控制依赖到那个 line: 0 的条件分支：
  
  O2 生成的条件分支 (line:0, aiff_read_header 的内联副本)
          │
          │ 控制依赖 (CDA 计算得出)                       **这个计算略微麻烦点，在下一个图中**
          ▼
  line 313:15 处的指令 (command.c / file_io.c)
  
  DG 报告这条边时：
  
  源码 (0:0)    ──控制依赖──→    目标 (313:15)
     ↑                                ↑
  getLine()=0                    getLine()=313
  getCol()=0                     getCol()=15
  
  

```

line=0是怎么来的：

```bash
已验证：0:0 -> 313:15 的真实来源
  
第一层：0:0 怎么来的

  两个函数都满足条件，以 psf_calc_signal_max（command.c:296）为例：

  ; .ll:11905
  define double @psf_calc_signal_max(...) !dbg !11812 {
    ; 函数入口 — 3 个 dbg.value，全部是 0:0
    call void @llvm.dbg.value(...), !dbg !11840    ; ← 0:0
    call void @llvm.dbg.value(...), !dbg !11840    ; ← 0:0
    ...
    ; block %16 — 313:15 的 sf_command 调用
    %17 = tail call i32 @sf_command(...), !dbg !11860  ; ← 313:15
    call void @llvm.dbg.value(metadata i32 %17, ...), !dbg !11840  ; ← 又是 0:0
    ...

  metadata 链：

  !11840 = !DILocation(line: 0, scope: !11812)     ← line=0, 直接 scope 到函数本身
  !11860 = !DILocation(line: 313, column: 15, scope: !11812)  ← 正常行号

  !11812 = DISubprogram(
      name: "psf_calc_signal_max",
      file: !886 = "Target/libsndfile/src/command.c",
      line: 296,
      spFlags: DISPFlagOptimized)

  对应源码 command.c:296-313：

  296: double psf_calc_signal_max(SF_PRIVATE *psf, int normalize) {
           ...
  308:     if (!psf->read_double) { ... }
  313:     save_state = sf_command((SNDFILE*) psf, SFC_GET_NORM_DOUBLE, NULL, 0);
           ^^^^^^^^
           column 15

第二层：真实 CFG

  psf_calc_signal_max(command.c:296)
    │
    ├─ dbg.value(psf)      ← !dbg !11840 (0:0) ── 参数标记
    ├─ dbg.value(normalize) ← !dbg !11840 (0:0)
    ├─ dbg.declare(buf)    ← valid line
    │
    ▼
  block %2:  psf->read_double == 0 ?
    │
    ├── true  → block %8:   error = 40 → return 0.0
    │
    └── false → block %10:  psf->read_double == NULL ?
                   │
                   ├── true  → block %14:  error = 18 → return 0.0
                   │
                   └── false → block %16:
                                 %17 = sf_command(SFC_GET_NORM_DOUBLE)  ← !dbg !11860 (313:15)
                                 dbg.value(%17)                          ← !dbg !11840 (0:0)
                                 %18 = sf_command(SFC_SET_NORM_DOUBLE)
                                 position = sf_seek(SEEK_CUR)
                                 sf_seek(SEEK_SET)
                                 ...
                                 br → block %46 (主循环)

第三层：DG 如何输出 0:0

  DG 的 dumpCda() 遍历 psf_calc_signal_max:

    for each instruction I in function:
      deps = cda.getDependencies(&I)   // DOD 算法计算 I 依赖于哪些节点
      for each dep in deps:
        print getInstName(&I) + " -> " + getInstName(dep)

  当 I = dbg.value (debug loc = 0:0)
     dep = sf_command (debug loc = 313:15)

  → getInstName(dbg.value) = I->getDebugLoc().getLine() + ":" + .getCol()
                           = 0 + ":" + 0
                           = "0:0"

  → getInstName(sf_command) = "313:15"

  → 输出: "0:0 -> 313:15"

  getInstName() 源码（llvm-cda-dump.cpp:120-124）：

  const auto &DL = I->getDebugLoc();    // ← O2 写了 line:0 的 metadata
  if (DL) {
      ro << DL.getLine() << ":" << DL.getCol();  // → "0:0"
  }

  完整因果链：

  O2 编译 psf_calc_signal_max (command.c:296)
      │
      ▼
  O2 生成 dbg.value 内联函数追踪指令，但无法精确映射回某个源码行
      │
      ▼
  LLVM 写入 metadata: !DILocation(line: 0, scope: psf_calc_signal_max)
      │  （注意：scope 直接是函数本身，不是内联进来的——这是 O2 对函数自身代码的行号坍缩）
      ▼
  DG 的 CDA DOD 分析为这个 dbg.value (0:0) 计算出控制依赖边 → sf_command (313:15)
      │
      ▼
  DG 调用 I->getDebugLoc().getLine() → 0（dbg.value）和 313（sf_command）
      │
      ▼
  输出 "0:0 -> 313:15"

  与前几个 case 的对比

  ┌─────────────┬──────────────────────────┬─────────────────────────────────┬───────────────────────────────────────┐
  │             │  SeaHorn case-13 (zfp)   │ SeaHorn case-03/04 (libsndfile) │        DG case-05 (libsndfile)        │
  ├─────────────┼──────────────────────────┼─────────────────────────────────┼───────────────────────────────────────┤
  │ line:0 来自 │ 内联函数分支 (inlinedAt) │ 内联函数分支/SSE intrinsic      │ 函数自身的 dbg.value (scope=函数本身) │
  ├─────────────┼──────────────────────────┼─────────────────────────────────┼───────────────────────────────────────┤
  │ 内联相关    │ 是（三重内联）           │ 是（三重/单层内联）             │ 否——scope 直接是函数本体              │
  ├─────────────┼──────────────────────────┼─────────────────────────────────┼───────────────────────────────────────┤
  │ O2 坍缩机制 │ CFG 变换后无法映射       │ 向量化/SSE 后无法映射           │ dbg.value 无法映射回源码行            │
  └─────────────┴──────────────────────────┴─────────────────────────────────┴───────────────────────────────────────┘

  核心结论不变：不管 line:0 的具体来源是什么（内联分支、SSE intrinsic、dbg.value），根因完全相同——O2 优化后无法把 IR 指令精确映射回源码行，在 metadata 里写了 line: 0，工具无条件信任 metadata 就输出 0:0。
```

## paper-libsndfile-dg-06

```bash

  ═══════════════════════════════════════════════════════════════════════════════
  第 1 层：源码 —— aiff_read_header 被 O2 内联
  ═══════════════════════════════════════════════════════════════════════════════

    aiff.c:398  static int aiff_read_header(...)
                {
                  ...
                  /* 各种分支判断：格式检查、采样率、位深度等 */
                  if (position < data_size - 8) {     ← 原始的分支
                    /* 读取数据 */
                  }
                  ...
                }

    aiff.c:249  static int aiff_open(...)
                {
                  ...
                  aiff_read_header(psf);              ← 调用点，O2 把整个函数体内联进来了
                  ...
                }

  ═══════════════════════════════════════════════════════════════════════════════
  第 2 层：IR —— O2 内联 + CFG 变换后的产物
  ═══════════════════════════════════════════════════════════════════════════════

    aiff_open 函数体内 (libsndfile_convert.ll:64013):

    %1019:                                            ← 来自被内联的 aiff_read_header
      %1020 = call @psf_ftell(...)                    ← 获取当前文件位置
      %1021 = load i64, i64* %55                      ← 加载 data_size
      %1022 = add nsw i64 %1021, -8                   ← data_size - 8
      %1023 = icmp slt i64 %1020, %1022               ← position < data_size - 8 ?

      br i1 %1023, label %1031, label %1026, !dbg !42042
      │              │            │            │
      │              │            │            └── debug location 指向 !42042
      │              │            └── false: 跳过数据读取，走 cleanup
      │              └── true: 继续读数据
      └── 条件分支

  ═══════════════════════════════════════════════════════════════════════════════
  第 3 层：Metadata —— O2 为什么写 line: 0
  ═══════════════════════════════════════════════════════════════════════════════

    !42042 = !DILocation(line: 0, scope: !41936, inlinedAt: !42036)
               ^^^^^^
               行号 = 0 ← O2 放弃了！

    展开这个 metadata 链条：

    !42042 ──┬── line: 0          ← "我不知道这是哪一行"
             ├── scope: !41936 ─── DISubprogram(name: "aiff_read_header")
             │                     file: aiff.c, line: 398
             │                     spFlags: DISPFlagOptimized ← O2 优化过的标志
             │
             └── inlinedAt: !42036 ── DILocation(line: 249, column: 17)
                                      scope: aiff.c:249
                                      ↑
                                      "aiff_read_header 被内联到 aiff.c:249"

    O2 为什么放弃写行号？

    原始 aiff_read_header 中的分支                        内联 + O2变换后的 IR
    ┌──────────────────────────┐                    ┌──────────────────────────┐
    │ if (position < size - 8) │  ── O2 ──→         │ %1023 = icmp slt ...     │
    │   read_data();           │  内联+CFG变换       │ br i1 %1023, ...         │
    │ else                     │                    │                          │
    │   skip();                │  这条 br 指令融入了   │ 原本分散在多行的逻辑     │
    └──────────────────────────┘  循环展开、Jump       │ 被压缩成一条 IR 指令     │
                                 Threading 的效果    │ LLVM 无法把它映射回      │
                                                     │ aiff_read_header 中的   │
                                                     │ 某一个具体行             │
                                                     └──────────────────────────┘
                                                     → 写 line: 0

  ═══════════════════════════════════════════════════════════════════════════════
  第 4 层：DG —— 怎么从 line: 0 变成 "0:0"
  ═══════════════════════════════════════════════════════════════════════════════

    DG 源码 llvm-cda-dump.cpp:85-95:

    static std::string getInstName(const llvm::Value *val) {
        ...
        const auto &DL = I->getDebugLoc();    // ① 拿 LLVM debug location
        if (DL) {
            ro << DL.getLine() << ":" << DL.getCol();  // ② line=0, col=0 → 输出 "0:0"
        }
    }

    调用链：

    dumpCda() → 遍历每个函数每个BB每条指令
      → cda.getDependencies(&I) → 返回控制依赖源（branch 指令 dep）
      → cout << getInstName(&I) << " -> " << getInstName(dep)
               │                              │
               │                              └── dep->getDebugLoc().getLine() = 0
               │                                  dep->getDebugLoc().getCol()  = 0
               │                                  输出 "0:0"
               │
               └── I->getDebugLoc().getLine() = 113
                   I->getDebugLoc().getCol()  = 2
                   输出 "113:2"

    输出行: 0:0 -> 113:2

  ═══════════════════════════════════════════════════════════════════════════════
  第 5 层：为什么 113:2 对应 4 个文件
  ═══════════════════════════════════════════════════════════════════════════════

    getInstName 对目标指令也做了相同的操作:

    I->getDebugLoc().getLine() → 113
    (*I->getDebugLoc()).getFilename() → 返回 scope 链中的文件名

    但由于这行代码来自被内联的公共函数（在 4 个编译单元中都被内联了），
    同一个 line:col 解析出 4 个不同的文件:

    ┌────────────────────────────┬──────────────────────────────────┐
    │ ALACBitUtilities.c:113     │ BitBufferPeek 位操作             │
    │ g721.c:113                 │ ADPCM 解码器 update() 调用       │
    │ avr.c:113                  │ AVR 文件头读取                   │
    │ common.c:113               │ psf_log_printf 格式解析          │
    └────────────────────────────┴──────────────────────────────────┘

  ═══════════════════════════════════════════════════════════════════════════════
  一图总结
  ═══════════════════════════════════════════════════════════════════════════════

    aiff.c 源码                    LLVM IR                    DG 输出
    ──────────                    ────────                   ────────

    aiff_read_header()             br i1 %1023,
       │                            label %1031,             0:0 → 113:2
       │ O2内联                      label %1026,              ↑      ↑
       ▼                            !dbg !42042               │      │
    aiff_open()                          │                    │      │
       │                                  │                    │      └─ 目标
       │ O2 CFG变换                       ▼                    │        指令的
       │ + 循环展开            !42042 = DILocation(            │        debug
       │ + JumpThreading          line: 0,  ← O2放弃了        │        loc
       ▼                         scope: aiff_read_header,      │
    合并后的 CFG                  inlinedAt: aiff.c:249)        │
       │                              │                        │
       │                              │ DG 读到 line=0         │
       ▼                              ▼                        │
    ┌──────────────────────┐    getLine() → 0            ──────┘
    │ br i1 %1023, ...     │    getCol()  → 0
    │ 这个分支在 aiff_read_ │    → 输出 "0:0"
    │ header 里找不到精确   │
    │ 对应的源码行          │
    └──────────────────────┘

  根因就是一句话：O2 把 aiff_read_header 内联进 aiff_open 后，对合并的 CFG 做了变换。变换后的条件分支 br i1 %1023 无法被精确映射回 aiff_read_header 中的某一个源码行，LLVM 在 debug metadata 里写了 line: 0。DG
  无条件读取这个 metadata，输出 0:0。

```

## paper-libsndfile-dg-15

此case与内联无关，O2 把 zfp_read_header 函数中所有 dbg.value 的 debug location 写成了 line: 0。

```bash

  0:0 -> 1278:10 完整追踪
  
  第一层：整个函数的 dbg.value 全是 0:0

  zfp_read_header（zfp.c:1265，98行 IR，.ll:7573-7670）中所有 dbg.value 都用同一个 metadata：

  ; .ll:7574-7577 — 函数入口
  call void @llvm.dbg.value(metadata %struct.zfp_stream* %0, ...), !dbg !4267  ; 0:0
  call void @llvm.dbg.value(metadata %struct.zfp_field* %1, ...), !dbg !4267  ; 0:0
  call void @llvm.dbg.value(metadata i32 %2, ...), !dbg !4267                 ; 0:0
  call void @llvm.dbg.value(metadata i64 0, ...), !dbg !4267                  ; 0:0

  metadata 链：

  !4267 = !DILocation(line: 0, scope: !4250)

  !4250 = DISubprogram(
      name: "zfp_read_header",
      file: !82 = "Target/zfp/src/zfp.c",
      line: 1265,
      spFlags: DISPFlagOptimized)

  O2 把这个函数里所有 dbg.value 的行号全部写成了 0——不是某个内联进来的分支，是整个函数自己的 debug 信息被碾碎了。

  第二层：真实 CFG 和依赖边

  zfp_read_header (zfp.c:1265)

  block %3:  dbg.value(0:0)×4 ── 参数初始化
    │
    br: mask & ZFP_HEADER_MAGIC ?
    │
    ├── false → block %23
    └── true  → block %6:  读 'z' 'f' 'p' version → block %23
                  │
  block %23:  dbg.value(0:0) ── bits 计数
    │
    br: mask & ZFP_HEADER_META ?
    │
    ├── false → block %34
    └── true  → block %27:
                  %30 = stream_read_bits(52)               ; 读 meta
                  dbg.value(0:0) ── meta 值
                  %31 = zfp_field_set_metadata(...)        ; ← 1278:10
                  %32 = icmp eq i32 %31, 0
                  dbg.value(0:0) ── bits 计数(undef)
                  br i1 %32, label %57, label %34           ; ← 条件分支
                            │              │
                        return 0      block %34:
                                        dbg.value(0:0) ── bits 更新    ← 这个 0:0
                                                                        被 1278:10 控制！

  第三层：为什么 DG 报 0:0 -> 1278:10

  block %34 中的 dbg.value 执行路径：

    block %27:
      br i1 %32, label %57, label %34
           │                │
      true (失败)      false (成功)
           │                │
      走 %57 return    走 %34 → dbg.value(0:0) 执行 ✓

  DG 的 CDA 计算：
    block %34 的后支配前沿 = { block %27 }
    → block %34 控制依赖于 block %27
    → block %34 中每条指令都控制依赖于 block %27 的 terminator (br i1 %32)

  dumpCda() 遍历 block %34 中的指令：
    for I in block %34:
      for dep in cda.getDependencies(&I):
        print getInstName(&I) + " -> " + getInstName(dep)

  当 I = dbg.value (debug loc = 0:0)
     dep = br i1 %32 (debug loc = 1278:10)

  → "0:0 -> 1278:10"

  DG 算的是对的——block %34 中的 bits 跟踪代码确实受 1278:10 处的 zfp_field_set_metadata 返回值控制。如果 metadata 设置失败，整个 block %34 被跳过，bits 不会被更新。

  唯一的问题：O2 把那个 dbg.value 的行号写成了 0，所以 DG 报的是 0:0 而不是 1266:X（函数内某行）。

  完整因果链

  O2 编译 zfp_read_header (zfp.c:1265)
      │
      ▼
  stream_read_bits、zfp_field_set_metadata 等函数被内联
      │
      ▼
  O2 在内联+优化后无法把 dbg.value 追踪指令映射回具体源码行
      │
      ▼
  LLVM 写入: !DILocation(line: 0, scope: zfp_read_header)
      │  （整个函数所有 dbg.value 共用同一个 line:0）
      ▼
  DG CDA 正确计算: block %34 控制依赖于 br at 1278:10
      │
      ▼
  DG 读出 dbg.value 的 debug loc → 0:0
  DG 读出 br 的 debug loc → 1278:10
      │
      ▼
  输出: "0:0 -> 1278:10"

  一句话：
  CDA 算的控制依赖边完全正确。O2 把 zfp_read_header 中所有 dbg.value 的行号碾成了 0，DG 读到 0 就输出 0。
```

## paper-libsndfile-dg-16

```bash
 zfp case-16: 为什么报 0:0 → 143:7
  
第1层：谁是 line:0 的源头

  zfp.ll 里只有5个条件分支携带 line:0 的 debug location，全部来自同一个函数：

  zfp_field_dimensionality (zfp.c:245)

  uint
  zfp_field_dimensionality(const zfp_field* field)
  {
    return field->nx ? field->ny ? field->nz ? field->nw ? 4 : 3 : 2 : 1 : 0;
         ^^^^^^^^^^  ^^^^^^^^^^  ^^^^^^^^^^  ^^^^^^^^^^
         分支1(!669) 分支2(!731) 分支3(!761) 分支4(!828)    ← 4个嵌套三元 ?:
  }

  O2 把这条单行嵌套三元表达式内联到了 4 个调用点：

  ┌──────────┬──────────────────────────────────────────┐
  │ 分支 dbg │              内联到的调用点              │
  ├──────────┼──────────────────────────────────────────┤
  │ !669     │ zfp.c:252 — zfp_field_size() 中的 switch │
  ├──────────┼──────────────────────────────────────────┤
  │ !731     │ zfp.c:282 — zfp_field_blocks() 中        │
  ├──────────┼──────────────────────────────────────────┤
  │ !761     │ zfp.c:295 — zfp_field_stride() 中        │
  ├──────────┼──────────────────────────────────────────┤
  │ !828     │ zfp.c:323 — zfp_field_metadata() 中      │
  ├──────────┼──────────────────────────────────────────┤
  │ !1593    │ zfp.c:282 → 再内联一层                   │
  └──────────┴──────────────────────────────────────────┘

  5 个 line:0 的 metadata 结构完全一致：

  !669 = !DILocation(line: 0, scope: !645, inlinedAt: !670)
         ^^^^^^
         行号=0

  !645 = DISubprogram(
      name: "zfp_field_dimensionality",
      file: "Target/zfp/src/zfp.c", line: 243,
      spFlags: DISPFlagOptimized)      ← O2 优化标志

  !670 = DILocation(line: 252, column: 13)  ← 被内联到的位置

第2层：为什么这一行会产生 line:0

  源码（一行）                        O2 内联 + CFG 变换后
  ─────────────────────              ─────────────────────
  field->nx                          %19 = icmp eq i64 %18, 0     ← 取 nx
    ? field->ny                      br i1 %19, label %23, %20    ← 分支
      ? field->nz              →     %22 = icmp eq i64 %15, 0     ← 取 ny
        ? field->nw                  br i1 %22, label %25, %28    ← 分支
          : 4                       ...（4个分支全部展开）
        : 3
      : 2                            O2 把这行嵌套三元符展开成 4 个独立
    : 1                              的 br 指令，散布在合并后的 CFG 中。
  : 0                                LLVM 无法把每个 br 映射回原本那一行，
                                     全部写 line: 0

第3层：143:7 是什么

  143:7 = if (field) 来自 zfp_field_alloc()：

  zfp_field*
  zfp_field_alloc(void)
  {
    zfp_field* field = malloc(sizeof(zfp_field));
    if (field) {              ← 143:7
      field->type = zfp_type_none;
      ...
    }
    return field;
  }

  zfp_field_alloc 被内联进 zfp_field_1d、zfp_field_2d 等函数，这些函数又可能进一步被内联。某个最终的合并函数中，同时存在：
  - 来自 zfp_field_dimensionality 的 line:0 分支
  - 来自 zfp_field_alloc 的 143:7 指令

  ---
  图解

  zfp.c 源码                        LLVM IR                    DG 输出
  ──────────                       ────────                   ────────

  zfp_field_dimensionality          br i1 %19, label %23,
    (zfp.c:245)                        label %20,              0:0 → 143:7
    field->nx ? ... : 0              !dbg !669                  ↑      ↑
         │                                │                    │      │
         │ O2 内联到                      │                    │      │
         │ zfp_field_size                 ▼                    │      │
         │ (zfp.c:252)          !669 = DILocation(             │      │
         │                          line: 0, ← O2放弃          │      │
         │ O2 展开嵌套三元          scope: zfp_field_          │      │
         │ → 4 个独立 br               dimensionality,         │      │
         │                          inlinedAt: zfp.c:252)      │      │
         ▼                             │                       │      │
    合并的 CFG                         │ getLine()=0            │      │
         │                             │ getCol()=0             │      │
         │                             ▼                       │      │
         │                       DG 输出 "0:0"        ─────────┘      │
  zfp.c 源码                        LLVM IR                    DG 输出
  ──────────                       ────────                   ────────

  zfp_field_dimensionality          br i1 %19, label %23,
    (zfp.c:245)                        label %20,              0:0 → 143:7
    field->nx ? ... : 0              !dbg !669                  ↑      ↑
         │                                │                    │      │
         │ O2 内联到                      │                    │      │
         │ zfp_field_size                 ▼                    │      │
         │ (zfp.c:252)          !669 = DILocation(             │      │
         │                          line: 0, ← O2放弃          │      │
         │ O2 展开嵌套三元          scope: zfp_field_          │      │
         │ → 4 个独立 br               dimensionality,         │      │
         │                          inlinedAt: zfp.c:252)      │      │
         ▼                             │                       │      │
    合并的 CFG                         │ getLine()=0            │      │
         │                             │ getCol()=0             │      │
         │                             ▼                       │      │
         │                       DG 输出 "0:0"        ─────────┘      │
         │                                                             │
         │                                                    zfp_field_alloc
         │                                                    的 inlined 副本
         │                                                    line=143, col=7
         │                                                    → "143:7"

  和 libsndfile case-05/06 对比

  两个 case 的根因完全相同：O2 内联了一个小函数 → 展开了其内部控制流 → 展开后的分支指令在原始函数中找不到对应的唯一源码行 → LLVM 写 line: 0 → DG 读出来 0:0。
```

## paper-libsndfile-cclyzerpp-07

这几个cases都有点不对劲，需要重新分析

```bash

  instr_pos.csv.gz 中 (0,0) 条目
      │
      ├── 第1步：拿到 refmode，如 <llvm-link>:aiff_open:5
      │
      ├── 第2步：去 .ll 文件找到 aiff_open 函数，定位第 5 条指令
      │
      ├── 第3步：读这条指令的 !dbg metadata 链路
      │         !XXXX = !DILocation(line: 0, scope: ..., inlinedAt: ...)
      │
      ├── 第4步：判断根因
      │         scope 是被内联的小函数？ → 内联导致 debug 坍缩
      │         scope 是当前函数本身？   → CFG 变换导致 debug 坍缩
      │         没有 inlinedAt？         → 函数的顶层代码被 O2 优化破坏
      │
      └── 第5步：找到真实源码位置
                如果 inlinedAt 存在 → 追到调用点
                如果只有 scope → scope 的函数定义行

```

```bash
 案例: paper-libsndfile-cclyzerpp-07
  
  结论: 工具误报 (Tool False Positive) — cclyzer++ 的文件解析 Bug 导致正确的 debug metadata 被映射到错误的源文件。

  根因链

  两个 common.c (src/ & programs/)  →  os.walk 按字母序, src/ 先被索引
      →  resolve_difile() 优先取 source_index basename 匹配
      →  dedup_paths()[0] = src/common.c (错误!)
      →  src/common.c:193 是空行 → ColumnOutOfRange
      →  phi_instr 流水线标记为 Wanted-PhiMergeLocationDrift (误导)

  生成的文档

  - case.md — 更新了 Paper-Ready Narrative
  - verification.md — 完整验证报告，verdict: exact（当文件正确解析时）
  - llm_output.md — 完整的 LLM recovery JSON 输出
  - root_cause_analysis.md — 全新的逐层根因分析文档（从原生输出→元数据解析→文件映射→列验证→分类的完整链条）

```

!image.png

## paper-libsndfile-cclyzerpp-08

这个属于当时codex分析的误报

```bash
Case-08：从原生输出到 ColumnOutOfRange 的完整根因链

  ---
  第 1 层：cclyzer++ 原生输出（Datalog relations）
  
  cclyzer++ 对这条指令输出了 8 条 Datalog 事实，全部没有行号列号：
  
  phi_instr:             <llvm-link>:sfe_apply_metadata_changes:367
  phi_instr_npairs:      <llvm-link>:sfe_apply_metadata_changes:367    2
  phi_instr_type:        <llvm-link>:sfe_apply_metadata_changes:367    i32
  phi_instr_pair_label:  <llvm-link>:sfe_apply_metadata_changes:367    0    [basicblock]%30
  phi_instr_pair_label:  <llvm-link>:sfe_apply_metadata_changes:367    1    [basicblock]%294
  phi_instr_pair_value:  <llvm-link>:sfe_apply_metadata_changes:367    0    ...:367:0:1
  phi_instr_pair_value:  <llvm-link>:sfe_apply_metadata_changes:367    1    ...:%288
  
  instr_pos:             (不存在！这条指令没有位置记录)

  关键事实：instr_pos.csv.gz 里根本没有 sfe_apply_metadata_changes:367 这一行。cclyzerpp 告诉你"有个 phi 节点，2 个入边"，但不告诉你这个 phi 在源码哪里。

  ---
  第 2 层：.ll 文件中的 debug metadata

  去 .ll 文件找到 sfe_apply_metadata_changes 函数，定位指令索引 367：
  
  ; .ll 行 130266-130268
    %289 = icmp eq %struct.sf_private_tag* %21, null, !dbg !87442
    %290 = icmp eq %struct.sf_private_tag* %21, %22          ← 没有 !dbg
    %291 = select i1 %289, i1 true, i1 %290, !dbg !87444    ← 这条

  其中 %290 = icmp eq ... %22 没有 !dbg——O2 已经丢了它的 debug location。

  metadata 完整链路：

  !87444 = !DILocation(line: 289, column: 22, scope: !87443)
             ↑                    ↑
           行号 289             列号 22

  !87443 = DILexicalBlock(scope: !87069, file: !3908, line: 289, column: 6)
  !87069 = DISubprogram(name: "sfe_apply_metadata_changes", line: 234)
  !3908  = DIFile("Target/libsndfile/programs/common.c")    ← 真实文件

  ---
  第 3 层：映射到源码——两次错误叠加

  错误 1：cclyzerpp 不记录这条指令的位置
  
  cclyzerpp 把 select 指令归入了 phi_instr 表。对于 phi 类型，instr_pos 的覆盖率只有 34.2%——另外 65.8% 不写位置。这条指令恰好落在 65.8% 里。

  错误 2：外部脚本的文件解析错误
  
  analyze_native_value_cases.py 的 parse_entity() 从 refmode 中提取函数名 sfe_apply_metadata_changes，然后在源码树中搜索这个函数。它找到了两个文件都包含这个函数：
  - Target/libsndfile/programs/common.c ← 正确的
  - Target/libsndfile/src/common.c ← 同名但不同文件

  脚本选了 src/common.c。

  ---
  第 4 层：为什么触发 ColumnOutOfRange
  
  Debug metadata:     programs/common.c:289:22
                                          ^^
                                col 22 = '&' (&& 运算符)
                                行长 43 字符，col 22 有效
                                语义：短路与的空指针检查
  
  脚本解析:           src/common.c:289:22
                                     ^^^^^^
                                该行只有 20 个字符
                                col 22 越界！
                                该行是 { tens *= 10 ;（乘法赋值）

  !87444 ──→ programs/common.c:289:22  ← O2 正确保留了 debug 位置
                if (outfile != NULL && outfile != infile)
                                   ^^
                             col 22 = &&（短路与）
                             select 指令实现的正是这个逻辑

  BUT 脚本解析 ──→ src/common.c:289:22  ← 错误文件！
                    {   tens *= 10 ;
                        ↑
                    col 22 不存在（行太短）
                    语义：乘法赋值，和 select 毫无关系

  ---
  根因总结
  
  ┌─────────────────────────────────────────────────────────┐
  │ 根因 1: cclyzerpp FactGenerator                         │
  │   • 把 select 指令归入 phi_instr（不是 select_instr）     │
  │   • phi_instr 中的指令有 65.8% 不写 instr_pos            │
  │   • 这条指令恰好没有 instr_pos                           │
  │   → 原生输出不包含行号列号                                │
  ├─────────────────────────────────────────────────────────┤
  │ 根因 2: O2 优化                                         │
  │   • CFG Simplification 把 if 条件替换为 select 指令       │
  │   • %290 = icmp eq psf1, psf2 的 debug loc 丢了          │
  │   • 但 select 指令本身保留了正确的 !87444                 │
  │   → O2 这次没丢行号，但丢了中间操作数的 debug loc           │
  ├─────────────────────────────────────────────────────────┤
  │ 根因 3: 外部脚本文件解析                                  │
  │   • 函数名 "sfe_apply_metadata_changes" 存在两个文件中    │
  │   • 脚本选了 src/common.c 而不是 programs/common.c       │
  │   • src/common.c:289 只有 20 个字符，col 22 越界          │
  │   → ColumnOutOfRange                                    │
  └─────────────────────────────────────────────────────────┘

  三个根因任何一个不存在，这个 case 都不会出现：如果 cclyzerpp 写了 instr_pos → 直接有位置；如果 O2 没丢 %290 的 debug loc → 列号可能不同；如果脚本选了正确的文件 → 列号 22 有效，指向 && 运算符，语义匹配。

```

## paper-zfp-cclyzerpp-17

同上，需要纠正

## paper-zfp-cclyzerpp-18

同上，需要纠正

## paper-libsndfile-yapall-09

```bash

  yapall 原始输出（第 384,897 行）:
  ┌─────────────────────────────────────────────────────────────────┐
  │ invalid_load   sfe_apply_metadata_changes:0   *@codec_close     │
  └─────────────────────────────────────────────────────────────────┘
         │                    │                         │
         ▼                    ▼                         ▼
    问题类型            有问题的操作数              points-to 目标
    (存储/加载/调用      (函数:索引, 其中          (yapall 认为操作数
     不精确性)          索引=函数参数)              可能指向的位置)
         │                    │                         │
         │                    ▼                         ▼
         │           IR: %0 = filenames           @codec_close 是一个
         │           参数 (const char**)          存储在 SF_PRIVATE
         │                                        中的函数指针
         │                    │                         │
         │                    └─────────┬───────────────┘
         │                              │
         ▼                              ▼
    根本原因:                    为什么它们混叠:
                !87128 = !DILocation(line: 0, scope: !87126)
                            ↑
                      报告位置: common.c:0

  yapall 的 issues 输出按 operand（其 points-to 集 "无效" 的 SSA 值/参数）聚合，而不是按
  instruction（执行加载/存储/调用/内存复制的指令）。这对于数据流分析是正确的（points-to
  是操作数的属性，而不是指令的属性），但意味着额外的步骤——通过 SSA
  使用-定义链找到使用该操作数的所有指令——对于源位置映射是必要的。
```

yapall 的原始输出（日志第 384,897 行）是：

invalid_load  sfe_apply_metadata_changes:0    *@codec_close

没有文件，没有行，没有列 — 只有 kind、operand、allocation。我们之前确认过：原始日志中匹配 line、column、!dbg 或 DILocation 的有 0 行。

```bash
原始输出

  invalid_load  sfe_apply_metadata_changes:0    *@codec_close

  三个字段。只有操作数 sfe_apply_metadata_changes:0 参与映射。kind 告诉你查找哪种指令（load），allocation 告诉你原因（函数指针）。

第 1 步：操作数是一个参数

  : 之前的部分是函数名，之后的部分是参数索引。yapall 如何生成这个标识符的：

  // llvm/name.rs:182-196 — ParameterName::name():
  // parent_function.0 + ":" + param_name
  // = "sfe_apply_metadata_changes" + ":" + "0"
  // = "sfe_apply_metadata_changes:0"

  这在 LLVM IR 中对应 %0，即函数的第一个参数：

  define dso_local void @sfe_apply_metadata_changes(
      i8** nocapture noundef readonly %0,    ← 这是 "sfe_apply_metadata_changes:0"
      %struct.METADATA_INFO* noundef readonly %1)  ← "sfe_apply_metadata_changes:1"

第 2 步：脚本构建指令→操作数的映射

  build_yapall_valuecases.py（第 684 行）解析整个 .ll 文件。对于每个函数，它：

  (a) 将参数映射到 yapall 样式的操作数名称（第 650 行，function_param_map）：

  # 函数签名: @sfe_apply_metadata_changes(i8** ... %0, %struct.METADATA_INFO* ... %1)
  # 提取: params["%0"] = "sfe_apply_metadata_changes:0"
  #        params["%1"] = "sfe_apply_metadata_changes:1"

  (b) 为每个基本块内的每条指令赋值一个 yapall 样式的指令名称（第 724 行）：

  # 对于函数 sfe_apply_metadata_changes 中块 "2" 中的指令索引 14：
  inst_name = "sfe_apply_metadata_changes:sfe_apply_metadata_changes:2:14"

  (c) 对于每条指令，提取其 !dbg ID（第 727 行）：

  # 从 "%9 = load i8*, i8** %0, align 8, !dbg !87128, !tbaa !7225"
  # 正则匹配捕获 "87128"
  dbg_id = "87128"

  (d) 记录哪些操作数被每条指令使用（第 744 行，classify_instruction_uses）：

  # 指令 "%9 = load i8*, i8** %0" 具有操作码 "load"
  # 此指令中的局部引用：["%0"]
  # local_map 将 "%0" 解析为 → "sfe_apply_metadata_changes:0"
  # 对于 "load"，最后一个操作数是 "load.ptr" 角色：
  #   → ("sfe_apply_metadata_changes:0", "load.ptr")

  这产生了 operand_use_index.csv 中的行：

  operand                           use_site_inst_name                                    role
  sfe_apply_metadata_changes:0  →  sfe_apply_metadata_changes:sfe_apply_metadata_changes:2:14  load.ptr

  同时也产生了 ir_instruction_index.csv 中的行：

  inst_name                                           function  block  idx  result  opcode  ir_text                                        dbg_id
  sfe_apply_metadata_changes:sfe_apply_metadata_changes:2:14  sfe...    2      14   %9      load    "%9 = load i8*, i8** %0, ... !dbg !87128"  87128

第 3 步：脚本将 !dbg 解析为 DILocation

  parse_metadata()（第 816 行）扫描 .ll 文件以查找元数据定义：

  # 输入行：!87128 = !DILocation(line: 0, scope: !87126)
  # 提取：dilocs["87128"] = {"line": "0", "column": "", "scope": "87126", "inlinedAt": ""}

  然后 resolve_diloc()（第 960 行）解析作用域链：

  # scope !87126 → !DILexicalBlock(scope: !87069, file: !3908, line: 243)
  # scope !87069 → !DISubprogram(name: "sfe_apply_metadata_changes", file: !3908, line: 234)
  # file !3908   → !DIFile(filename: "Target/libsndfile/programs/common.c", ...)

  这产生了 debug_location_index.csv 中的行：

  dbg_id  source_file                                source_line  source_column  scope_function
  87128 → Target/libsndfile/programs/common.c         0                         sfe_apply_metadata_changes

第 4 步：脚本通过连接查找将问题与位置匹配

  在 build_valuecases() 中，对于每个原始问题（第 1432 行）：

  for site in resolve_sites(issue, insts, uses):
      # issue.operand = "sfe_apply_metadata_changes:0"
      # resolve_sites 在 uses 映射中查找此操作数
      # 找到 5 个使用站点，按首选角色过滤（invalid_load → "load.ptr"）
      # 得到：
      #   - sfe_apply_metadata_changes:sfe_apply_metadata_changes:2:14   ← 我们的案例
      #   - sfe_apply_metadata_changes:sfe_apply_metadata_changes:24:0
      #   - sfe_apply_metadata_changes:sfe_apply_metadata_changes:242:0

      inst = insts["sfe_apply_metadata_changes:sfe_apply_metadata_changes:2:14"]
      # inst.dbg_id = "87128"

      loc = locs["87128"]
      # loc.line = "0"        ← 这是 DWARF 所说的
      # loc.source_file = "Target/libsndfile/programs/common.c"

      # 写入 CSV：
      row["source_line"] = "0"
      row["source_file"] = "Target/libsndfile/programs/common.c"

  可视化：完整链条

  .ll 文件           ─────────────────────────────────────────────────────────────
                     │
  第 129764 行:      │  define ... @sfe_apply_metadata_changes(i8** ... %0, ...)
                     │      函数名 ────────────────────┘           参数 %0 ─┘
                     │
  第 129779 行:      │  %9 = load i8*, i8** %0, align 8, !dbg !87128
                     │       │              │                │
                     │   指令结果      使用 %0          调试引用
                     │
  第 217829 行:      │  !87128 = !DILocation(line: 0, scope: !87126)
                     │           调试 ID ─┘          行=0 ─┘
                     │
  第 217827 行:      │  !87126 = distinct !DILexicalBlock(..., file: !3908, line: 243)
                     │                                                     │
  第 134609 行:      │  !3908 = !DIFile(filename: "Target/libsndfile/programs/common.c")
                     │
  ───────────────────┼──────────────────────────────────────────────────────────
                     │
  build_yapall_      │
  valuecases.py:     │
                     │
  function_param_map │  "%0"  → 操作数名称 "sfe_apply_metadata_changes:0"
     (第 650 行)     │
                     │
  parse_ll_          │  指令在 函数=sfe_..., 块=2, 索引=14
  instructions       │  → 指令名称 "sfe_apply_metadata_changes:sfe_apply_metadata_changes:2:14"
     (第 684 行)     │  → 指令文本 "%9 = load i8*, i8** %0, ..., !dbg !87128"
                     │  → dbg_id "87128"
                     │
  classify_          │  "%0" 在局部映射中 → "sfe_apply_metadata_changes:0"
  instruction_uses   │  角色: "load.ptr"
     (第 772 行)     │  → ("sfe_apply_metadata_changes:0", "load.ptr") 添加到 uses[]
                     │
  parse_metadata     │  "!87128 = !DILocation(line: 0, ...)"  → locs["87128"].line = "0"
     (第 816 行)     │  scope !87126 → file !3908 → "common.c"
                     │
  build_valuecases   │  issue.operand = "sfe_apply_metadata_changes:0"
     (第 1432 行)    │  resolve_sites() 返回 inst_name = "...2:14" (角色 load.ptr 匹配 invalid_load)
                     │  inst = insts["...2:14"], inst.dbg_id = "87128"
                     │  loc = locs["87128"], loc.line = "0"
                     │  → CSV: source_file="common.c", source_line="0"
                     │
  ───────────────────┼──────────────────────────────────────────────────────────
                     │
  collect_yapall_    │  source_line = "0"
  o2g_cases.py:      │  parse_int("0") → 0
                     │  if line_no == 0: return "line_zero"
                     │  → P0 / LineZero / LocationInvalid

  关键洞察

  映射不是 1:1 — 一个 yapall 操作数（sfe_apply_metadata_changes:0，一个参数）解析为多个 IR 指令（使用 %0 的每个加载、GEP 或调用参数）。脚本过滤 invalid_load → 角色 load.ptr，得到 3
  条候选加载指令（位于块 2、24、242）。选择第一个（块 2 中的 %9），其调试 ID !87128 具有 line: 0。

  line: 0 并不是一个错误 — 它是生成该 IR 的 O2 代码提升的正确 DWARF 结果。该指令（对 filenames[0] 的加载）被提升到了条件分支之上，因此它不再干净地映射到任何单一的源代码行。Clang 将 line: 0 作为 DWARF
  标准的 "无特定行" 标记发出。
```

## paper-libsndfile-yapall-10

```bash

  核心逻辑链条：

  points_to_top main:1
         │
         ▼
  main:1 = 参数 argv (%1) —— .ll 中找到 define @main(i32 %0, i8** %1)
         │
         ▼
  %1 在 main 中被 6 条指令使用 —— 自己写的脚本建立 operand_use_index
         │
         ▼
  points_to_top 无角色筛选 —— 6 条全部保留，取第一条
         │
         ▼
  选中的是 llvm.dbg.value(metadata i8** %1, ...) —— 调试内建函数，不是真实指令
         │
         ▼
  提取 !dbg !86589
         │
         ▼
  !86589 = !DILocation(line: 0, scope: main函数) —— DWARF 元数据里写了 line:0
         │
         ▼
  文件 = sndfile-convert.c → 报告位置: sndfile-convert.c:0

  三个关键转折点：

  1. points_to_top 没有角色筛选 → 选了调试内建函数，而没选真实的 %9 = load i8*, i8** %1
  2. llvm.dbg.value 是编译器脚手架 → 它的 !dbg 指向 line: 0
  3. line: 0 的作用域是 main 函数本身（不是词法块）→ 无法进一步缩小到某个代码行
```

## paper-zfp-yapall-19

!image.png

```bash

  ┌──────────────────────────────────────────────────────────────────────────┐
  │     Case 19：yapall 原始输出 → 调试元数据映射                                │
  │     invalid_load  zfp_decode_block_int64_2:zfp_decode_block_int64_2:2:8  *null │
  └──────────────────────────────────────────────────────────────────────────┘

    STEP 1 — 操作数解析
    ┌─────────────────────────────────────────────────────────────────────┐
    │ zfp_decode_block_int64_2:zfp_decode_block_int64_2:2:8               │
    │ │                        │                     │  │                 │
    │ 函数                     块 "2"                索引 8                │
    │ → LocalName::Instruction(InstructionName {function, block, idx=8}) │
    │                                                                     │
    │ ★ 这是 INSTRUCTION 操作数，不是参数 — 操作数就是指令结果本身            │
    └─────────────────────────────────────────────────────────────────────┘
           │
           │  操作数直接在 instructions 字典中匹配
           ▼

    STEP 2 — site_resolution = "resolved_exact_operand_instruction"
    ┌─────────────────────────────────────────────────────────────────────┐
    │ 无需 operand_use_index 查找 — 操作数名称 = 指令名称                    │
    │                                                                     │
    │ inst = insts["zfp_decode_block_int64_2:zfp_decode_block_int64_2:2:8"]│
    │ inst.function = "zfp_decode_block_int64_2"                          │
    │ inst.block    = "2"                                                  │
    │ inst.index    = 8                                                    │
    │ inst.opcode   = "load"                                               │
    │ inst.text     = "%9 = load %struct.bitstream*, ..."                  │
    │ inst.dbg_id   = "18006"                                              │
    └─────────────────────────────────────────────────────────────────────┘
           │
           │  dbg_id = "18006"
           ▼

    STEP 3 — 调试元数据解析
    ┌─────────────────────────────────────────────────────────────────────┐
    │ !18006 = !DILocation(line: 0, scope: !17976)                        │
    │            │               │        │                                │
    │            │               │        └── !17976 = DISubprogram(       │
    │            │               │              "zfp_decode_block_int64_2",│
    │            │               │              file: !10290, line: 7)     │
    │            │               │                                         │
    │            │               └── ★ line: 0                             │
    │            │                   作用域 = 函数 DISubprogram 本身          │
    │            │                                                         │
    │            └── 调试位置引用，附加到加载指令                              │
    │                                                                     │
    │ !10290 = !DIFile("Target/zfp/src/template/decodei.c",               │
    │                  checksum: "1ae21529d348c455943de4c8f3de3641")      │
    └─────────────────────────────────────────────────────────────────────┘
           │
           │  source_file = "decodei.c", source_line = "0"
           ▼

    STEP 4 — 为什么 !18006 具有 line: 0（而 !18007 保持 line: 9）
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  三元表达式（decodei.c 第 9 行，完整的函数体）：                       │
    │                                                                     │
    │  REVERSIBLE(zfp)                                                    │
    │    ? rev_decode( zfp->stream, zfp->minbits, zfp->maxbits, iblock)   │
    │    :  decode_block(zfp->stream, zfp->minbits, zfp->maxbits, ...)    │
    │                    ↑             ↑              ↑                    │
    │                    在两个分支中    在两个分支中      在两个分支中           │
    │                    → 已提升       → 已提升         → 已提升              │
    │                    → !18006      → !18006        → !18006             │
    │                    → line: 0     → line: 0       → line: 0            │
    │                                                                     │
    │  REVERSIBLE(zfp) = (zfp->minexp < -1074)                            │
    │                       ↑                                             │
    │                       仅在条件中 — 未被提升                               │
    │                       → !18007 → line: 9, column: 10                 │
    └─────────────────────────────────────────────────────────────────────┘
           │
           ▼

    STEP 5 — 级联内联的 line: 0
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  decodei.c:9 → zfp_decode_block_int64_2                             │
    │    !18006 = line: 0  scope: !17976 (DISubprogram)                   │
    │       │                                                             │
    │       │  第 9 行第 28 列调用 rev_decode_block_int64_2                  │
    │       ▼                                                             │
    │  revdecode.c:37 → rev_decode_block_int64_2 (内联)                    │
    │    !18019 = line: 0  scope: !18009  inlinedAt: !18020 (第 9 行第 28 列)│
    │       │                                                             │
    │       │  第 41 行第 21 列调用 stream_read_bits                        │
    │       ▼                                                             │
    │  inline.c:254 → stream_read_bits (内联)                              │
    │    !18028 = line: 0  scope: !18022  inlinedAt: !18029 (第 41 行第 21 列)│
    │                                                                     │
    │  ★ 所有三个内联级别在其被提升的序言指令上共享相同的 line:0 模式           │
    │  ★ 一个 O2 提升决策 → 三个函数体的调试位置丢失                           │
    └─────────────────────────────────────────────────────────────────────┘

  总结：

    invalid_load
    zfp_decode_block_int64_2:zfp_decode_block_int64_2:2:8
    *null
         │
         │  resolved_exact_operand_instruction（操作数就是指令本身）
         ▼
    %9 = load %struct.bitstream*, %struct.bitstream** %8, !dbg !18006
         │                                                   │
         │  %8 = &zfp->stream（zfp_stream 结构体的字段 4）      │
         │                                                   │
         ▼                                                   ▼
    加载 zfp->stream                                !18006 = DILocation(line: 0)
         │                                           作用域: DISubprogram(zfp_decode_block_int64_2)
         │                                           文件: decodei.c
         ▼
    invalid_load 原因:                                line:0 原因:
    yapall 无法证明                                  O2 从三元表达式的两个分支
    zfp->stream ≠ null                               中提升了 zfp->stream 加载
    (流不敏感 + k=0                                 → 合并后的指令没有唯一的源行
     过度近似)                                       → LLVM 将行号设为 0 (DWARF 标准)

```

## paper-zfp-yapall-20

```bash
  ┌──────────────────────────────────────────────────────────────────────────┐
  │  Case 20：yapall 原始输出 → 调试元数据 → 三重分类                            │
  │  invalid_load  zfp_encode_block_float_2:zfp_encode_block_float_2:534:24  *null │
  └──────────────────────────────────────────────────────────────────────────┘

    STEP 1 — 操作数解析
    ┌─────────────────────────────────────────────────────────────────────┐
    │ zfp_encode_block_float_2:zfp_encode_block_float_2:534:24           │
    │ │                        │                     │   │               │
    │ 函数                     块 534（深度内联！）    索引 24             │
    │                                                                     │
    │ ★ site_resolution = "resolved_exact_operand_instruction"            │
    │   (操作数就是指令结果，直接匹配)                                       │
    └─────────────────────────────────────────────────────────────────────┘
           │
           ▼

    STEP 2 — .ll 中的 IR 指令 (第 24451 行)
    ┌─────────────────────────────────────────────────────────────────────┐
    │ %549 = load %struct.bitstream*, %struct.bitstream** %548,           │
    │        align 8, !dbg !12037, !tbaa !1267                           │
    │                                                                     │
    │ %548 = getelementptr ... %0, i32 4   ← &zfp->stream (字段 4)       │
    │ %549 加载 zfp->stream（指向 bitstream 结构的指针）                    │
    └─────────────────────────────────────────────────────────────────────┘
           │
           │  dbg_id = "12037"
           ▼

    STEP 3 — 调试元数据（与 case 19 的关键区别）
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  !12037 = !DILocation(line: 0, scope: !12021, inlinedAt: !12023)   │
    │              │               │        │              │              │
    │              │               │        │              └── 调用站点     │
    │              │               │        │                   !12023 =   │
    │              │               │        │                   DILocation(│
    │              │               │        │                   line: 98,  │
    │              │               │        │                   col: 79,   │
    │              │               │        │                   scope:     │
    │              │               │        │                   !11598)    │
    │              │               │        │                              │
    │              │               │        └── 作用域（被调用者）          │
    │              │               │             !12021 = DILexicalBlock(  │
    │              │               │               scope: !12012,          │
    │              │               │               line: 71)  ← if(e) 块  │
    │              │               │             !12012 = DISubprogram(    │
    │              │               │               "encode_block_float_2", │
    │              │               │               line: 63)               │
    │              │               │                                       │
    │              │               └── ★ line: 0                           │
    │              │                                                       │
    │              └── 调试位置引用                                         │
    │                                                                     │
    │  !11598 = DISubprogram("zfp_encode_block_float_2", line: 96)        │
    │  !4911  = DIFile("Target/zfp/src/template/encodef.c")               │
    │                                                                     │
    │  ★ 对比 case 19：!18006 没有 inlinedAt                               │
    │  ★ 本案例：inlinedAt 存在 → 跨函数边界 + 函数归因错误                   │
    └─────────────────────────────────────────────────────────────────────┘
           │
           │  从一份元数据中触发三个分类
           ▼

    STEP 4 — 三重分类触发
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  !12037                                                             │
    │  ├── line: 0         →  source_line_missing                         │
    │  │                  →  ★ Wanted-LineColumnMissing                   │
    │  │                                                                  │
    │  ├── inlinedAt: !12023 → has_inlined_at = True                      │
    │  │                    →  ★ InlineAttributionDrift                   │
    │  │                                                                  │
    │  └── scope: !12012 ("encode_block_float_2")                         │
    │      vs IR function ("zfp_encode_block_float_2")                    │
    │                    →  scope_func ≠ ir_func                          │
    │                    →  ★ WrongFunctionAttribution                    │
    │                                                                     │
    │  函数归因跟踪：                                                       │
    │    ir_function              = "zfp_encode_block_float_2" (IR 物理位置)│
    │    scope_function           = "encode_block_float_2" (元数据作用域)   │
    │    source_enclosing_function = "encode_block_float_2" (从第 71 行回溯) │
    └─────────────────────────────────────────────────────────────────────┘
           │
           ▼

    STEP 5 — 与保留行号指令的对比
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  已提升（line: 0）：                                                  │
    │    zfp->stream   → line 75, 79, 83  (if/else 分支) → 已合并 → line:0│
    │                                                                     │
    │  未提升（保留行号）：                                                  │
    │    zfp->maxprec  → line 68  (仅一次，在 if(e) 之前) → 未合并 → line:68│
    │    if(e) 检查     → line 71  (仅一次) → 未合并 → line:71              │
    │                                                                     │
    │  ★ 直接证据：只有共享的/被合并的子表达式才会丢失其行号                   │
    └─────────────────────────────────────────────────────────────────────┘

  总结：

    invalid_load
    zfp_encode_block_float_2:zfp_encode_block_float_2:534:24  ← 块 534 = 深度内联
    *null
         │
         │  resolved_exact_operand_instruction
         ▼
    %549 = load ... zfp->stream, !dbg !12037
         │                           │
         │                           ├── line: 0
         │                           ├── scope: encode_block_float_2 (被调用者)
         │                           └── inlinedAt: zfp_encode_block_float_2:98:79 (调用者)
         │
         ▼
    三重分类：
      1. Wanted-LineColumnMissing  ←  line: 0
      2. InlineAttributionDrift    ←  inlinedAt 存在
      3. WrongFunctionAttribution  ←  scope (被调用者) ≠ IR 函数 (调用者)
```

# Cases Study总结

导致行号不一致的几个原因：

1.工具严格按照debug的metadata进行搜集，所以O2优化导致工具的行列错报

2.工具会对metadata进行一个简单的分析（phasar），工具的错报+O2优化

3.clang在编译的时候，直接DWARF 标准 §6.2.2 规定，当 "一个指令......不与任何源行有可预测的关系" 时（例如，提升过基本块边界），编译器应发出 line: 0。这种属于真实且实际的编译流程，然后程序分析工具（不一定report bug）直接使用metadata必然报linezero。

聚焦点应该是什么？

针对静态扫描工具吗？

还是针对编译优化

Phasar

Seahorn

dg

cclyzer++

yapall
