# AIME Domain-Specific Prompts

**Date:** 2025-11-18  
**Status:** ✅ Implemented  
**Issue:** ARC-specific prompts were being used for AIME problems

---

## Problem

The abstraction stage (GPT-4.1) was using **ARC-specific prompts** for AIME problems:

```
### Introduction
Consider a class of "ARC" puzzles where each puzzle has a hidden transformation 
rule that maps input grids to output grids...

Grids are 2D numpy integer arrays with integers representing colors. 0 represents 
black and should be treated as the background.
```

**Issues:**
- ❌ References "ARC puzzles" for AIME math problems
- ❌ Talks about "grids" and "colors" for algebra/geometry problems
- ❌ Confusing for the model
- ❌ May reduce abstraction quality

---

## Solution

Created **AIME-specific abstraction prompts** that reference mathematical domains instead of grid puzzles.

### New AIME Prompts

**Added to `analysis_concept_prompts.py`:**

**1. Few-Shot Template (`EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE`):**
```
### Introduction
You are analyzing AIME (American Invitational Mathematics Examination) problems 
to extract reusable mathematical reasoning patterns. AIME problems span various 
domains including algebra, geometry, number theory, combinatorics, and probability.

Your task is to analyze a solved problem and its reasoning process to extract 
reusable lessons for solving other AIME problems.

### Instructions
- The "situation" should describe mathematical patterns, structures, or conditions
- The "suggestion" should recommend specific techniques or approaches
- Parameterize specific values (use "when coefficients form a pattern" not "when a=5")

### Examples
{examples}

### Problem Answer
{solution}

### Solver's Reasoning
{thought_process}
```

**2. Zero-Shot Template (`EXTRACT_LESSON_FROM_AIME_ZS_TEMPLATE`):**
- Similar but without examples section

---

## Implementation

### Config-Based Template Selection

**Added `use_aime_prompts` parameter to function signature:**

```python
async def extract_lessons(
    problems: dict[str, Problem],
    solutions: dict[str, str],
    thought_processes: dict[str, str] | None,
    ...,
    use_aime_prompts: bool = False,  # ← New parameter
    dry_run: bool = False,
) -> tuple[dict[str, list[dict]], dict]:
```

**In `build_abstraction_prompt()`:**

```python
def build_abstraction_prompt(
    problem: Problem,
    solution: str,
    thought_process: str | None = None,
    ...,
    use_aime_template: bool = False,  # ← New parameter
) -> str:
    if thought_process is None:
        # ARC path (requires grid formatting)
        ...
    else:
        # Select template based on domain
        if use_aime_template:
            # Use AIME-specific templates
            if fixed_examples is not None:
                prompt = EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE.format(...)
            else:
                prompt = EXTRACT_LESSON_FROM_AIME_ZS_TEMPLATE.format(...)
        else:
            # Use ARC-specific templates
            ...
```

**Config-driven selection in `async_main()`:**

```python
await extract_lessons(
    ...,
    use_aime_prompts=cfg.abstraction.get('use_aime_prompts', False),  # ← From config
    dry_run=cfg.dry_run,
)
```

---

## Configuration

**AIME Config (`aime_lesson_from_trace.yaml`):**
```yaml
abstraction:
  use_aime_prompts: true  # ← Triggers AIME-specific templates
```

**ARC Config (`default_lesson_from_trace.yaml`):**
```yaml
abstraction:
  use_aime_prompts: false  # ← Uses ARC templates (default)
  # Or omit - defaults to false
```

**Note:** Both ARC and AIME use thought processes. The distinguisher is the explicit `use_aime_prompts` flag, not the presence of `thought_processes`.

---

## What Changed

### Before (Confusing)
```
Introduction: "Consider ARC puzzles with grids and colors..."
Your Problem: [AIME algebra problem]
```

### After (Clear)
```
Introduction: "Analyzing AIME problems spanning algebra, geometry, number theory..."
Your Problem: [AIME algebra problem]
```

---

## Key Improvements

**1. Domain-Appropriate Language**
- ❌ Before: "grids", "colors", "transformation rules"
- ✅ After: "mathematical patterns", "algebra", "geometry", "number theory"

**2. Better Generalization Instructions**
- ❌ Before: "parameterize colors, shapes, orientations"
- ✅ After: "parameterize coefficients, exponents, moduli"

**3. Context Alignment**
- ✅ Model now knows it's analyzing AIME math problems, not grid puzzles
- ✅ Examples and instructions match the domain

---

## Backward Compatibility

**ARC puzzles still work exactly as before:**
- Uses `Problem.from_puzzle_id()` → Full Problem objects
- `use_aime_template=False` → Uses ARC-specific templates
- No changes to ARC functionality

**AIME now works properly:**
- Uses `DummyProblem` objects (lines 320-328 in `analysis_concepts.py`)
- Automatically detected → `use_aime_template=True`
- Uses AIME-specific templates

---

## Files Modified

1. **`analysis_concept_prompts.py`**
   - Added `EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE`
   - Added `EXTRACT_LESSON_FROM_AIME_ZS_TEMPLATE`
   - Organized with clear section headers

2. **`analysis_concepts.py`**
   - Imported new AIME templates
   - Added `use_aime_template` parameter to `build_abstraction_prompt()`
   - Added auto-detection logic based on `DummyProblem`

---

## Testing

**Run AIME abstraction:**
```bash
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace \
  abstraction.problem_solutions="experiments/aime_test_v3/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_test_v3/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_test_v3/abstraction"
```

**Verify AIME template is used:**
```bash
cat experiments/aime_test_v3/abstraction/prompts.json | jq '.[0]' | grep -i "AIME"
# Should see: "analyzing AIME problems" not "ARC puzzles"
```

---

## Expected Improvements

1. **Better concept quality:** Model understands it's analyzing math, not grids
2. **More appropriate abstractions:** Math techniques instead of grid operations
3. **Clearer instructions:** Domain-specific guidance
4. **Less confusion:** No mixed signals about what domain we're in

---

## Summary Table

| Stage | Template Used | Domain Language |
|-------|---------------|-----------------|
| **ARC Puzzles** | `EXTRACT_LESSON_FROM_TRACE_FS_TEMPLATE` | Grids, colors, transformations |
| **AIME Problems** | `EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE` | Algebra, geometry, number theory |

---

**Status:** ✅ Implemented and auto-detected  
**Next:** Test on AIME problems to verify improved abstraction quality

