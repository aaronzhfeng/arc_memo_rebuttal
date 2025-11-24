# AIME Pipeline (Condensed)

Most runs follow the same four-stage loop. Execute from the `arc_memo/` repository with the virtualenv active:

```bash
cd arc_memo
source .venv/bin/activate
# replace with your keys or load from an .env
export OPENAI_API_KEY="sk-your-openai-key"
export OPENROUTER_API_KEY="sk-or-your-openrouter-key"
```

---

## 1. Warm-Start Solve (o4-mini → training set)

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

## 2. Thought Processes / Reflection (o4-mini)

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

### Optional: Mistake-only reflection

```bash
REASON_MISTAKE_RUN="experiments/aime_train/o4_reasoning_mistake_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="$SOLVE_RUN/solutions.json" \
  abstraction.reflection_style=mistake_only \
  data=aime_train \
  model=o4_mini \
  generation.max_tokens=8192 \
  hydra.run.dir="$REASON_MISTAKE_RUN"
```

---

## 3. Memory Abstraction (gpt-4.1)

```bash
ABSTRACT_RUN="experiments/aime_train/abstraction_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_strict \
  abstraction.problem_solutions="$SOLVE_RUN/solutions.json" \
  abstraction.thought_processes="$REASON_RUN/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="$ABSTRACT_RUN"

python ../arc_memo_rebuttal/aime_analysis/filter_correct_lessons.py \
  --solutions="$SOLVE_RUN/solutions.json" \
  --lessons-in="$ABSTRACT_RUN/lessons.json" \
  --lessons-out="$ABSTRACT_RUN/lessons_correct.json"
```

### Optional: Mistake-only abstraction

```bash
ABSTRACT_MISTAKE_RUN="experiments/aime_train/abstraction_mistake_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_mistake \
  abstraction.problem_solutions="$SOLVE_RUN/solutions.json" \
  abstraction.thought_processes="$REASON_MISTAKE_RUN/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="$ABSTRACT_MISTAKE_RUN"
```

---

## 4. Validation Inference (Gemini 2.5 Flash Lite)

### 4a. Baseline (no retrieval)

```bash
BASELINE_RUN="experiments/aime_val/gemini_baseline_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="$BASELINE_RUN"
```

### 4b. With memory (default lessons)

If you haven’t generated `prompt_info.json` yet:

```bash
SELECTION_RUN="experiments/aime_val/selection_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.selection.description.select \
  selection=aime \
  selection.lesson_file="$ABSTRACT_RUN/lessons.json" \
  model@selection.model=gpt41 \
  hydra.run.dir="$SELECTION_RUN"
```

Then run inference:

```bash
WITH_MEMORY_RUN="experiments/aime_val/gemini_with_memory_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_RUN/prompt_info.json" \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="$WITH_MEMORY_RUN"
```

### 4c. With memory (correct-only lessons)

```bash
SELECTION_CORRECT_RUN="experiments/aime_val/selection_correct_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.selection.description.select \
  selection=aime \
  selection.lesson_file="$ABSTRACT_RUN/lessons_correct.json" \
  model@selection.model=gpt41 \
  hydra.run.dir="$SELECTION_CORRECT_RUN"
```

```bash
WITH_MEMORY_CORRECT_RUN="experiments/aime_val/gemini_with_memory_correct_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_CORRECT_RUN/prompt_info.json" \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="$WITH_MEMORY_CORRECT_RUN"
```

### 4d. With memory (mistake-only lessons)

```bash
SELECTION_MISTAKE_RUN="experiments/aime_val/selection_mistake_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.selection.description.select \
  selection=aime \
  selection.lesson_file="$ABSTRACT_MISTAKE_RUN/lessons.json" \
  model@selection.model=gpt41 \
  hydra.run.dir="$SELECTION_MISTAKE_RUN"
```

```bash
WITH_MEMORY_MISTAKE_RUN="experiments/aime_val/gemini_with_memory_mistake_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_MISTAKE_RUN/prompt_info.json" \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="$WITH_MEMORY_MISTAKE_RUN"
```

---

*See `docs/21_aime_reflection_modes.md` for a deeper explanation of the reflection variants and when to use each pipeline branch.*

