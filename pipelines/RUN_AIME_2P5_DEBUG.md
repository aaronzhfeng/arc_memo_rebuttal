# AIME Pipeline – Gemini 2.5 ("2p5") Self-Reflection – DEBUG (1 problem)

Single-problem debug run to verify the entire pipeline works correctly.

> **Setup**
> ```bash
> cd arc_memo
> source .venv/bin/activate
> export OPENAI_API_KEY="sk-your-openai-key"
> export OPENROUTER_API_KEY="sk-or-your-openrouter-key"
> ```

---

## 1. Joint Solve + Thought Process (1 problem: 2020-I-1)

```bash
JOINT_RUN="experiments_2p5_debug/aime_train/joint_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_joint_solver \
  data=aime_train_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  hydra.run.dir="$JOINT_RUN"
```

This produces:
- `solutions.json` with extracted integer (should be 547)
- `joint_responses.json` storing the full reasoning + final answer

---

## 2. Self-Reflection (1 problem)

```bash
REFLECT_RUN="experiments_2p5_debug/aime_train/self_reflect_$(date +"%Y%m%d-%H%M%S")"
JOINT_RUN=$(ls -td experiments_2p5_debug/aime_train/joint_* | head -n1)
python -m concept_mem.data.aime_self_reflection \
  data=aime_train_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  +joint_responses_file="$JOINT_RUN/joint_responses.json" \
  hydra.run.dir="$REFLECT_RUN"
```

Outputs `thought_processes.json`, containing the refined narrative with no external correctness signal.

---

## 3. Lesson Abstraction (Gemini 2.5, uncertain reflections)

```bash
ABSTRACT_UNCERTAIN_RUN="experiments_2p5_debug/aime_train/abstraction_uncertain_$(date +"%Y%m%d-%H%M%S")"
JOINT_RUN=$(ls -td experiments_2p5_debug/aime_train/joint_* | head -n1)
REFLECT_RUN=$(ls -td experiments_2p5_debug/aime_train/self_reflect_* | head -n1)
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_uncertain \
  abstraction.problem_solutions="$JOINT_RUN/solutions.json" \
  abstraction.thought_processes="$REFLECT_RUN/thought_processes.json" \
  model=gemini_2_5_flash_lite_thinking \
  abstraction.generation.ignore_cache=true \
  hydra.run.dir="$ABSTRACT_UNCERTAIN_RUN"
```

**Expected**: Prompt should start with "### Introduction\n\nYou are analyzing a self-reflection on an AIME..." (the AIME strict uncertain template), NOT the ARC puzzle template.

---

## 4. Lesson Retrieval for Validation (Gemini 2.5, 1 validation problem: 2024_I_10 - geometry)

**Note**: Clear cache before running to avoid cached responses:
```bash
# Clear LLM cache to force fresh responses
rm -rf cache/*
```

```bash
SELECTION_UNCERTAIN_RUN="experiments_2p5_debug/aime_val/selection_uncertain_$(date +"%Y%m%d-%H%M%S")"
ABSTRACT_UNCERTAIN_RUN=$(ls -td experiments_2p5_debug/aime_train/abstraction_uncertain_* | head -n1)
python -m concept_mem.selection.description.select \
  selection=aime \
  selection.problems=data/aime/validation_ids_debug.json \
  selection.description_file=data/aime/validation_debug.json \
  selection.lesson_file="$ABSTRACT_UNCERTAIN_RUN/lessons.json" \
  model@selection.model=gemini_2_5_flash_lite_thinking \
  generation@selection.generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.seed=null \
  selection.generation.ignore_cache=true \
  selection.generation.seed=null \
  selection.generation.max_tokens=8192 \
  hydra.run.dir="$SELECTION_UNCERTAIN_RUN"
```

**Expected**: Should retrieve relevant lessons from the training problem for the validation problem.

---

## 5. Validation Solve with Retrieved Lessons (Gemini 2.5, 1 problem)

```bash
WITH_MEMORY_UNCERTAIN_RUN="experiments_2p5_debug/aime_val/gemini_with_memory_uncertain_$(date +"%Y%m%d-%H%M%S")"
SELECTION_UNCERTAIN_RUN=$(ls -td experiments_2p5_debug/aime_val/selection_uncertain_* | head -n1)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_UNCERTAIN_RUN/prompt_info.json" \
  generation.ignore_cache=true \
  hydra.run.dir="$WITH_MEMORY_UNCERTAIN_RUN"
```

