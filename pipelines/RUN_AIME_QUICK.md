# AIME Quick Comparison - Baseline vs Correct-Only Lessons

Quick two-command comparison to test if correct-only lessons improve performance.

**Setup:**

```bash
cd arc_memo
source .venv/bin/activate
export OPENAI_API_KEY="sk-your-openai-key"
export OPENROUTER_API_KEY="sk-or-your-openrouter-key"
```

---

## 1. Baseline (No Memory) - n=3, pass@2

```bash
BASELINE_RUN="experiments_2p5/aime_val/gemini_baseline_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="$BASELINE_RUN"
```

---

## 2. With Correct-Only Lessons (Top 2) - n=3, pass@2

Uses pre-extracted lessons from correctly solved training problems.
**Limits to top 2 most relevant lessons per problem.**

```bash
WITH_MEMORY_CORRECT_RUN="experiments_2p5/aime_val/gemini_with_memory_correct_top2_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="experiments/aime_val/selection_correct/prompt_info.json" \
  prompt.hint_lessons_limit=2 \
  generation.ignore_cache=true \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="$WITH_MEMORY_CORRECT_RUN"
```

---

## Quick Results Check

```bash
echo "=== Baseline ==="
grep "pass@1:" "$BASELINE_RUN/aime_simple_solver_v3.log" | tail -1

echo ""
echo "=== With Correct-Only Memory ==="
grep "pass@1:" "$WITH_MEMORY_CORRECT_RUN/aime_simple_solver_v3.log" | tail -1
```

---

**Notes:**
- `n=3`: Generate 3 attempts per problem
- `expand_multi=true`: Enables pass@2 evaluation (best 2 out of 3)
- Uses existing correct-only lessons from `experiments/aime_val/selection_correct/`
- **`prompt.hint_lessons_limit=2`**: Truncates to only the top 2 most relevant lessons per problem
- Both runs use Gemini 2.5 Flash Lite with 16k thinking budget
- **New**: The solver now includes a self-assessment prompt: "If you consider this problem straightforward to solve, you may disregard the following lessons..."

**Rationale for top_k=2:**
- Previous experiments with 5 lessons showed memory hurting performance (73.33% → 68.33%)
- Limiting to top 2 lessons reduces noise while keeping the most relevant guidance
- Combined with self-assessment prompt, gives model agency to ignore even these 2 lessons if problem is straightforward

