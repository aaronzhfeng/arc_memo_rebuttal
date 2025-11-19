# AIME Lesson Format Verification

**Date:** 2025-11-18  
**Status:** ✅ Verified - Format matches ArcMemo's lesson system exactly

---

## Summary

**AIME Training Results:**
- 97 problems with valid data (2019-2022)
- 459 total situation-suggestion pairs
- Average: 4.7 lessons per problem
- Format: `{problem_id: [{"situation": "...", "suggestion": "..."}, ...]}`

**Comparison with ARC:**
- ARC: ~600+ lessons from 160 problems (avg 3.8 per problem)
- AIME: 459 lessons from 97 problems (avg 4.7 per problem)
- **Same format structure** ✓

---

## Format Structure

### Current AIME Format (Correct!)

```json
{
  "2020-I-1": [
    {
      "situation": "When a geometry problem involves...",
      "suggestion": "Scale the figure so that..."
    },
    {
      "situation": "When a triangle has symmetry...",
      "suggestion": "Introduce a variable..."
    }
  ],
  "2020-I-2": [...]
}
```

**This is exactly what ArcMemo expects!** ✅

---

## How Retrieval Works

### Step 1: Flatten During Selection

**Code** (`concept_mem/selection/description/select.py` lines 194-204):
```python
concept_entries = []
concept_number_to_uid = {}
num = 0
for uid in sorted(lessons.keys()):
    for i, lesson in enumerate(lessons[uid]):
        num += 1
        entry = f"lesson {num}.\n- situation: {lesson['situation']}\n- suggestion: {lesson['suggestion']}"
        concept_entries.append(entry)
        concept_number_to_uid[num] = (uid, i)
```

**Result:** Creates a numbered list 1-459 with source tracking

### Step 2: LLM Selects Top-K

**Prompt:** Shows problem + numbered lesson list (1-459)
**Output:** Top-K lesson numbers (e.g., `[45, 234, 389, 12, 156]`)

### Step 3: Map Back to Source

```python
selected_lessons = [concept_number_to_uid[num] for num in [45, 234, ...]]
# Returns: [("2020-I-10", 2), ("2021-I-15", 3), ...]
```

### Step 4: Format for Solve Prompt

```python
formatted_hint = "\n".join([
    f"- situation: {lessons[uid][idx]['situation']}\n  suggestion: {lessons[uid][idx]['suggestion']}"
    for uid, idx in selected_lessons
])
```

---

## Files & Locations

### Generated Files (Ready!)
```
experiments/aime_train/abstraction/lessons.json  ← 459 AIME lessons
```

### Config Files (Created)
```
configs/selection/aime.yaml  ← AIME selection config
```

### Usage
```bash
python -m concept_mem.selection.description.select \
  selection@=aime \
  hydra.run.dir="experiments/aime_val/selection"
```

---

## Verification Commands

**Count total lessons:**
```bash
cat experiments/aime_train/abstraction/lessons.json | jq '[.[] | length] | add'
# Output: 459
```

**Count problems:**
```bash
cat experiments/aime_train/abstraction/lessons.json | jq 'keys | length'
# Output: 97
```

**Check format matches ARC:**
```bash
# AIME sample
cat experiments/aime_train/abstraction/lessons.json | jq '.["2020-I-1"][0]'

# ARC sample  
cat data/lessons/from_trace_fs/parsed_lessons.json | jq '.[keys[0]][0]'

# Both have: {"situation": "...", "suggestion": "..."}
```

---

## Lesson Quality Stats

**Distribution by problem:**
- Most lessons per problem: 6 (2022-I-11, 2020-I-12)
- Fewest lessons: 1 (2021-I-2, 2020-II-12)
- Median: 4-5 lessons per problem

**Domain coverage:**
- Geometry problems: 20-30% (coordinate geometry, circles, triangles)
- Algebra problems: 20-25% (polynomials, systems, logs)
- Number theory: 20-25% (divisibility, modular arithmetic, primes)
- Combinatorics: 20-25% (counting, arrangements, PIE)
- Probability: 10-15% (Markov chains, expected values)

---

## Next Steps

1. ✅ **Format verified** - No conversion needed
2. ✅ **Config created** - `configs/selection/aime.yaml`
3. ⏳ **Test selection** - Run on validation set
4. ⏳ **Run with memory** - Compare baseline vs with-memory

---

**Status:** ✅ Format verified, ready for selection and inference

