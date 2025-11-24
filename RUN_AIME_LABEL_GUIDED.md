# AIME Pipeline: Label-Guided Learning

**Approach**: Extract lessons only from correctly solved problems, using ground truth labels to filter.

**Philosophy**: The model learns from verified correct solutions, ensuring lesson quality through label-guided filtering.

**Output Directory**: `experiments_label_guided/`

---

## Setup

```bash
cd arc_memo
source .venv/bin/activate
export OPENAI_API_KEY="sk-your-openai-key"
export OPENROUTER_API_KEY="sk-or-your-openrouter-key"
```

---

## Stage 0: Baseline (No Memory)

Establish baseline performance without any lessons.

```bash
BASELINE_RUN="experiments_label_guided/aime_val/baseline_$(date +"%Y%m%d-%H%M%S")"
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

## Stage 1: Solve Training Set (o4-mini, n=3, pass@2)

Generate solutions with multiple attempts to maximize correct solves.

```bash
SOLVE_RUN="experiments_label_guided/aime_train/solve_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_train \
  model=o4_mini \
  generation=o4_solve \
  generation.ignore_cache=true \
  hydra.run.dir="$SOLVE_RUN"
```

**Outputs**: 
- `solutions.json` - Extracted answers (will be used to filter correct problems)

---

## Stage 2: Generate Thought Processes (o4-mini)

Create detailed reasoning traces for all training problems.

```bash
REASON_RUN="experiments_label_guided/aime_train/reasoning_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="$SOLVE_RUN/solutions.json" \
  data=aime_train \
  model=o4_mini \
  generation.max_tokens=8192 \
  hydra.run.dir="$REASON_RUN"
```

**Outputs**: 
- `thought_processes.json` - Reasoning traces for all problems

---

## Stage 3: Lesson Abstraction (gpt-4.1)

Extract lessons from all problems, then filter to keep only correct ones.

```bash
ABSTRACT_RUN="experiments_label_guided/aime_train/abstraction_$(date +"%Y%m%d-%H%M%S")"
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

**Outputs**: 
- `lessons.json` - All extracted lessons
- `lessons_correct.json` - **Filtered lessons from correct solutions only**

---

## Stage 4: Lesson Retrieval (GPT-4.1, Validation)

Select relevant correct-only lessons for each validation problem.

```bash
SELECTION_RUN="experiments_label_guided/aime_val/selection_$(date +"%Y%m%d-%H%M%S")"
ABSTRACT_RUN=$(ls -td experiments_label_guided/aime_train/abstraction_* | head -n1)
python -m concept_mem.selection.description.select \
  selection=aime \
  data=aime_val \
  model=gpt41 \
  selection.problems=data/aime/validation_ids.json \
  selection.lesson_file="$ABSTRACT_RUN/lessons_correct.json" \
  selection.description_file=data/aime/validation.json \
  generation.ignore_cache=true \
  selection.generation.ignore_cache=true \
  selection.generation.max_tokens=16384 \
  selection.generation.seed=null \
  hydra.run.dir="$SELECTION_RUN"
```

**Outputs**: 
- `prompt_info.json` - Retrieved correct-only lessons for validation

---

## Stage 5: Validation Solve with Memory (Top 2 Lessons)

Solve validation problems with top 2 retrieved correct-only lessons.

```bash
WITH_MEMORY_RUN="experiments_label_guided/aime_val/with_memory_top2_$(date +"%Y%m%d-%H%M%S")"
SELECTION_RUN=$(ls -td experiments_label_guided/aime_val/selection_* | head -n1)
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

## Results Comparison

```bash
echo "=== Baseline (No Memory) ==="
grep "pass@1:" "$BASELINE_RUN/aime_simple_solver_v3.log" | tail -1

echo ""
echo "=== With Label-Guided Memory (Top 2) ==="
grep "pass@1:" "$WITH_MEMORY_RUN/aime_simple_solver_v3.log" | tail -1
```

---

## Analysis & Reports

Generate comprehensive evaluation reports, cost analysis, and reflective usage analysis:

```bash
# Set up analysis directory
ANALYSIS_DIR="experiments_label_guided/aime_val/analysis"
mkdir -p "$ANALYSIS_DIR"

# 1. Evaluate training solve
SOLVE_RUN=$(ls -td experiments_label_guided/aime_train/solve_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $SOLVE_RUN)/solutions.json" \
  --dataset="data/aime/train.json" \
  --output="$(realpath --relative-to=. $SOLVE_RUN)/evaluation_results.json"

# 2. Evaluate baseline
BASELINE_RUN=$(ls -td experiments_label_guided/aime_val/baseline_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $BASELINE_RUN)/solutions.json" \
  --dataset="data/aime/validation.json" \
  --output="$(realpath --relative-to=. $BASELINE_RUN)/evaluation_results.json"

