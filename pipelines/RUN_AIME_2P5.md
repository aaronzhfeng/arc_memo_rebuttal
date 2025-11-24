# AIME Pipeline – Gemini 2.5 ("2p5") Self-Reflection

> **⚠️ DEPRECATED**: This file has been superseded by `RUN_AIME_SELF_REFLECTIVE.md`
> 
> **New structure**:
> - Better naming: "Self-Reflective" clearly describes the approach
> - Organized outputs: `experiments_self_reflective/` directory
> - Debug workflow: `RUN_AIME_SELF_REFLECTIVE_DEBUG.md` for single-problem testing
> - See `README_PIPELINES.md` for full comparison
>
> The commands below are preserved for reference but should use the new files.

---

The commands below keep the entire training and evaluation loop within Gemini 2.5 Flash Lite (Thinking). Every stage writes into a timestamped directory so multiple runs can coexist.

> **Setup**
> ```bash
> cd arc_memo
> source .venv/bin/activate
> export OPENAI_API_KEY="sk-your-openai-key"
> export OPENROUTER_API_KEY="sk-or-your-openrouter-key"
> ```

---

## 1. Joint Solve + Thought Process (120 training problems)

```bash
JOINT_RUN="experiments_2p5/aime_train/joint_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_joint_solver \
  data=aime_train \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  hydra.run.dir="$JOINT_RUN"
```

This produces:
- `solutions.json` with extracted integers
- `joint_responses.json` storing the full reasoning + final answer for each problem

---

## 2. Self-Reflection (120 training problems)

```bash
REFLECT_RUN="experiments_2p5/aime_train/self_reflect_$(date +"%Y%m%d-%H%M%S")"
JOINT_RUN=$(ls -td experiments_2p5/aime_train/joint_* | head -n1)
python -m concept_mem.data.aime_self_reflection \
  data=aime_train \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  +joint_responses_file="$JOINT_RUN/joint_responses.json" \
  hydra.run.dir="$REFLECT_RUN"
```

Outputs `thought_processes.json`, containing the refined narratives with no external correctness signal.

---

## 3. Lesson Abstraction (Gemini 2.5, uncertain reflections)

```bash
ABSTRACT_UNCERTAIN_RUN="experiments_2p5/aime_train/abstraction_uncertain_$(date +"%Y%m%d-%H%M%S")"
JOINT_RUN=$(ls -td experiments_2p5/aime_train/joint_* | head -n1)
REFLECT_RUN=$(ls -td experiments_2p5/aime_train/self_reflect_* | head -n1)
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_uncertain \
  abstraction.problem_solutions="$JOINT_RUN/solutions.json" \
  abstraction.thought_processes="$REFLECT_RUN/thought_processes.json" \
  model=gemini_2_5_flash_lite_thinking \
  abstraction.generation.ignore_cache=true \
  hydra.run.dir="$ABSTRACT_UNCERTAIN_RUN"
```

---

## 4. Lesson Retrieval for Validation (Gemini 2.5)

```bash
SELECTION_UNCERTAIN_RUN="experiments_2p5/aime_val/selection_uncertain_$(date +"%Y%m%d-%H%M%S")"
ABSTRACT_UNCERTAIN_RUN=$(ls -td experiments_2p5/aime_train/abstraction_uncertain_* | head -n1)
python -m concept_mem.selection.description.select \
  selection=aime \
  selection.lesson_file="$ABSTRACT_UNCERTAIN_RUN/lessons.json" \
  model@selection.model=gemini_2_5_flash_lite_thinking \
  generation@selection.generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  selection.generation.ignore_cache=true \
  selection.generation.max_tokens=16384 \
  selection.generation.seed=null \
  hydra.run.dir="$SELECTION_UNCERTAIN_RUN"
```

---

## 5. Validation Solve with Retrieved Lessons (Gemini 2.5)

```bash
WITH_MEMORY_UNCERTAIN_RUN="experiments_2p5/aime_val/gemini_with_memory_uncertain_$(date +"%Y%m%d-%H%M%S")"
SELECTION_UNCERTAIN_RUN=$(ls -td experiments_2p5/aime_val/selection_uncertain_* | head -n1)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_UNCERTAIN_RUN/prompt_info.json" \
  generation.ignore_cache=true \
  hydra.run.dir="$WITH_MEMORY_UNCERTAIN_RUN"
```

---

## Baseline Reference (Gemini 2.5, no retrieval)

```bash
BASELINE_RUN="experiments_2p5/aime_val/gemini_baseline_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  hydra.run.dir="$BASELINE_RUN"
```

Use the baseline to gauge raw solver accuracy before comparing the uncertain self-reflection variant.

