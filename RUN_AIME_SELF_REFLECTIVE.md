# AIME Pipeline: Self-Reflective Learning

**Approach**: Extract lessons from the model's self-reflection on its own reasoning, without using ground truth labels.

**Philosophy**: The model learns by critiquing and improving its own thought process, developing meta-cognitive reasoning skills.

**Output Directory**: `experiments_self_reflective/`

---

## Setup

```bash
cd arc_memo
source .venv/bin/activate
export OPENAI_API_KEY="sk-your-openai-key"
export OPENROUTER_API_KEY="sk-or-your-openrouter-key"
```

---

## Stage 1: Joint Solve (Training - 120 problems)

Generate initial solutions and reasoning traces.

```bash
JOINT_RUN="experiments_self_reflective/aime_train/joint_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_joint_solver \
  data=aime_train \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  hydra.run.dir="$JOINT_RUN"
```

**Outputs**: 
- `solutions.json` - Extracted integer answers
- `joint_responses.json` - Full reasoning + answers

---

## Stage 2: Self-Reflection (Training - 120 problems)

Model reflects on its own reasoning to produce improved thought processes.

```bash
REFLECT_RUN="experiments_self_reflective/aime_train/self_reflect_$(date +"%Y%m%d-%H%M%S")"
JOINT_RUN=$(ls -td experiments_self_reflective/aime_train/joint_* | head -n1)
python -m concept_mem.data.aime_self_reflection \
  data=aime_train \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  +joint_responses_file="$JOINT_RUN/joint_responses.json" \
  hydra.run.dir="$REFLECT_RUN"
```

**Outputs**: 
- `thought_processes.json` - Refined reasoning narratives (no correctness labels)

---

## Stage 3: Lesson Abstraction (Training - 120 problems)

Extract generalizable lessons from self-reflections.

```bash
ABSTRACT_RUN="experiments_self_reflective/aime_train/abstraction_$(date +"%Y%m%d-%H%M%S")"
JOINT_RUN=$(ls -td experiments_self_reflective/aime_train/joint_* | head -n1)
REFLECT_RUN=$(ls -td experiments_self_reflective/aime_train/self_reflect_* | head -n1)
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_uncertain \
  abstraction.problem_solutions="$JOINT_RUN/solutions.json" \
  abstraction.thought_processes="$REFLECT_RUN/thought_processes.json" \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  hydra.run.dir="$ABSTRACT_RUN"
```

**Outputs**: 
- `lessons.json` - Extracted lessons from uncertain reasoning

---

## Stage 4: Lesson Retrieval (Validation - 60 problems)

Select relevant lessons for each validation problem.

```bash
SELECTION_RUN="experiments_self_reflective/aime_val/selection_$(date +"%Y%m%d-%H%M%S")"
ABSTRACT_RUN=$(ls -td experiments_self_reflective/aime_train/abstraction_* | head -n1)
python -m concept_mem.selection.description.select \
  selection=aime \
  selection.lesson_file="$ABSTRACT_RUN/lessons.json" \
  model@selection.model=gemini_2_5_flash_lite_thinking \
  generation@selection.generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  selection.generation.ignore_cache=true \
  selection.generation.max_tokens=16384 \
  selection.generation.seed=null \
  hydra.run.dir="$SELECTION_RUN"
```
```bash
SELECTION_RUN="experiments_self_reflective/aime_val/selection_$(date +"%Y%m%d-%H%M%S")"
ABSTRACT_RUN=$(ls -td experiments_self_reflective/aime_train/abstraction_* | head -n1)
python -m concept_mem.selection.description.select \
  selection=aime \
  selection.lesson_file="$ABSTRACT_RUN/lessons.json" \
  model@selection.model=gemini_2_5_flash_lite_thinking \
  selection.generation.max_tokens=32000 \
  +selection.generation.extra_kwargs.extra_body.reasoning.max_tokens=8000 \
  selection.generation.ignore_cache=true \
  selection.generation.seed=null \
  hydra.run.dir="$SELECTION_RUN"
```


**Outputs**: 
- `prompt_info.json` - Retrieved lessons for each validation problem

---

## Stage 5: Validation Solve with Memory (Top 2 Lessons)

Solve validation problems with retrieved lessons.

```bash
WITH_MEMORY_RUN="experiments_self_reflective/aime_val/with_memory_top2_$(date +"%Y%m%d-%H%M%S")"
SELECTION_RUN=$(ls -td experiments_self_reflective/aime_val/selection_* | head -n1)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_RUN/prompt_info.json" \
  prompt.hint_lessons_limit=2 \
  generation.ignore_cache=true \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="$WITH_MEMORY_RUN"
```

**Note**: `prompt.hint_lessons_limit=2` uses only top 2 most relevant lessons + self-assessment prompt.

---

## Baseline Reference (No Memory)

```bash
BASELINE_RUN="experiments_self_reflective/aime_val/baseline_$(date +"%Y%m%d-%H%M%S")"
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

## Results Comparison

```bash
echo "=== Baseline (No Memory) ==="
grep "pass@1:" "$BASELINE_RUN/aime_simple_solver_v3.log" | tail -1

