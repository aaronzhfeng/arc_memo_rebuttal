# AIME Label-Guided Pipeline - DEBUG (Single Problem)

**Purpose**: Test the label-guided pipeline on a single problem to inspect prompts, lessons, and outputs in detail.

**Training Problem**: `2020-I-1` (geometry, assume correct solve)  
**Validation Problem**: `2024_I_10` (geometry, matching domain)

**Output Directory**: `experiments_label_guided/debug/`

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

## Stage 0: Baseline (1 validation problem, no memory)

```bash
BASELINE_RUN="experiments_label_guided/debug/baseline_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.n=3 \
  generation.expand_multi=true \
  generation.seed=null \
  hydra.run.dir="$BASELINE_RUN"
```

**Verify**: 
```bash
cat "$BASELINE_RUN/solutions.json"
echo "Expected: 113"
```

---

## Stage 1: Solve Training Set (1 problem)

```bash
SOLVE_RUN="experiments_label_guided/debug/solve_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_train_debug \
  model=o4_mini \
  generation=o4_solve \
  generation.ignore_cache=true \
  generation.seed=null \
  hydra.run.dir="$SOLVE_RUN"
```

**Verify**: 
```bash
echo "=== Solution ==="
cat "$SOLVE_RUN/solutions.json"
echo ""
echo "Expected: 2020-I-1 should be 803"
```

---

## Stage 2: Generate Thought Process (1 problem)

```bash
REASON_RUN="experiments_label_guided/debug/reasoning_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="$SOLVE_RUN/solutions.json" \
  data=aime_train_debug \
  model=o4_mini \
  generation.max_tokens=8192 \
  generation.seed=null \
  hydra.run.dir="$REASON_RUN"
```

**Verify**: 
```bash
cat "$REASON_RUN/thought_processes.json" | python -m json.tool | head -50
```

---

## Stage 3: Lesson Abstraction + Filter (1 problem → N lessons)

```bash
ABSTRACT_RUN="experiments_label_guided/debug/abstraction_$(date +"%Y%m%d-%H%M%S")"
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_strict \
  abstraction.problem_solutions="$SOLVE_RUN/solutions.json" \
  abstraction.thought_processes="$REASON_RUN/thought_processes.json" \
  model=gpt41 \
  generation.seed=null \
  hydra.run.dir="$ABSTRACT_RUN"

# Filter to keep only lessons from correctly solved problems
python ../arc_memo_rebuttal/aime_analysis/filter_correct_lessons.py \
  --solutions="$SOLVE_RUN/solutions.json" \
  --lessons-in="$ABSTRACT_RUN/lessons.json" \
  --lessons-out="$ABSTRACT_RUN/lessons_correct.json"
```

**Verify**: 
```bash
echo "=== All Extracted Lessons ==="
cat "$ABSTRACT_RUN/lessons.json" | python -m json.tool

echo ""
echo "=== Correct-Only Lessons (filtered) ==="
cat "$ABSTRACT_RUN/lessons_correct.json" | python -m json.tool
```

---

## Stage 4: Lesson Retrieval (1 validation problem)

```bash
SELECTION_RUN="experiments_label_guided/debug/selection_$(date +"%Y%m%d-%H%M%S")"
ABSTRACT_RUN=$(ls -td experiments_label_guided/debug/abstraction_* | head -n1)
python -m concept_mem.selection.description.select \
  selection=aime \
  data=aime_val_debug \
  model=gpt41 \
  selection.lesson_file="$ABSTRACT_RUN/lessons_correct.json" \
  selection.description_file=data/aime/validation_debug.json \
  selection.problems=data/aime/validation_ids_debug.json \
  selection.generation.ignore_cache=true \
  selection.generation.max_tokens=8192 \
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

## Stage 5: Validation Solve WITH Memory (Top 2 Lessons)

```bash
WITH_MEMORY_RUN="experiments_label_guided/debug/with_memory_top2_$(date +"%Y%m%d-%H%M%S")"
SELECTION_RUN=$(ls -td experiments_label_guided/debug/selection_* | head -n1)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val_debug \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  prompt.problem_data="$SELECTION_RUN/prompt_info.json" \
  prompt.hint_lessons_limit=2 \
  generation.ignore_cache=true \
  generation.n=3 \
  generation.expand_multi=true \
  generation.seed=null \
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
echo "=== Baseline Answer (No Memory) ==="
cat "$BASELINE_RUN/solutions.json"

