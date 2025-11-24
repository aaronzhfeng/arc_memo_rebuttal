# Test AIME v3 Complete Pipeline

Complete testing of all 3 stages on the 10-problem test set.

**Status:** Stage 1a complete (10/10 solved) ✓

---

## Stage 1a: Solving (Complete ✓)

Already done:
```
experiments/aime_test_v3/o4_solve/
├── solutions.json (10/10 solved)
├── model_outputs.json
└── token_usage.json (with per-request details)
```

---

## Stage 1b: Thought Process Generation

```bash
cd arc_memo
source .venv/bin/activate

python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="experiments/aime_test_v3/o4_solve/solutions.json" \
  data=aime_test \
  model=o4_mini \
  generation.max_tokens=2048 \
  hydra.run.dir="experiments/aime_test_v3/o4_reasoning"

# Verify
cat experiments/aime_test_v3/o4_reasoning/thought_processes.json | jq 'keys | length'
# Should output: 10

# Check one thought process
cat experiments/aime_test_v3/o4_reasoning/thought_processes.json | jq '.["2019-II-2"]' | head -20
```

**What to check:**
- ✅ All 10 problems have thought processes
- ✅ Each is a coherent explanation (not empty)
- ✅ Describes reasoning steps

---

## Stage 2a: Abstraction (Original Prompt)

```bash
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace \
  abstraction.problem_solutions="experiments/aime_test_v3/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_test_v3/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_test_v3/abstraction_original"

# Verify
cat experiments/aime_test_v3/abstraction_original/lessons.json | jq 'keys | length'
# Should output: 10

# Check one lesson
cat experiments/aime_test_v3/abstraction_original/lessons.json | jq '.["2019-II-2"]'
```

**What to check:**
- ✅ All 10 problems have lessons
- ✅ Each has situation-suggestion pairs in YAML format
- ✅ Lessons are mathematical (not ARC/grid references)

---

## Stage 2b: Abstraction (Strict Prompt)

```bash
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_strict \
  abstraction.problem_solutions="experiments/aime_test_v3/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_test_v3/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_test_v3/abstraction_strict"

# Verify
cat experiments/aime_test_v3/abstraction_strict/lessons.json | jq 'keys | length'

# Compare with original
cat experiments/aime_test_v3/abstraction_strict/lessons.json | jq '.["2019-II-2"]'
```

**What to check:**
- ✅ Lessons are more concrete and specific
- ✅ Avoid problem-specific details
- ✅ At least one lesson encodes main key step

---

## Quality Comparison Checklist

For 2-3 sample problems, compare original vs strict:

### Original (`abstraction_original/`)
- [ ] Lesson quality
- [ ] Generalization level
- [ ] Concreteness of suggestions

### Strict (`abstraction_strict/`)
- [ ] Lesson quality
- [ ] Better generalization?
- [ ] More concrete suggestions?
- [ ] Captures key steps?

---

## Success Criteria

**Stage 1b (Thought Process):**
- ✓ 10/10 problems have explanations
- ✓ Explanations are coherent and describe reasoning

**Stage 2 (Abstraction):**
- ✓ 10/10 problems have situation-suggestion pairs
- ✓ Uses AIME-specific template (no ARC references)
- ✓ Lessons are generalizable

**Pick winner:** Original or Strict prompt for full 120-problem run

---

**Next:** Run stages 1b, 2a, 2b and evaluate which abstraction prompt is better


