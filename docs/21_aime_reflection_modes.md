# AIME Reflection Modes

We now support three tiers of reasoning traces and lessons for AIME experiments:

1. **Direct solution narration** – produced when the solver answered correctly.
2. **Corrective reflection** – the existing mode that restates the correct approach after comparing the wrong answer with the ground truth.
3. **Mistake-only reflection** – a new mode that focuses on diagnosing the incorrect attempt and recording what *not* to do, without revealing the final answer.

This page explains how to generate each variant and how to build the corresponding memory for retrieval.

---

## Step 2 – Thought Process Generation (`concept_mem.data.aime_thought_process`)

Reflection style is controlled by the `abstraction.reflection_style` flag:

| Style | Behavior | Command snippet |
|-------|----------|-----------------|
| `corrective` *(default)* | Wrong or blank answers trigger the corrective template that contrasts the initial attempt with the true answer. | `python -m concept_mem.data.aime_thought_process +abstraction=aime_thought_process ... hydra.run.dir="experiments/aime_train/o4_reasoning"` |
| `mistake_only` | Wrong/blank answers trigger the new mistake-only template that highlights the flawed assumptions and preventative checks. | `python -m concept_mem.data.aime_thought_process +abstraction=aime_thought_process abstraction.reflection_style=mistake_only ... hydra.run.dir="experiments/aime_train/o4_reasoning_mistake"` |

Correct answers always use the original narration prompt regardless of the reflection style.

*(Default config: `configs/abstraction/aime_thought_process.yaml` – `reflection_style: corrective`)*

---

## Step 3 – Lesson Abstraction (`concept_mem.abstraction.analysis_concepts`)

Choose the abstraction config based on the reflection traces you want to use:

| Lessons | Config / Command | Thought-process input |
|---------|------------------|-----------------------|
| Standard strict lessons (corrective reflections) | `+abstraction=aime_lesson_from_trace_strict` | `experiments/aime_train/o4_reasoning/thought_processes.json` |
| Strict lessons filtered to correct solves only | `python ../arc_memo_rebuttal/aime_analysis/filter_correct_lessons.py --solutions="experiments/aime_train/o4_solve/solutions.json" --lessons-in="experiments/aime_train/abstraction/lessons.json" --lessons-out="experiments/aime_train/abstraction/lessons_correct.json"` | Same as above |
| Mistake-only “pitfall” lessons | `+abstraction=aime_lesson_from_trace_mistake` | `experiments/aime_train/o4_reasoning_mistake/thought_processes.json` |

Both configs live in `configs/abstraction/` and can be overridden on the CLI. Each run writes a separate `lessons.json` (e.g., `experiments/aime_train/abstraction/lessons.json` vs. `experiments/aime_train/abstraction_mistake/lessons.json`).

---

## Step 4 – Retrieval & Validation Runs

When you want to evaluate with different lesson sets, point the selection / inference steps to the appropriate `lessons.json`.

1. **Default lessons**
   ```bash
   python -m concept_mem.selection.description.select \
     selection=aime \
     selection.lesson_file="experiments/aime_train/abstraction/lessons.json" \
     model@selection.model=gpt41 \
     hydra.run.dir="experiments/aime_val/selection"

   python -m concept_mem.data.aime_simple_solver_v3 \
     data=aime_val \
     model=gemini_2_5_flash_lite_thinking \
     generation=gemini_thinking_16k \
     prompt.problem_data="experiments/aime_val/selection/prompt_info.json" \
     generation.ignore_cache=true \
     generation.max_tokens=4096 \
     generation.n=3 \
     hydra.run.dir="experiments/aime_val/gemini_with_memory"
   ```

2. **Correct-only lessons**
   ```bash
   python -m concept_mem.selection.description.select \
     selection=aime \
     selection.lesson_file="experiments/aime_train/abstraction/lessons_correct.json" \
     model@selection.model=gpt41 \
     hydra.run.dir="experiments/aime_val/selection_correct"

   python -m concept_mem.data.aime_simple_solver_v3 \
     data=aime_val \
     model=gemini_2_5_flash_lite_thinking \
     generation=gemini_thinking_16k \
     prompt.problem_data="experiments/aime_val/selection_correct/prompt_info.json" \
     generation.ignore_cache=true \
     generation.max_tokens=4096 \
     generation.n=3 \
     hydra.run.dir="experiments/aime_val/gemini_with_memory_correct"
   ```

3. **Mistake-only lessons**
   ```bash
   python -m concept_mem.selection.description.select \
     selection=aime \
     selection.lesson_file="experiments/aime_train/abstraction_mistake/lessons.json" \
     model@selection.model=gpt41 \
     hydra.run.dir="experiments/aime_val/selection_mistake"

   python -m concept_mem.data.aime_simple_solver_v3 \
     data=aime_val \
     model=gemini_2_5_flash_lite_thinking \
     generation=gemini_thinking_16k \
     prompt.problem_data="experiments/aime_val/selection_mistake/prompt_info.json" \
     generation.ignore_cache=true \
     generation.max_tokens=4096 \
     generation.n=3 \
     hydra.run.dir="experiments/aime_val/gemini_with_memory_mistake"
   ```

You can swap lesson files freely—both variants share the same retrieval pipeline, so you can compare performances directly.

---

## Summary

- **Step 2** now supports two reflection modes (`corrective`, `mistake_only`).
- **Step 3** produces strict lessons, a filtered strict subset (correct solves only), and pitfall lessons.
- **Step 4** simply consumes whichever lesson file you feed into the selection step.

Refer back to `RUN_AIME_COMPACT.md` for the condensed command list that stitches these options together.