echo ""
echo "=== With Label-Guided Memory Answer (Top 2) ==="
cat "$WITH_MEMORY_RUN/solutions.json"

echo ""
echo "=== Ground Truth ==="
echo "2024_I_10 should be: 113"
```

---

## Prompt Inspection Helper

```bash
# Extract and view the exact lesson text that was provided
SELECTION_RUN=$(ls -td experiments_label_guided/debug/selection_* | head -n1)
python3 << 'EOF'
import json
with open(f'{SELECTION_RUN}/prompt_info.json') as f:
    data = json.load(f)
problem_id = list(data.keys())[0]
hint = data[problem_id].get('aime_lessons', {}).get('hint', '')
print("=== Lesson Text Provided to Model (Top 2) ===")
print(hint)
EOF
```

---

## Key Inspection Points

1. **Training Problem Correctness**: Verify the training problem was solved correctly
2. **Lesson Quality**: Check if extracted lessons are specific and actionable
3. **Filter Effect**: Compare `lessons.json` vs `lessons_correct.json` - what was filtered out?
4. **Retrieval Relevance**: Are the top 2 correct-only lessons actually relevant?
5. **Prompt Format**: Does the self-assessment + top 2 lessons look good?
6. **Model Behavior**: Did the model use or ignore the lessons?
7. **Answer Quality**: Did label-guided memory help or hurt?

---

## Debugging Workflow

### If Training Problem Was Solved Incorrectly:
```bash
# Check if the problem was filtered out
ABSTRACT_RUN=$(ls -td experiments_label_guided/debug/abstraction_* | head -n1)
echo "=== Lessons from incorrect solution (should be empty) ==="
cat "$ABSTRACT_RUN/lessons_correct.json"
```

### If Retrieval Failed:
```bash
# Check retrieval logs
SELECTION_RUN=$(ls -td experiments_label_guided/debug/selection_* | head -n1)
tail -50 "$SELECTION_RUN/select.log"
```

### If Memory Hurt Performance:
```bash
# Compare the prompts side-by-side
echo "=== BASELINE PROMPT ==="
cat "$BASELINE_RUN/prompts.json" | python -m json.tool

echo ""
echo "=== WITH MEMORY PROMPT ==="
cat "$WITH_MEMORY_RUN/prompts.json" | python -m json.tool
```

---

## Tuning Opportunities

1. **Lesson Formatting**: Adjust `situation:`/`suggestion:` structure in abstraction prompt
2. **Retrieval Prompt**: Modify how the model selects relevant lessons
3. **Self-Assessment Phrasing**: Experiment with different wordings
4. **Top K**: Try k=1, 2, or 3 to find sweet spot
5. **Lesson Length**: Truncate overly verbose lessons

---

## Analysis & Reports (Automatic)

Generate evaluation reports and analysis in the debug folder:

```bash
# Set up analysis directory
ANALYSIS_DIR="experiments_label_guided/debug/analysis"
mkdir -p "$ANALYSIS_DIR"

# 1. Evaluate training solve
SOLVE_RUN=$(ls -td experiments_label_guided/debug/solve_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $SOLVE_RUN)/solutions.json" \
  --dataset="data/aime/train_debug.json" \
  --output="$(realpath --relative-to=. $SOLVE_RUN)/evaluation_results.json"

# 2. Evaluate baseline
BASELINE_RUN=$(ls -td experiments_label_guided/debug/baseline_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $BASELINE_RUN)/solutions.json" \
  --dataset="data/aime/validation_debug.json" \
  --output="$(realpath --relative-to=. $BASELINE_RUN)/evaluation_results.json"

# 3. Evaluate with memory
WITH_MEMORY_RUN=$(ls -td experiments_label_guided/debug/with_memory_top2_* | head -n1)
python ../arc_memo_rebuttal/aime_analysis/evaluate_aime.py \
  --solutions="$(realpath --relative-to=. $WITH_MEMORY_RUN)/solutions.json" \
  --dataset="data/aime/validation_debug.json" \
  --output="$(realpath --relative-to=. $WITH_MEMORY_RUN)/evaluation_results.json"

# 4. Cost analysis (all debug runs)
python ../arc_memo_rebuttal/aime_analysis/analyze_costs.py \
  --experiments-dir="experiments_label_guided/debug" \
  > "$ANALYSIS_DIR/cost_analysis.txt"

