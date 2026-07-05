# cclyzer++ Scan Final Report

## Metadata
- target: flatbuffers
- universe: LLVM14-O2-g
- input_bc: /home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc
- docker_image: ghcr.io/galoisinc/cclyzerpp-dev:main
- analysis: subset
- context_sensitivity: insensitive
- run_dir: /home/jimi/PaperExperiment/CompilerOptimization/Result/flatbuffers/cclyzerpp/LLVM14-O2-g/run_20260427_132609_flatbuffers_flatc_O2_g
- status: reported
- return_code: 0
- elapsed_sec: 12516

## Important Interpretation Note
- cclyzer++ is a global pointer-analysis engine. Rows in `extract/candidates.tsv` are high-signal candidate anomalies for manual review, not verified CWE bug reports.
- Promote a row to a paper case only after O0/O2/O2-noinline comparison and source/IR inspection.

## Candidate Counts
| kind | count |
| --- | ---: |
| CallgraphFanout | 1000 |
| PointsToFanout | 1000 |
| AliasBucketFanout | 1000 |
| PointerObjectFanout | 1000 |
| PhiMergeHotspot | 1000 |
| TailCallSite | 1000 |
| MissingDebugLoc | 1000 |

## Top Candidates
| kind | metric | file | line | function | subject | detail |
| --- | ---: | --- | ---: | --- | --- | --- |
| PointsToFanout | 1512 | llvm-link | 0 | _ZStplIcSt11char_traitsIcESaIcEENSt7__cxx1112basic_stringIT_T0_T1_EEPKS5_RKS8_ | %21 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 1254 | llvm-link | 0 | _ZStplIcSt11char_traitsIcESaIcEENSt7__cxx1112basic_stringIT_T0_T1_EEPKS5_RKS8_ | %22 | variable has a broad points-to set; candidate over-approximation / phi merge |
| AliasBucketFanout | 1132 | NA | 0 | NA | *heap_alloc@_ZN11flatbuffers15vector_downwardIjE10reallocateEm[i8* %39][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1132 | NA | 0 | NA | *typed_heap_alloc@_ZN11flatbuffers15vector_downwardIjE10reallocateEm[i32* %39][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1130 | NA | 0 | NA | *heap_alloc@_ZN11flatbuffers15vector_downwardIjE10reallocateEm[i8* %54][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| AliasBucketFanout | 1130 | NA | 0 | NA | *typed_heap_alloc@_ZN11flatbuffers15vector_downwardIjE10reallocateEm[i32* %54][*] | one allocation reaches many variables; candidate alias collapse hotspot |
| PointsToFanout | 872 | llvm-link | 0 | _ZStplIcSt11char_traitsIcESaIcEENSt7__cxx1112basic_stringIT_T0_T1_EEPKS5_RKS8_ | %27 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 676 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIN9__gnu_cxx17__normal_iteratorIPKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESt6vectorIS9_SaIS9_EEEEPS9_EET0_T_SI_SH_ | %13 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIN9__gnu_cxx17__normal_iteratorIPKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESt6vectorIS9_SaIS9_EEEEPS9_EET0_T_SI_SH_ | %1 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EE20_M_allocate_and_copyIN9__gnu_cxx17__normal_iteratorIPKS5_S7_EEEEPS5_mT_SF_ | %3 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIPNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEES8_EET0_T_SA_S9_ | %1 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIPNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEES8_EET0_T_SA_S9_ | %2 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %115 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %112 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %111 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %105 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %104 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %102 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %72 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %68 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %51 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %50 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %26 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %9 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EEaSERKS7_ | %6 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIPNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEES8_EET0_T_SA_S9_ | %58 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIPNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEES8_EET0_T_SA_S9_ | %47 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIPNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEES8_EET0_T_SA_S9_ | %46 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIPNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEES8_EET0_T_SA_S9_ | %32 | variable has a broad points-to set; candidate over-approximation / phi merge |
| PointsToFanout | 666 | llvm-link | 0 | _ZNSt20__uninitialized_copyILb0EE13__uninit_copyIPNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEES8_EET0_T_SA_S9_ | %23 | variable has a broad points-to set; candidate over-approximation / phi merge |

## Largest Relations
| relation | rows |
| --- | ---: |
| call_instr_arg | 3622410 |
| instr_bb_entry | 2032763 |
| instr_func | 2032763 |
| instr_successor | 2030165 |
| instr_pos | 1940782 |
| constant | 1917717 |
| constant_has_type | 1917717 |
| constant_has_value | 1917717 |
| constant_hashes_to | 1917717 |
| constant_in_func_name | 1903415 |
| subset.ptr_points_to | 1384110 |
| func_constant | 1276756 |
| func_constant_fn_name | 1276756 |
| variable | 1269158 |
| variable_has_type | 1269158 |
| variable_in_func_name | 1269158 |
| call_instr | 1247685 |
| call_instr_func_operand | 1247685 |
| variable_has_name | 1245668 |
| subset.operand_points_to | 1117325 |

## Command
```bash
timeout -s KILL -k 5 21600 docker run --rm -v /home/jimi/PaperExperiment:/work -w /work/CompilerOptimization/Tools/cclyzerpp/cclyzerpp --entrypoint /bin/bash ghcr.io/galoisinc/cclyzerpp-dev:main -lc 'set -euo pipefail; opt --disable-output -enable-new-pm=0 --load=build/libSoufflePA.so --load=build/libPAPass.so -cclyzer -debug-datalog=true -debug-datalog-dir='"'"'/work/CompilerOptimization/Result/flatbuffers/cclyzerpp/LLVM14-O2-g/run_20260427_132609_flatbuffers_flatc_O2_g/relations'"'"' -context-sensitivity='"'"'insensitive'"'"' -datalog-analysis='"'"'subset'"'"' '"'"'/work/CompilerOptimization/CompilerResult/flatbuffers/LLVM14-O2-g/artifacts/flatbuffers_flatc_O2_g.bc'"'"''
```
