# AIME Prompt Adaptation

**Date:** 2025-11-19  
**Status:** ✅ Implemented

---

## Why ArcMemo Prompts Needed to Change

- **Original assumption:** ARC puzzles use grid inputs and expect a Python `transform()` implementation with color semantics.  
- **AIME reality:** Problems are natural-language math questions that require boxed integer answers, not grid programs.  
- **Failure mode:** Reusing the ARC prompts confused the solver, leading to irrelevant instructions (“treat colors as labels”) and fragile parsing (“Final Answer: X”).  
- **Goal:** Teach the model to output a single boxed integer while still allowing lesson retrieval to augment problem statements.

---

## Original ArcMemo Inference Prompt (for ARC puzzles)

Source: `Main/arc_memo/concept_mem/evaluation/prompts.py`

- System/User instructions expect grid data, e.g.:
  - “Write a Python function `transform(input_grid: np.ndarray) -> np.ndarray`…”
  - Procedures assume reference examples are numpy arrays with color labels.  
- Retry prompts restate grid-specific instructions and append concept hints drawn from ARC memory.
- Output parsing relies on code blocks or grid comparisons.

This design works for ARC but is incompatible with AIME where answers are integers and reasoning is text-based.

---

## AIME Solver Prompt (v3)

Source: `concept_mem/data/aime_simple_solver_v3.py`

Key components:

1. **System prompt** (`AIME_SYSTEM_PROMPT`):  
   - Explicitly states “You are solving AIME problems.”  
   - Forces the final answer to appear exactly once as `\boxed{XYZ}`.  
   - Forbids extra boxed expressions or free-standing integers.

2. **User prompt** (`build_problem_prompt`):  
   - Starts with “Solve this AIME problem:” followed by the raw problem text.  
   - Optionally appends retrieved lessons under “Lessons distilled from similar problems:”.  
   - Ends with `AIME_OUTPUT_REQUIREMENT`, reminding the model to output a single boxed integer.

3. **Extraction logic** (`extract_answer_from_response`):  
   - Prefers the last `\boxed{}` match but falls back to legacy heuristics when models fail.  
   - Logs whether a boxed form was used, enabling quality audits.

4. **Lesson truncation** (`truncate_hint_lessons`):  
   - Optional cap (`prompt.hint_lessons_limit`) so prompts remain short when many lessons are retrieved.

---

## Retrieval Integration

1. **Selection pipeline** (`concept_mem/selection/description/select.py` with `selection=aime`):  
   - Builds math-specific queries over the 459 lesson memory entries.  
   - Outputs `experiments/aime_val/selection/retrieved_lessons.json` and `prompt_info.json`.

2. **Prompt data file** (`prompt_info.json`):  
   - Maps each validation problem ID to `{ "aime_lessons": { "description": "...", "hint": "..." } }`.  
   - When passed as `prompt.problem_data=...`, the solver injects both a short external description and top-k lessons into the user prompt.

3. **Runtime switch:**  
   - Baseline run: omit `prompt.problem_data` to disable lessons.  
   - Memory run: set `prompt.problem_data="experiments/aime_val/selection/prompt_info.json"` (optionally choose a specific variant via `prompt.problem_data_variant`).

---

## Where the New Prompts Live

- `concept_mem/data/aime_simple_solver_v3.py` – system/user prompt templates, extraction rules.  
- `configs/data/aime_*.yaml` – dataset splits for AIME train/val/test.  
- `configs/selection/aime.yaml` – retrieval hyperparameters (top_k=5, lesson file path).  
- `experiments/aime_val/selection/prompt_info.json` – generated prompt augmentations consumed at inference time.  
- `concept_mem/evaluation/prompt_builder.py` – unchanged ARC builder; AIME bypasses it by constructing prompts directly in the solver.

---

## Running with the Adapted Prompts

Baseline (no retrieval):
```bash
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="experiments/aime_val/gemini_baseline"
```

With lessons:
```bash
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="experiments/aime_val/selection/prompt_info.json" \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="experiments/aime_val/gemini_with_memory"
```

The solver automatically detects the prompt data file, loads the `aime_lessons` variant, and appends both the retrieved description and lesson bullets to each problem.

---

## Follow-Up: Quality Checks

- Monitor `extraction_failures.json` for responses that still violate the boxing requirement.  
- Compare lesson usage by inspecting `experiments/aime_val/gemini_with_memory/full_responses.json` to verify that appended hints influence the reasoning.  
- Future improvement: tighten heuristics when the model ignores `\boxed{}` (e.g., reinforce via retry prompt or more explicit penalties).


