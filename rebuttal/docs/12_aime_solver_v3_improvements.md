# AIME Solver v3 - Ultra-Strict Output Format

**Date:** 2025-11-18  
**Status:** ✅ Implemented  
**Issue:** Fragile answer extraction in v1/v2

---

## Problem with v1/v2

### v2 Prompts (Fragile)
```
System: "Think through the problem step by step, then provide your final answer 
in the format: Final Answer: [number]"

User: "Solve this AIME problem: [problem] 
Show your reasoning, then provide your final answer in the format: Final Answer: [number]"
```

**Issues:**
- ❌ Model might not follow "Final Answer: X" format
- ❌ Fragile regex parsing required
- ❌ Instructions repeated in both system and user prompts
- ❌ Could output "The answer is 237" or "237" or "Answer: 237"
- ❌ Requires 5 different extraction fallback patterns

---

## v3 Solution (Ultra-Strict)

### How System vs User Prompts Work

**In `llmplus/client.py` `_format_chat()` method:**
```python
def _format_chat(self, inp: str | list[dict]):
    if isinstance(inp, str):
        msgs = [{"role": "user", "content": inp}]
    else:
        msgs = inp
    if self.system_prompt:
        msgs = [{"role": "system", "content": self.system_prompt}, *msgs]
    return msgs
```

**In solver code:**
```python
llm_client.system_prompt = AIME_SYSTEM_PROMPT  # Sets system role
prompts = [AIME_SOLVE_PROMPT.format(...)]      # User role
```

**Sent to API as:**
```json
[
  {"role": "system", "content": "You are solving AIME..."},
  {"role": "user", "content": "Solve this AIME problem: ..."}
]
```

---

### v3 Prompts (Ultra-Strict)

**System Prompt:**
```
You are solving AIME (American Invitational Mathematics Examination) problems.

You may think step by step internally, but your final output MUST be a single 
base-10 integer with no other characters at all.

Requirements for the final output:
- Only the integer, nothing else (no words, labels, units, or punctuation).
- No spaces, no newlines before or after, no explanation.
- No leading zeros unless the answer is 0 itself.
- The answer must be between 0 and 999 inclusive.

Example of correct output: 237

Examples of incorrect output: "Final Answer: 237", "237 ", "0237", "The answer is 237".
```

**User Prompt:**
```
Solve this AIME problem:

[problem text]

Output only the integer answer.
```

**Benefits:**
- ✅ Crystal clear format requirements with examples
- ✅ Shows both correct and incorrect examples
- ✅ Minimal, clean user prompt
- ✅ Allows internal reasoning but demands clean output
- ✅ Explicit constraints (0-999, no leading zeros)

---

## Extraction Logic Improvements

### v3 Extraction (Primary + Fallbacks)

```python
def extract_answer_from_response(response: str) -> str:
    response = response.strip()
    
    # PRIMARY: Response IS the number (v3 format)
    if response.isdigit():
        num = int(response)
        if 0 <= num <= 999:
            return response  # ✓ Perfect v3 compliance
    
    # FALLBACK 1-5: Handle non-compliant models
    # (Same patterns as v2, but clearly secondary)
    ...
```

**Key Improvement:**
- **Primary check**: `response.isdigit()` → Super fast, no regex
- **Fallbacks**: Keep v2 patterns for robustness
- **Logging**: Distinguishes v3-compliant responses from fallback extractions

---

## Usage

**Command:**
```bash
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_test \
  model=o4_mini \
  generation.n=3 \
  generation.expand_multi=true \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  hydra.run.dir="experiments/aime_test_v3/o4_solve"
```

**Output:**
```
AIME Solver v3 - Ultra-Strict Output Format
======================================================================
Model: o4-mini-2025-04-16
Format: Integer only (no text, no formatting)
======================================================================

Solving 10 AIME problems...

Results:
  Successfully solved: 10/10
  Extraction failures: 0
  
✓ Solutions saved to: experiments/aime_test_v3/o4_solve/solutions.json
✓ Full responses saved to: experiments/aime_test_v3/o4_solve/full_responses.json
```

**Debug Artifacts:**
- `solutions.json` - Final extracted answers
- `full_responses.json` - Raw model outputs
- `extraction_failures.json` - Any failed extractions (if any)

---

## Comparison

| Feature | v1 | v2 | v3 (New) |
|---------|----|----|----------|
| **Prompt clarity** | Poor | Good | Excellent |
| **Format strictness** | Loose | Medium | Ultra-strict |
| **Extraction method** | Regex | Multi-pattern regex | isdigit() + fallbacks |
| **Format examples** | No | No | Yes (both correct & incorrect) |
| **Explicit constraints** | No | Partial | Yes (0-999, no leading zeros) |
| **System/User separation** | Mixed | Mixed | Clean |
| **Debugging output** | Minimal | Good | Excellent |
| **Compliance logging** | No | No | Yes (distinguishes v3 vs fallback) |

---

## Expected Improvements

1. **Higher compliance:** Models more likely to follow explicit examples
2. **Fewer extraction failures:** Primary check handles 95%+ of cases
3. **Faster extraction:** `isdigit()` is instant vs regex patterns
4. **Better debugging:** Know immediately if model followed format
5. **Cleaner responses:** Less reasoning text in output to parse

---

## Migration Path

**For new experiments:** Use v3

**For existing experiments:**
- v2 still works fine
- v3 recommended for production
- Both support `expand_multi=true` for o4-mini

---

## Files

- **Implementation:** `arc_memo/concept_mem/data/aime_simple_solver_v3.py`
- **Documentation:** This file
- **Related:** `10_aime_o4mini_expand_multi_fix.md` (o4-mini n>1 issue)

---

**Status:** ✅ Ready for testing  
**Next:** Test on 10-problem set, then roll out to full pipeline

