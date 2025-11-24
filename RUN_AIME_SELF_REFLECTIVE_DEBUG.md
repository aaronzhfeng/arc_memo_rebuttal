# AIME Self-Reflective Pipeline - DEBUG (Single Problem)

**Purpose**: Test the self-reflective pipeline on a single problem to inspect prompts, lessons, and outputs in detail.

**Training Problem**: `2020-I-1` (geometry)  
**Validation Problem**: `2024_I_10` (geometry, matching domain)

**Output Directory**: `experiments_self_reflective/debug/`

---

## Setup

```bash
cd arc_memo
source .venv/bin/activate
export OPENAI_API_KEY="sk-your-openai-key"
export OPENROUTER_API_KEY="sk-or-your-openrouter-key"

# Clear cache to ensure fresh runs
rm -rf cache/*
```

---

## Stage 1: Joint Solve (1 training problem)

```bash
JOINT_RUN="experiments_self_reflective/debug/joint_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_joint_solver \
  data=aime_train_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.seed=null \
  hydra.run.dir="$JOINT_RUN"
```

**Verify**: 
```bash
cat "$JOINT_RUN/solutions.json"
cat "$JOINT_RUN/joint_responses.json" | python -m json.tool | head -50
```

---

## Stage 2: Self-Reflection (1 problem)

```bash
REFLECT_RUN="experiments_self_reflective/debug/self_reflect_$(date +"%Y%m%d-%H%M%S")"
JOINT_RUN=$(ls -td experiments_self_reflective/debug/joint_* | head -n1)
python -m concept_mem.data.aime_self_reflection \
  data=aime_train_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.seed=null \
  +joint_responses_file="$JOINT_RUN/joint_responses.json" \
  hydra.run.dir="$REFLECT_RUN"
```

**Verify**: 
```bash
cat "$REFLECT_RUN/thought_processes.json" | python -m json.tool | head -50
```

---

## Stage 3: Lesson Abstraction (1 problem → N lessons)

```bash
ABSTRACT_RUN="experiments_self_reflective/debug/abstraction_$(date +"%Y%m%d-%H%M%S")"
JOINT_RUN=$(ls -td experiments_self_reflective/debug/joint_* | head -n1)
REFLECT_RUN=$(ls -td experiments_self_reflective/debug/self_reflect_* | head -n1)
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_uncertain \
  abstraction.problem_solutions="$JOINT_RUN/solutions.json" \
  abstraction.thought_processes="$REFLECT_RUN/thought_processes.json" \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.seed=null \
  hydra.run.dir="$ABSTRACT_RUN"
```

**Verify**: 
```bash
echo "=== Extracted Lessons ==="
cat "$ABSTRACT_RUN/lessons.json" | python -m json.tool
```

---

## Stage 4: Lesson Retrieval (1 validation problem)

```bash
SELECTION_RUN="experiments_self_reflective/debug/selection_$(date +"%Y%m%d-%H%M%S")"
ABSTRACT_RUN=$(ls -td experiments_self_reflective/debug/abstraction_* | head -n1)
python -m concept_mem.selection.description.select \
  data=aime_val_debug \
  selection.lesson_file="$ABSTRACT_RUN/lessons.json" \
  model@selection.model=gemini_2_5_flash_lite_thinking \
  selection.generation.max_tokens=32000 \
  +selection.generation.extra_kwargs.extra_body.reasoning.max_tokens=8000 \
  selection.generation.ignore_cache=true \
  selection.generation.seed=null \
  hydra.run.dir="$SELECTION_RUN"
```

**Verify**: 
```bash
echo "=== Retrieved Lesson UIDs ==="
cat "$SELECTION_RUN/retrieved_concept_uids.json" | python -m json.tool

echo ""
echo "=== Formatted Prompt Info ==="
cat "$SELECTION_RUN/prompt_info.json" | python -m json.tool
```

---

## Stage 5: Validation Solve WITHOUT Memory (Baseline)

```bash
BASELINE_RUN="experiments_self_reflective/debug/baseline_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.seed=null \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="$BASELINE_RUN"
```

---

## Stage 6: Validation Solve WITH Memory (Top 2 Lessons)

```bash
WITH_MEMORY_RUN="experiments_self_reflective/debug/with_memory_top2_$(date +"%Y%m%d-%H%M%S")"
SELECTION_RUN=$(ls -td experiments_self_reflective/debug/selection_* | head -n1)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_RUN/prompt_info.json" \
  prompt.hint_lessons_limit=2 \
  generation.ignore_cache=true \
  generation.seed=null \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="$WITH_MEMORY_RUN"
```

---

## Inspect Full Prompts