# 3. Evaluate with memory
WITH_MEMORY_RUN=$(ls -td experiments_label_guided/aime_val/with_memory_top2_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $WITH_MEMORY_RUN)/solutions.json" \
  --dataset="data/aime/validation.json" \
  --output="$(realpath --relative-to=. $WITH_MEMORY_RUN)/evaluation_results.json"

# 4. Reflective usage analysis (which training problems had wrong→correct lessons)
# Note: In label-guided, "reflective" means lessons from initially incorrect problems
#       that were corrected by multi-attempt solving (n=3, pass@2)
SELECTION_RUN=$(ls -td experiments_label_guided/aime_val/selection_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/reflective_usage_analysis.py \
  --train-solutions="$(realpath --relative-to=. $SOLVE_RUN)/solutions.json" \
  --retrieved-concepts="$(realpath --relative-to=. $SELECTION_RUN)/retrieved_concept_uids.json" \
  --baseline-solutions="$(realpath --relative-to=. $BASELINE_RUN)/solutions.json" \
  --with-memory-solutions="$(realpath --relative-to=. $WITH_MEMORY_RUN)/solutions.json" \
  --output-dir="$ANALYSIS_DIR"

# 5. Cost analysis (training pipeline)
python ../arc_memo_rebuttal/aime_analysis/analyze_costs.py \
  --experiments-dir="experiments_label_guided/aime_train" \
  > "$ANALYSIS_DIR/cost_analysis_train.txt"

# 6. Cost analysis (validation pipeline)
python ../arc_memo_rebuttal/aime_analysis/analyze_costs.py \
  --experiments-dir="experiments_label_guided/aime_val" \
  > "$ANALYSIS_DIR/cost_analysis_val.txt"

echo ""
echo "=== Analysis Complete ==="
echo "Training solve evaluation: $SOLVE_RUN/evaluation_results.json"
echo "Baseline evaluation: $BASELINE_RUN/evaluation_results.json"
echo "With memory evaluation: $WITH_MEMORY_RUN/evaluation_results.json"
echo "Reflective usage analysis: $ANALYSIS_DIR/"
echo "Training costs: $ANALYSIS_DIR/cost_analysis_train.txt"
echo "Validation costs: $ANALYSIS_DIR/cost_analysis_val.txt"
```

---

## Detailed Results Summary

```bash
echo "=== LABEL-GUIDED PIPELINE RESULTS ==="
echo ""

SOLVE_RUN=$(ls -td experiments_label_guided/aime_train/solve_* | head -n1)
BASELINE_RUN=$(ls -td experiments_label_guided/aime_val/baseline_* | head -n1)
WITH_MEMORY_RUN=$(ls -td experiments_label_guided/aime_val/with_memory_top2_* | head -n1)
ANALYSIS_DIR="experiments_label_guided/aime_val/analysis"

echo "--- Training Solve (o4-mini, n=3, pass@2) ---"
if [ -f "$SOLVE_RUN/evaluation_results.json" ]; then
  cat "$SOLVE_RUN/evaluation_results.json" | python -c "
import sys, json
d = json.load(sys.stdin)
print(f'Accuracy: {d[\"accuracy\"]:.2%} ({d[\"correct\"]}/{d[\"total\"]})')
print(f'Problems for lesson extraction: {d[\"correct\"]}')
"
fi

echo ""
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
echo "--- With Label-Guided Memory (Top 2 Correct-Only Lessons) ---"
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

echo ""
echo "--- Reflective Usage Summary ---"
if [ -f "$ANALYSIS_DIR/summary.json" ]; then
  cat "$ANALYSIS_DIR/summary.json" | python -c "
import sys, json
d = json.load(sys.stdin)
print(f'Validation problems with retrieval: {d[\"problems_with_reflective_retrieval\"]}')
print(f'Problems where retrieval helped: {d[\"problems_with_reflective_and_correct\"]}')
print(f'Problems flipped (wrong→correct): {d[\"problems_with_reflective_flip\"]}')
"
fi
```

---

## Key Features

- ✅ **Quality-filtered lessons**: Only from correctly solved problems
- ✅ **Multiple solve attempts**: n=3 with pass@2 to maximize correct solves
- ✅ **Top 2 lessons**: Reduces noise, keeps most relevant guidance
- ✅ **Self-assessment**: Model can ignore lessons if problem is straightforward
- ✅ **Verified correctness**: Every lesson comes from a verified correct solution

---

## Debug Version

See `RUN_AIME_LABEL_GUIDED_DEBUG.md` for single-problem testing and prompt inspection.