echo ""
echo "=== Analysis Complete ==="
echo "Training evaluation: $SOLVE_RUN/evaluation_results.json"
echo "Baseline evaluation: $BASELINE_RUN/evaluation_results.json"
echo "With memory evaluation: $WITH_MEMORY_RUN/evaluation_results.json"
echo "Cost analysis: $ANALYSIS_DIR/cost_analysis.txt"
```

---

## Quick Results Summary

```bash
echo "=== LABEL-GUIDED DEBUG SUMMARY ==="
echo ""
echo "Training Problem: 2020-I-1 (expected: 803)"
echo "Validation Problem: 2024_I_10 (expected: 113)"
echo ""

SOLVE_RUN=$(ls -td experiments_label_guided/debug/solve_* | head -n1)
BASELINE_RUN=$(ls -td experiments_label_guided/debug/baseline_* | head -n1)
WITH_MEMORY_RUN=$(ls -td experiments_label_guided/debug/with_memory_top2_* | head -n1)

echo "--- Training Solve (o4-mini, n=3) ---"
cat "$SOLVE_RUN/solutions.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Answer: {list(d.values())[0]}')"
if [ -f "$SOLVE_RUN/evaluation_results.json" ]; then
  cat "$SOLVE_RUN/evaluation_results.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Correct: {d[\"correct\"]}/{d[\"total\"]}')"
fi

echo ""
echo "--- Baseline (No Memory) ---"
cat "$BASELINE_RUN/solutions.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Answer: {list(d.values())[0]}')"
if [ -f "$BASELINE_RUN/evaluation_results.json" ]; then
  cat "$BASELINE_RUN/evaluation_results.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Correct: {d[\"correct\"]}/{d[\"total\"]}')"
fi

echo ""
echo "--- With Memory (Top 2 Correct-Only Lessons) ---"
cat "$WITH_MEMORY_RUN/solutions.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Answer: {list(d.values())[0]}')"
if [ -f "$WITH_MEMORY_RUN/evaluation_results.json" ]; then
  cat "$WITH_MEMORY_RUN/evaluation_results.json" | python -c "import sys, json; d=json.load(sys.stdin); print(f'Correct: {d[\"correct\"]}/{d[\"total\"]}')"
fi

echo ""
echo "--- Retrieved Lessons ---"
SELECTION_RUN=$(ls -td experiments_label_guided/debug/selection_* | head -n1)
echo "Top lessons used:"
cat "$SELECTION_RUN/retrieved_concept_uids.json" | python -m json.tool

echo ""
echo "--- Filter Effect ---"
ABSTRACT_RUN=$(ls -td experiments_label_guided/debug/abstraction_* | head -n1)
echo "All lessons count:"
cat "$ABSTRACT_RUN/lessons.json" | python -c "import sys, json; d=json.load(sys.stdin); print(sum(len(v) for v in d.values()))"
echo "Correct-only lessons count:"
cat "$ABSTRACT_RUN/lessons_correct.json" | python -c "import sys, json; d=json.load(sys.stdin); print(sum(len(v) for v in d.values()))"
```

---

## Expected Debug Output Structure

```
experiments_label_guided/debug/
├── solve_TIMESTAMP/
│   ├── solutions.json            # "2020-I-1": "803"
│   ├── evaluation_results.json   # Training accuracy
│   ├── token_usage.json
│   └── full_responses.json
├── reasoning_TIMESTAMP/
│   ├── thought_processes.json    # Detailed reasoning
│   └── token_usage.json
├── abstraction_TIMESTAMP/
│   ├── lessons.json              # All lessons (before filter)
│   ├── lessons_correct.json      # Only from correct solves
│   ├── prompts.json
│   └── token_usage.json
├── selection_TIMESTAMP/
│   ├── retrieved_concept_uids.json  # Top K lesson IDs
│   ├── prompt_info.json             # Formatted lessons
│   └── token_usage.json
├── baseline_TIMESTAMP/
│   ├── solutions.json            # Answer without memory
│   ├── evaluation_results.json   # Validation accuracy
│   └── token_usage.json
├── with_memory_top2_TIMESTAMP/
│   ├── solutions.json            # Answer with top 2 lessons
│   ├── evaluation_results.json   # Validation accuracy (with memory)
│   ├── prompts.json              # Full prompt sent to model
│   ├── full_responses.json       # Model's full response
│   └── token_usage.json
└── analysis/
    └── cost_analysis.txt         # Aggregated cost report
```