**Expected**: Should solve the validation problem using the retrieved lessons as hints.

---

## 6. Baseline Solve (Gemini 2.5, no retrieval, 1 problem)

```bash
BASELINE_RUN="experiments_2p5_debug/aime_val/gemini_baseline_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  hydra.run.dir="$BASELINE_RUN"
```

**Expected**: Should solve the validation problem without any lesson hints (baseline comparison).

---

## Verification Commands

After each step, verify the outputs:

```bash
# Step 1: Check joint solve output
JOINT_RUN=$(ls -td experiments_2p5_debug/aime_train/joint_* | head -n1)
echo "=== Step 1: Joint Solutions ==="
cat "$JOINT_RUN/solutions.json" | python3 -m json.tool
echo ""

# Step 2: Check reflection output
REFLECT_RUN=$(ls -td experiments_2p5_debug/aime_train/self_reflect_* | head -n1)
echo "=== Step 2: Thought Processes ==="
cat "$REFLECT_RUN/thought_processes.json" | python3 -c "import json, sys; d=json.load(sys.stdin); print(f'Keys: {list(d.keys())}'); print(f'First 200 chars: {list(d.values())[0][:200]}')"
echo ""

# Step 3: Check abstraction prompt and lessons
ABSTRACT_RUN=$(ls -td experiments_2p5_debug/aime_train/abstraction_uncertain_* | head -n1)
echo "=== Step 3: Abstraction Prompt (first 500 chars) ==="
cat "$ABSTRACT_RUN/prompts.json" | python3 -c "import json, sys; d=json.load(sys.stdin); print(d[0][:500])"
echo ""

echo "=== Step 3: Abstraction Lessons ==="
cat "$ABSTRACT_RUN/lessons.json" | python3 -c "import json, sys; d=json.load(sys.stdin); print(f'Number of lessons: {len(d)}'); print(f'Lesson keys: {list(d.keys())}'); [print(f'  - {lesson[\"situation\"][:80]}...') for problem_lessons in d.values() for lesson in problem_lessons[:2]]"
echo ""

echo "=== Step 3: Abstraction Logs ==="
grep -i "loaded.*thought\|first problem\|domain_template" "$ABSTRACT_RUN/analysis_concepts.log"
echo ""

# Step 4: Check lesson retrieval
if [ -d "experiments_2p5_debug/aime_val" ]; then
  SELECTION_RUN=$(ls -td experiments_2p5_debug/aime_val/selection_uncertain_* 2>/dev/null | head -n1)
  if [ -n "$SELECTION_RUN" ]; then
    echo "=== Step 4: Lesson Retrieval ==="
    cat "$SELECTION_RUN/prompt_info.json" | python3 -c "import json, sys; d=json.load(sys.stdin); print(f'Problems: {list(d.keys())}'); [print(f'Problem {pid}: {len(info.get(\"default\", {}).get(\"lessons\", []))} lessons retrieved') for pid, info in d.items()]"
    echo ""
  fi
fi

# Step 5: Check validation solve with memory
if [ -d "experiments_2p5_debug/aime_val" ]; then
  WITH_MEMORY_RUN=$(ls -td experiments_2p5_debug/aime_val/gemini_with_memory_uncertain_* 2>/dev/null | head -n1)
  if [ -n "$WITH_MEMORY_RUN" ]; then
    echo "=== Step 5: Validation Solve (with lessons) ==="
    cat "$WITH_MEMORY_RUN/solutions.json" | python3 -m json.tool
    echo ""
  fi
  
  # Step 6: Check baseline solve
  BASELINE_RUN=$(ls -td experiments_2p5_debug/aime_val/gemini_baseline_* 2>/dev/null | head -n1)
  if [ -n "$BASELINE_RUN" ]; then
    echo "=== Step 6: Baseline Solve (no lessons) ==="
    cat "$BASELINE_RUN/solutions.json" | python3 -m json.tool
    echo ""
  fi
fi

echo "=== All Verification Complete ==="
```

