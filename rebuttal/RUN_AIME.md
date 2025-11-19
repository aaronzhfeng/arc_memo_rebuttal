# AIME Experiment Commands

Domain generalization to mathematical reasoning.

Run from `arc_memo/` directory.

---

## Setup (One-time)

**Requirements:** Python 3.10+ (check: `python3 --version`)

```bash
# Create virtual environment (first time only)
cd arc_memo
python3 -m venv .venv  # Use python3.10, python3.11, or python3.12 if needed

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install datasets pandas  # Additional for AIME

# Download AIME dataset
cd data/aime
python download_and_prepare.py  # Creates train, val, test splits + ID files
cd ../..

# Create .env file with API keys
cat > .env << 'EOF'
OPENAI_API_KEY=sk-...your-key...
OPENROUTER_API_KEY=sk-or-...your-key...
EOF
```

**Remember to activate venv before running experiments:**
```bash
cd arc_memo
source .venv/bin/activate
```

---

## Full Pipeline

```bash
bash experiments/aime_pilot.sh
```

---

## Quick Test (10 problems from 2019-II)

Test the pipeline on small subset before full run.

**Note:** Using `aime_simple_solver_v3` with ultra-strict output format (integer only).

```bash
# Test split already created by download_and_prepare.py

# 1a. o4 solves test set (v3 = ultra-strict format, outputs only integer)
# IMPORTANT: expand_multi=true forces 3 separate calls (o4-mini doesn't support n>1)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_test \
  model=o4_mini \
  generation.ignore_cache=true \
  generation.max_tokens=8192 \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="experiments/aime_test_v3/o4_solve"

# 1b. Generate thought processes (o4 explains how it solved each problem)
# This creates reasoning text for GPT-4.1 to abstract from
python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="experiments/aime_test_v3/o4_solve/solutions.json" \
  data=aime_test \
  model=o4_mini \
  generation.max_tokens=8192 \
  hydra.run.dir="experiments/aime_test_v3/o4_reasoning"

# 2. Check solutions
cat experiments/aime_test_v3/o4_solve/solutions.json | jq '[.[] | select(. != "")] | length'

# 3. gpt41 abstracts concepts (uses thought processes)
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_strict \
  abstraction.problem_solutions="experiments/aime_test_v3/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_test_v3/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_test_v3/abstraction"

# 4. Check abstraction results
python -c "import json; d=json.load(open('experiments/aime_test_v3/abstraction/lessons.json')); print(f'Extracted {len(d)} concept sets'); print('Sample:', list(d.items())[0])"
```

**Purpose:** Verify pipeline works before running on 120 training problems.

**Key Changes (v3):**
- Uses `aime_simple_solver_v3` (ultra-strict format: integer only)
- `max_tokens=4096` for solving (hard problems need >2000 reasoning tokens)
- `max_tokens=2048` for thought_process (generates reasoning explanation)
- Model outputs ONLY the integer in step 1a (e.g., `237` not `Final Answer: 237`)
- All 10/10 test problems solved with clean format ✓
- Per-request token tracking enabled (see `token_usage.json`)
- Output dir: `experiments/aime_test_v3/` (v3 suffix)

---

## Prompt Comparison (A/B Test)

Compare original vs strict AIME abstraction prompts on the same data.

```bash
# Run both abstraction versions on test set

# Version 1: Original AIME prompt (simpler)
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace \
  abstraction.problem_solutions="experiments/aime_test_v3/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_test_v3/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_test_v3/abstraction_original"

# Version 2: Strict AIME prompt (with 6 explicit constraints)
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_strict \
  abstraction.problem_solutions="experiments/aime_test_v3/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_test_v3/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_test_v3/abstraction_strict"

# Compare results
echo "=== Original Prompt ==="
python -c "import json; d=json.load(open('experiments/aime_test_v3/abstraction_original/lessons.json')); print(f'Concepts: {len(d)}'); print('Sample:', list(d.items())[0][1][:2])"

echo ""
echo "=== Strict Prompt ==="
python -c "import json; d=json.load(open('experiments/aime_test_v3/abstraction_strict/lessons.json')); print(f'Concepts: {len(d)}'); print('Sample:', list(d.items())[0][1][:2])"
```

**Compare:**
- Generalization quality (are lessons problem-specific or general?)
- Concreteness (are suggestions actionable?)
- Encoding of key steps (does at least one lesson capture the main insight?)

**Pick the better version for full training run.**

---


## Step-by-Step (Full Experiment)

**All commands use v3 solver with ultra-strict format.**

