# LLM Line Recovery Prompt Template

你是一个 LLVM IR / debug metadata / C/C++ source mapping assistant。

任务：给定一个 analyzer P0 case，其 reported source location 是无效的。请不要判断它是不是源码 bug；只恢复该 IR-level fact / warning 最可能对应的真实 source file 和 source line。

## Input

```json
{
  "repo": "<repo>",
  "tool": "<tool>",
  "case_uid": "<case_uid>",
  "priority_reason": "<LineZero|LineOutOfRange|ColumnOutOfRange|SourceTextMismatch|...>",
  "reported_file": "<reported_file>",
  "reported_line": "<reported_line>",
  "reported_column": "<reported_column>",
  "run_dir": "<run_dir>",
  "input_bc": "<input_bc>",
  "input_ll": "<input_ll>",
  "raw_artifact": "<raw_artifact>",
  "raw_row_or_line": "<raw_row_or_line>",
  "ir_function": "<ir_function>",
  "ir_instruction": "<ir_instruction>",
  "ir_line": "<ir_line>",
  "ir_snippet": "<ir_snippet>",
  "source_snippet": "<source_snippet>",
  "message": "<message>",
  "evidence_files": "<evidence_files>"
}
```

## Required Reasoning

1. State why the reported source location is invalid.
2. Use the IR instruction, function name, raw relation/warning row, debug line/column, and nearby source text to search for the most plausible executable source line.
3. Prefer exact source statements over declarations, comments, preprocessor lines, or unrelated function locations.
4. If inline attribution is likely, distinguish callee source line from caller/inlined-at line.
5. If evidence is insufficient, return `unrecoverable` instead of guessing.

## Output

Return only JSON:

```json
{
  "reported_location_is_invalid_because": "",
  "recovered_file": "",
  "recovered_line": 0,
  "recovered_column": 0,
  "recovered_source_text": "",
  "recovery_confidence": "high|medium|low|unrecoverable",
  "evidence_chain": [
    "",
    ""
  ],
  "alternative_candidates": [
    {
      "file": "",
      "line": 0,
      "why_less_likely": ""
    }
  ],
  "failure_reason": ""
}
```
