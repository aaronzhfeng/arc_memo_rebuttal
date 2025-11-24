# AIME Pipeline - Correct-Only Lessons

> **⚠️ DEPRECATED**: This file has been superseded by `RUN_AIME_LABEL_GUIDED.md`
> 
> **New structure**:
> - Better naming: "Label-Guided" clearly describes the label-filtering approach
> - Organized outputs: `experiments_label_guided/` directory
> - Debug workflow: `RUN_AIME_LABEL_GUIDED_DEBUG.md` for single-problem testing
> - See `README_PIPELINES.md` for full comparison
>
> The commands below are preserved for reference but should use the new files.

---

Pipeline for extracting lessons from correct solutions only and evaluating on validation set.

Execute from the `arc_memo/` repository with the virtualenv active:

```bash
cd arc_memo
source .venv/bin/activate
# replace with your keys or load from an .env
export OPENAI_API_KEY="sk-your-openai-key"
export OPENROUTER_API_KEY="sk-or-your-openrouter-key"
```

---

## 1. Baseline (No Memory)

```bash
BASELINE_RUN="experiments/aime_val/gemini_baseline_$(date +"%Y%m%d-%H%M%S")"
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

## 2. Training: Solve (o4-mini → training set)

```bash
SOLVE_RUN="experiments/aime_train/o4_solve_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_train \
  model=o4_mini \
  generation=o4_solve \
  generation.ignore_cache=true \
  hydra.run.dir="$SOLVE_RUN"
```

---

## 3. Training: Thought Processes (o4-mini)

```bash
REASON_RUN="experiments/aime_train/o4_reasoning_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="$SOLVE_RUN/solutions.json" \
  data=aime_train \
  model=o4_mini \
  generation.max_tokens=8192 \
  hydra.run.dir="$REASON_RUN"
```

---

## 4. Training: Lesson Abstraction (gpt-4.1)

```bash
ABSTRACT_RUN="experiments/aime_train/abstraction_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_strict \
  abstraction.problem_solutions="$SOLVE_RUN/solutions.json" \
  abstraction.thought_processes="$REASON_RUN/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="$ABSTRACT_RUN"

# Filter to keep only lessons from correctly solved problems
python ../arc_memo_rebuttal/aime_analysis/filter_correct_lessons.py \
  --solutions="$SOLVE_RUN/solutions.json" \
  --lessons-in="$ABSTRACT_RUN/lessons.json" \
  --lessons-out="$ABSTRACT_RUN/lessons_correct.json"
```

---

## 5. Validation: Lesson Retrieval (gpt-4.1)

```bash
SELECTION_CORRECT_RUN="experiments/aime_val/selection_correct_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.selection.description.select \
  selection=aime \
  data=aime_val \
  model=gpt41 \
  selection.problems=data/aime/validation_ids.json \
  selection.lesson_file="$ABSTRACT_RUN/lessons_correct.json" \
  selection.description_file=data/aime/validation.json \
  selection.generation.ignore_cache=true \
  selection.generation.max_tokens=16384 \
  selection.generation.seed=null \
  hydra.run.dir="$SELECTION_CORRECT_RUN"
```

---

## 6. Validation: Solve with Memory (Top 2 Lessons)

```bash
WITH_MEMORY_CORRECT_RUN="experiments/aime_val/gemini_with_memory_correct_top2_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_CORRECT_RUN/prompt_info.json" \
  prompt.hint_lessons_limit=2 \
  generation.ignore_cache=true \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="$WITH_MEMORY_CORRECT_RUN"
```

**Note**: `prompt.hint_lessons_limit=2` truncates to only the top 2 most relevant lessons per problem.

---

## Results Comparison

```bash
echo "=== Baseline (No Memory) ==="
cat "$BASELINE_RUN/solutions.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Solved: {len([v for v in d.values() if v])}/{len(d)}')"

echo ""
echo "=== With Memory (Correct-Only Lessons) ==="
cat "$WITH_MEMORY_CORRECT_RUN/solutions.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Solved: {len([v for v in d.values() if v])}/{len(d)}')"
```

---

## Notes

- **Baseline first**: Run baseline to establish performance without memory
- **Correct-only lessons**: Only extract lessons from problems the model solved correctly
- **Higher max_tokens for retrieval**: 16384 tokens to avoid truncation during lesson selection
- **seed=null**: Ensures non-deterministic generation to avoid cache loops