```bash
# 1a. o4 solves training (120 problems, outputs integer only)
# expand_multi=true forces 3 separate calls (o4-mini doesn't support n>1)
# max_tokens=4096 needed (hard problems use >2000 reasoning tokens)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_train \
  model=o4_mini \
  generation.ignore_cache=true \
  generation.max_tokens=8192 \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="experiments/aime_train/o4_solve"

# 1b. Generate thought processes (o4 explains reasoning)
python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="experiments/aime_train/o4_solve/solutions.json" \
  data=aime_train \
  model=o4_mini \
  generation.max_tokens=8192 \
  hydra.run.dir="experiments/aime_train/o4_reasoning"

# 2. gpt41 abstracts concepts (uses thought processes)
# Use aime_lesson_from_trace_strict for better quality (based on A/B test)
python -m concept_mem.abstraction.analysis_concepts \
  +abstraction=aime_lesson_from_trace_strict \
  abstraction.problem_solutions="experiments/aime_train/o4_solve/solutions.json" \
  abstraction.thought_processes="experiments/aime_train/o4_reasoning/thought_processes.json" \
  model=gpt41 \
  hydra.run.dir="experiments/aime_train/abstraction"

# 3a. GPT 4.1 Mini baseline solves validation (2024-2025, 60 problems)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gpt41_mini \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="experiments/aime_val/baseline"

# 3b. Baseline thought processes (for fair comparison)
python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="experiments/aime_val/baseline/solutions.json" \
  data=aime_val \
  model=gpt41_mini \
  generation.max_tokens=2048 \
  hydra.run.dir="experiments/aime_val/baseline_reasoning"

# 3c. Gemini 2.5 Flash Lite (Thinking) baseline (no retrieval)
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gemini_2_5_flash_lite_thinking \
  generation=gemini_thinking_16k \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="experiments/aime_val/gemini_baseline"

# 4. Select concepts for validation set (reuses ArcMemo code)
python -m concept_mem.selection.description.select \
  selection=aime \
  selection.lesson_file="experiments/aime_train/abstraction/lessons.json" \
  model@selection.model=gpt41 \
  hydra.run.dir="experiments/aime_val/selection"

# Output includes `prompt_info.json`, which the solver consumes as retrieval hints.

# 5a. GPT 4.1 Mini solves with memory
python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_val \
  model=gpt41_mini \
  prompt.problem_data="experiments/aime_val/selection/prompt_info.json" \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  generation.n=3 \
  hydra.run.dir="experiments/aime_val/with_memory"

# 5b. With-memory thought processes (for analysis)
python -m concept_mem.data.aime_thought_process \
  +abstraction=aime_thought_process \
  abstraction.solutions_file="experiments/aime_val/with_memory/solutions.json" \
  data=aime_val \
  model=gpt41_mini \
  generation.max_tokens=2048 \
  hydra.run.dir="experiments/aime_val/with_memory_reasoning"

The solver automatically appends the retrieved lessons and descriptions from `prompt_info.json` to every problem prompt.

# 5c. Gemini 2.5 Flash Lite (Thinking) with ArcMemo retrieval
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

---

## Evaluate

```bash
cd data/aime

# Evaluate baseline
python evaluate_results.py ../../experiments/aime_val/baseline/solutions.json

# Evaluate with memory
python evaluate_results.py ../../experiments/aime_val/with_memory/solutions.json

# Compare (show both)
echo "=== Baseline ==="
python evaluate_results.py ../../experiments/aime_val/baseline/solutions.json
echo ""
echo "=== With Memory ==="
python evaluate_results.py ../../experiments/aime_val/with_memory/solutions.json
```

---

## Expected

Baseline: ~49% → With memory: ~55% (+6%)

---

## Important Notes

### v3 Solver (Recommended)
- **Always use `aime_simple_solver_v3`** (ultra-strict format)
- Model outputs ONLY the integer (e.g., `237` not `Final Answer: 237`)
- `max_tokens=4096` (hard problems need >2000 reasoning tokens)
- Much more robust than v1/v2 (no fragile parsing)
- Saves `full_responses.json` with complete reasoning traces
- **Tested: 10/10 success rate** on 2019-II problems ✓

### Why v3?
- **v1:** Had empty response issues (6/10 failures)
- **v2:** Fixed empty responses but fragile "Final Answer: X" format
- **v3:** Ultra-strict format with explicit examples → much more robust

See `docs/12_aime_solver_v3_improvements.md` for details.

### Output Files (v3)
- `solutions.json` - Extracted numerical answers
- `full_responses.json` - Complete reasoning traces (includes internal reasoning)
- `extraction_failures.json` - Any failed extractions (if any)
- `model_outputs.json` - Raw API responses
- `token_usage.json` - Now includes per-request breakdown with reasoning tokens ✨

---

## References

- **Implementation:** `docs/06_aime_implementation.md`
- **v3 solver (current):** `docs/12_aime_solver_v3_improvements.md`
- **v2 solver fix:** `docs/08_aime_empty_response_fix.md`
- **o4-mini n>1 fix:** `docs/10_aime_o4mini_expand_multi_fix.md`
- **Pipeline details:** `docs/07_aime_pipeline_corrected.md`
