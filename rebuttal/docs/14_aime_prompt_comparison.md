# AIME Abstraction Prompt Comparison

**Date:** 2025-11-18  
**Status:** ✅ Ready for A/B testing  
**Purpose:** Compare original vs strict AIME abstraction prompts

---

## Two Versions

### Version 1: Original AIME Template

**Config:** `aime_lesson_from_trace.yaml`

**Prompt:** `EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE`

**Characteristics:**
- Simple, concise instructions
- Basic generalization guidance
- ~250 tokens

**Strengths:**
- ✅ Clear and straightforward
- ✅ Less restrictive (model has more freedom)
- ✅ Faster to process

**Weaknesses:**
- ⚠️ May produce vague suggestions
- ⚠️ May not capture key steps explicitly
- ⚠️ Could overfit to specific numbers

---

### Version 2: Strict AIME Template

**Config:** `aime_lesson_from_trace_strict.yaml`

**Prompt:** `EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE_STRICT`

**Characteristics:**
- 6 explicit numbered constraints
- Anti-overfitting guards
- Concrete suggestion requirements
- ~650 tokens

**Strengths:**
- ✅ Enforces concrete, executable suggestions
- ✅ Requires at least one lesson to encode main key step
- ✅ Explicit anti-overfitting checks
- ✅ Prevents trivial advice
- ✅ Scope-limited (AIME-level only)

**Weaknesses:**
- ⚠️ More tokens per request (~2.5x longer)
- ⚠️ More restrictive (less model creativity)

---

## The 6 Constraints (Strict Version Only)

1. **General but Detectable Situations**
   - Parameterize values
   - Use structural patterns

2. **Concrete, Executable Suggestions**
   - Must describe specific actions
   - At least ONE lesson encodes main key step

3. **AIME-Level Methods Only**
   - No advanced university mathematics
   - High-school olympiad level

4. **Avoid Problem-Specific Overfitting**
   - Don't use problem labels or variable names
   - Test: "Would this work if numbers changed?"

5. **No Trivial or Meta Advice**
   - No "re-read the problem" type advice
   - Focus on mathematical structure

6. **Faithfulness to Given Solution**
   - Base on actual reasoning steps
   - Don't invent new methods

---

## How to A/B Test

### Run Both Versions

```bash
cd arc_memo
source .venv/bin/activate

# Make sure you have solutions and thought processes
# (from steps 1a and 1b)

# Version 1: Original
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace \
  abstraction.problem_solutions="experiments/aime_test_v3/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_test_v3/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_test_v3/abstraction_original"

# Version 2: Strict
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_strict \
  abstraction.problem_solutions="experiments/aime_test_v3/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_test_v3/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_test_v3/abstraction_strict"
```

---

## Comparison Metrics

### Quantitative

**Count lessons:**
```bash
python -c "import json; d=json.load(open('experiments/aime_test_v3/abstraction_original/lessons.json')); print('Original:', sum(len(v) for v in d.values()), 'lessons from', len(d), 'problems')"

python -c "import json; d=json.load(open('experiments/aime_test_v3/abstraction_strict/lessons.json')); print('Strict:', sum(len(v) for v in d.values()), 'lessons from', len(d), 'problems')"
```

**Token usage:**
```bash
python -c "import json; print('Original tokens:', json.load(open('experiments/aime_test_v3/abstraction_original/token_usage.json'))['after'])"

python -c "import json; print('Strict tokens:', json.load(open('experiments/aime_test_v3/abstraction_strict/token_usage.json'))['after'])"
```

---

### Qualitative (Manual Review)

**For 2-3 sample problems, check:**

**1. Generalization Quality**
- ❌ Bad: "When you have N = 9 + 99 + 999 + ... with 321 digits"
- ✅ Good: "When summing sequences where each term has k repeated identical digits"

**2. Concreteness of Suggestions**
- ❌ Vague: "Consider the structure carefully"
- ✅ Concrete: "Rewrite each k-digit block as 10^k - 1 and sum as geometric series"

**3. Key Step Encoding**
- ✅ At least one lesson should explicitly describe the main solution technique
- Example: "View probability as counting lattice points in a triangular region"

**4. Problem-Specific Overfitting**
- ❌ Bad: "When calculating (10^322 - 10)/9 - 321"
- ✅ Good: "When large algebraic expressions need only their digit sum"

**5. Trivial Advice**
- ❌ Bad: "Check your arithmetic"
- ✅ Good: "Apply Vieta's formulas to relate coefficients to roots"

---

## Expected Results

**Hypothesis:**
- **Strict version produces higher quality lessons** due to explicit constraints
- **But uses ~2.5x more tokens** (~650 vs ~250 per problem)

**Decision criteria:**
- If quality improvement is significant → Use strict for full run
- If quality is similar → Use original (cheaper)

---

## Files

**Configs:**
- `configs/abstraction/aime_lesson_from_trace.yaml` - Original
- `configs/abstraction/aime_lesson_from_trace_strict.yaml` - Strict

**Templates:**
- `EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE` - Original
- `EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE_STRICT` - Strict (with 6 constraints)

**Outputs:**
- `experiments/.../abstraction_original/lessons.json`
- `experiments/.../abstraction_strict/lessons.json`

---

**Status:** ✅ Both versions ready for comparison  
**Recommended:** Run A/B test on 10-problem test set before full 120-problem run

