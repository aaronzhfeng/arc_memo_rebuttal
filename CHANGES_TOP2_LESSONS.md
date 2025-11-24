# Top 2 Lessons + Self-Assessment Update

**Date**: 2025-11-20  
**Status**: Ready to test

## Changes Made

### 1. Self-Assessment Prompt
Added a line before lessons that gives the model agency:
```
If you consider this problem straightforward to solve, you may disregard the following lessons retrieved from other similar problems.
```

### 2. Limited to Top 2 Lessons
- Changed from 5 lessons to 2 lessons per problem
- Set via `prompt.hint_lessons_limit=2` parameter
- Keeps only the most relevant lessons from retrieval

## Example Prompt (With Memory)

```
Solve this AIME problem:

[Problem text here...]

If you consider this problem straightforward to solve, you may disregard the following lessons retrieved from other similar problems.

Lessons distilled from similar problems:

- situation: When a word problem involves changing ratios or fractions after an event...
  suggestion: Introduce variables for the unknown quantities, set up equations...

- situation: When you derive an equation with integer variables and a divisibility condition...
  suggestion: Translate the divisibility into a congruence (modular arithmetic)...

Output only the integer answer, and wrap it exactly once as \boxed{XYZ}.
```

## Rationale

### Why Self-Assessment?
Previous experiments showed memory **hurting** performance:
- Baseline: 73.33% pass@1
- With 5 lessons: 68.33% pass@1

**6 problems went from correct→wrong**, all of them easy problems where the model already had the right intuition but got distracted by lessons.

Self-assessment allows the model to:
- ✅ Ignore lessons on easy problems (prevent harm)
- ✅ Use lessons on hard problems (get help when needed)
- ✅ Self-calibrate based on confidence

### Why Top 2 Instead of 5?

1. **Less noise**: Lessons 3-5 are less relevant and may add confusion
2. **More thinking tokens**: Shorter prompts leave more budget for the model's thinking phase
3. **Better signal-to-noise ratio**: The top 2 lessons are most likely to be helpful
4. **Faster iteration**: Shorter prompts = faster generation

### Why Both Together?

The combination is powerful:
- **Top 2 lessons**: Reduces information overload
- **Self-assessment**: Gives model final say on whether to use them
- **Result**: Model gets high-quality hints but isn't forced to use them

## Testing

Run the quick comparison:
```bash
cd arc_memo
source .venv/bin/activate
# Follow RUN_AIME_QUICK.md
```

**Expected Results:**
- Baseline: ~73% pass@1 (unchanged)
- With top 2 lessons + self-assessment: **≥73% pass@1** (ideally higher)
- Easy problems (1-8): Should maintain baseline performance
- Hard problems (9-15): Should improve with lessons

## Files Modified

1. ✅ `arc_memo/concept_mem/data/aime_simple_solver_v3.py`
   - Added self-assessment instruction in `build_problem_prompt()`

2. ✅ `arc_memo_rebuttal/RUN_AIME_QUICK.md`
   - Added `prompt.hint_lessons_limit=2` to memory command
   - Updated documentation

3. ✅ `arc_memo_rebuttal/RUN_AIME_CORRECT_ONLY.md`
   - Added `prompt.hint_lessons_limit=2` to validation solve step

4. ✅ `arc_memo/docs/27_self_assessment_prompt_for_lessons.md`
   - Full design document with rationale

## Alternative Approaches Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Keep 5 lessons | More coverage | More noise, worse performance | ❌ Rejected |
| Reduce to 3 lessons | Middle ground | Still more than needed | ⚠️ Could try if 2 doesn't work |
| Reduce to 1 lesson | Minimal noise | Might miss important context | ⚠️ Could try if 2 is still too many |
| Skip lessons for easy problems | Targeted approach | Need to define "easy" | ❌ Too rigid |
| **Top 2 + self-assessment** | Best of both worlds | None identified | ✅ **Selected** |

## Success Metrics

### Must Have:
- ✅ pass@1 ≥ 73.33% (baseline)
- ✅ No problems go from correct→wrong on easy problems (1-8)

### Nice to Have:
- 🎯 pass@1 > 75% (beat baseline)
- 🎯 At least 2-3 hard problems (9-15) go from wrong→correct
- 🎯 pass@2 > 76.67% (current best)

### How to Check:
```bash
# After running RUN_AIME_QUICK.md
echo "=== Results ==="
grep "pass@1:" experiments_2p5/aime_val/*/aime_simple_solver_v3.log | tail -2
```

## Next Steps if This Works

1. ✅ Use top 2 lessons in all future runs
2. 🔄 Try top_k=1 to see if even less is more
3. 🔄 Analyze which problems actually use vs ignore lessons
4. 🔄 Consider different phrasings of self-assessment instruction
5. 🔄 Apply same approach to other domains (ARC puzzles, etc.)

## Next Steps if This Doesn't Work

1. ⚠️ Try top_k=3 (middle ground)
2. ⚠️ Remove self-assessment, keep top_k=2
3. ⚠️ Try different self-assessment phrasing
4. ⚠️ Consider retrieval quality improvements instead