echo ""
echo "=== With Self-Reflective Memory (Top 2) ==="
grep "pass@1:" "$WITH_MEMORY_RUN/aime_simple_solver_v3.log" | tail -1
```

---

## Analysis & Reports

Generate comprehensive evaluation reports and cost analysis:

```bash
# Set up analysis directory
ANALYSIS_DIR="experiments_self_reflective/aime_val/analysis"
mkdir -p "$ANALYSIS_DIR"

# 1. Evaluate baseline
BASELINE_RUN=$(ls -td experiments_self_reflective/aime_val/baseline_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $BASELINE_RUN)/solutions.json" \
  --dataset="data/aime/validation.json" \
  --output="$(realpath --relative-to=. $BASELINE_RUN)/evaluation_results.json"

# 2. Evaluate with memory
WITH_MEMORY_RUN=$(ls -td experiments_self_reflective/aime_val/with_memory_top2_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $WITH_MEMORY_RUN)/solutions.json" \
  --dataset="data/aime/validation.json" \
  --output="$(realpath --relative-to=. $WITH_MEMORY_RUN)/evaluation_results.json"

# 3. Cost analysis (training pipeline)
python ../arc_memo_rebuttal/aime_analysis/analyze_costs.py \
  --experiments-dir="experiments_self_reflective/aime_train" \
  > "$ANALYSIS_DIR/cost_analysis_train.txt"

# 4. Cost analysis (validation pipeline)
python ../arc_memo_rebuttal/aime_analysis/analyze_costs.py \
  --experiments-dir="experiments_self_reflective/aime_val" \
  > "$ANALYSIS_DIR/cost_analysis_val.txt"

echo ""
echo "=== Analysis Complete ==="
echo "Baseline evaluation: $BASELINE_RUN/evaluation_results.json"
echo "With memory evaluation: $WITH_MEMORY_RUN/evaluation_results.json"
echo "Training costs: $ANALYSIS_DIR/cost_analysis_train.txt"
echo "Validation costs: $ANALYSIS_DIR/cost_analysis_val.txt"
```

---

## Detailed Results Summary

```bash
echo "=== SELF-REFLECTIVE PIPELINE RESULTS ==="
echo ""

BASELINE_RUN=$(ls -td experiments_self_reflective/aime_val/baseline_* | head -n1)
WITH_MEMORY_RUN=$(ls -td experiments_self_reflective/aime_val/with_memory_top2_* | head -n1)

echo "--- Baseline (No Memory) ---"
if [ -f "$BASELINE_RUN/evaluation_results.json" ]; then
  cat "$BASELINE_RUN/evaluation_results.json" | python -c "
import sys, json
d = json.load(sys.stdin)
print(f'Accuracy: {d[\"accuracy\"]:.2%} ({d[\"correct\"]}/{d[\"total\"]})')
print(f'Errors: {len(d[\"errors\"])}')
"
fi

echo ""
echo "--- With Self-Reflective Memory (Top 2 Lessons) ---"
if [ -f "$WITH_MEMORY_RUN/evaluation_results.json" ]; then
  cat "$WITH_MEMORY_RUN/evaluation_results.json" | python -c "
import sys, json
d = json.load(sys.stdin)
print(f'Accuracy: {d[\"accuracy\"]:.2%} ({d[\"correct\"]}/{d[\"total\"]})')
print(f'Errors: {len(d[\"errors\"])}')
"
fi

echo ""
echo "--- Comparison ---"
python3 << 'EOF'
import json
from pathlib import Path

baseline = Path("$BASELINE_RUN/evaluation_results.json")
with_mem = Path("$WITH_MEMORY_RUN/evaluation_results.json")

if baseline.exists() and with_mem.exists():
    b_data = json.loads(baseline.read_text())
    m_data = json.loads(with_mem.read_text())
    
    b_correct = b_data["correct"]
    m_correct = m_data["correct"]
    total = b_data["total"]
    
    improvement = m_correct - b_correct
    print(f"Improvement: {improvement:+d} problems")
    print(f"Delta: {improvement/total:+.1%}")
    
    # Find flips
    b_wrong = {e["id"] for e in b_data["errors"]}
    m_wrong = {e["id"] for e in m_data["errors"]}
    
    fixed = b_wrong - m_wrong
    broken = m_wrong - b_wrong
    
    print(f"\nFixed by memory: {len(fixed)} problems")
    if fixed:
        print(f"  {sorted(fixed)[:5]}")
    
    print(f"\nBroken by memory: {len(broken)} problems")
    if broken:
        print(f"  {sorted(broken)[:5]}")
EOF
```

---

## Key Features

- ✅ **No label dependency**: Learns from model's own reasoning
- ✅ **Self-improvement**: Model critiques and refines its thought process
- ✅ **Top 2 lessons**: Reduces noise, keeps most relevant guidance
- ✅ **Self-assessment**: Model can ignore lessons if problem is straightforward
- ✅ **Scalable**: Can work on problems without ground truth

---

## Debug Version

See `RUN_AIME_SELF_REFLECTIVE_DEBUG.md` for single-problem testing.