```bash
# Show the actual prompt sent to the model (with top 2 lessons)
echo "=== Full Prompt with Top 2 Lessons ==="
cat "$WITH_MEMORY_RUN/prompts.json" | python -m json.tool

# Show the response
echo ""
echo "=== Model Response ==="
cat "$WITH_MEMORY_RUN/full_responses.json" | python -m json.tool
```

---

## Compare Results

```bash
echo "=== Baseline Answer ==="
cat "$BASELINE_RUN/solutions.json"

echo ""
echo "=== With Memory Answer ==="
cat "$WITH_MEMORY_RUN/solutions.json"

echo ""
echo "=== Ground Truth ==="
echo "2024_I_10 should be: 113"
```

---

## Prompt Inspection Helper

```bash
# Extract and view the exact lesson text that was provided
SELECTION_RUN=$(ls -td experiments_self_reflective/debug/selection_* | head -n1)
python3 << 'EOF'
import json
with open('$SELECTION_RUN/prompt_info.json') as f:
    data = json.load(f)
problem_id = list(data.keys())[0]
hint = data[problem_id].get('aime_lessons', {}).get('hint', '')
print("=== Lesson Text Provided to Model ===")
print(hint)
EOF
```

---

## Key Inspection Points

1. **Lesson Quality**: Check if extracted lessons make sense
2. **Retrieval Relevance**: Are the top 2 lessons actually relevant?
3. **Prompt Format**: Does the self-assessment + lessons look good?
4. **Model Behavior**: Did the model use or ignore the lessons?
5. **Answer Quality**: Did memory help or hurt?

---

## Debugging Tips

- **If lessons are bad**: Adjust abstraction prompt or use different model
- **If retrieval is poor**: Check selection prompt and max_tokens
- **If memory hurts**: Lessons might be too specific or irrelevant
- **If memory doesn't help**: Lessons might be too generic or obvious

---

## Analysis & Reports (Automatic)

Generate evaluation reports and analysis in the debug folder:

```bash
# Set up analysis directory
ANALYSIS_DIR="experiments_self_reflective/debug/analysis"
mkdir -p "$ANALYSIS_DIR"

# 1. Evaluate baseline
BASELINE_RUN=$(ls -td experiments_self_reflective/debug/baseline_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $BASELINE_RUN)/solutions.json" \
  --dataset="data/aime/validation_debug.json" \
  --output="$(realpath --relative-to=. $BASELINE_RUN)/evaluation_results.json"

# 2. Evaluate with memory
WITH_MEMORY_RUN=$(ls -td experiments_self_reflective/debug/with_memory_top2_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $WITH_MEMORY_RUN)/solutions.json" \
  --dataset="data/aime/validation_debug.json" \
  --output="$(realpath --relative-to=. $WITH_MEMORY_RUN)/evaluation_results.json"

# 3. Cost analysis (all debug runs)
python ../arc_memo_rebuttal/aime_analysis/analyze_costs.py \
  --experiments-dir="experiments_self_reflective/debug" \
  > "$ANALYSIS_DIR/cost_analysis.txt"

echo ""
echo "=== Analysis Complete ==="
echo "Baseline evaluation: $BASELINE_RUN/evaluation_results.json"
echo "With memory evaluation: $WITH_MEMORY_RUN/evaluation_results.json"
echo "Cost analysis: $ANALYSIS_DIR/cost_analysis.txt"
```

---

## Quick Results Summary

```bash
echo "=== SELF-REFLECTIVE DEBUG SUMMARY ==="
echo ""
echo "Training Problem: 2020-I-1 (expected: 803)"
echo "Validation Problem: 2024_I_10 (expected: 113)"
echo ""

BASELINE_RUN=$(ls -td experiments_self_reflective/debug/baseline_* | head -n1)
WITH_MEMORY_RUN=$(ls -td experiments_self_reflective/debug/with_memory_top2_* | head -n1)

echo "--- Baseline (No Memory) ---"
cat "$BASELINE_RUN/solutions.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Answer: {list(d.values())[0]}')"
if [ -f "$BASELINE_RUN/evaluation_results.json" ]; then
  cat "$BASELINE_RUN/evaluation_results.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Correct: {d[\"correct\"]}/{d[\"total\"]}')"
fi

echo ""
echo "--- With Memory (Top 2 Lessons) ---"
cat "$WITH_MEMORY_RUN/solutions.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Answer: {list(d.values())[0]}')"
if [ -f "$WITH_MEMORY_RUN/evaluation_results.json" ]; then
  cat "$WITH_MEMORY_RUN/evaluation_results.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Correct: {d[\"correct\"]}/{d[\"total\"]}')"
fi

echo ""
echo "--- Retrieved Lessons ---"
SELECTION_RUN=$(ls -td experiments_self_reflective/debug/selection_* | head -n1)
echo "Top lessons used:"
cat "$SELECTION_RUN/retrieved_concept_uids.json" | python -m json.tool
```

