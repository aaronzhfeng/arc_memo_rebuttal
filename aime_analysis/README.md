# AIME Analysis Tools

This directory contains analysis scripts for evaluating and inspecting AIME pipeline results.

---

## Scripts Overview

### 1. `evaluate_aime.py`

**Purpose**: Generate `evaluation_results.json` for any AIME solutions file.

**Usage**:
```bash
python evaluate_aime.py \
  --solutions="experiments/aime_val/baseline/solutions.json" \
  --dataset="data/aime/validation.json" \
  --output="experiments/aime_val/baseline/evaluation_results.json"
```

**Parameters**:
- `--solutions`: Path to solutions.json (relative to arc_memo root)
- `--dataset`: Path to ground truth dataset (default: data/aime/validation.json)
- `--output`: Output path (defaults to same dir as solutions)
- `--arc-memo-root`: Path to arc_memo repository (auto-detected)

**Output Format** (`evaluation_results.json`):
```json
{
  "correct": 26,
  "total": 60,
  "accuracy": 0.4333,
  "errors": [
    {
      "id": "2024_I_8",
      "predicted": "1",
      "ground_truth": "197"
    },
    ...
  ]
}
```

---

### 2. `filter_correct_lessons.py`

**Purpose**: Filter lesson files to keep only lessons from correctly solved problems.

**Usage**:
```bash
python filter_correct_lessons.py \
  --solutions="experiments/aime_train/o4_solve/solutions.json" \
  --lessons-in="experiments/aime_train/abstraction/lessons.json" \
  --lessons-out="experiments/aime_train/abstraction/lessons_correct.json"
```

**Parameters**:
- `--solutions`: Path to training solutions (relative to arc_memo root)
- `--lessons-in`: Path to all extracted lessons
- `--lessons-out`: Path for filtered output (correct-only)
- `--dataset`: Ground truth dataset(s) for training problems
- `--arc-memo-root`: Path to arc_memo repository (auto-detected)

**Logic**:
- Compares each problem's solution to ground truth
- Keeps lessons only from problems where `solution == ground_truth`
- Handles ID variants (underscore vs hyphen: `2020_I_1` vs `2020-I-1`)

**Output**:
```
Input lessons: 120
Kept (correct): 87
Dropped: 33 (missing answer: 0, missing solution: 0)
Wrote filtered lessons to: experiments/aime_train/abstraction/lessons_correct.json
```

---

### 3. `analyze_costs.py`

**Purpose**: Aggregate token usage and compute API costs across experiment runs.

**Usage**:
```bash
# Analyze all experiments
python analyze_costs.py \
  --experiments-dir="experiments_label_guided"

# Analyze specific stage
python analyze_costs.py \
  --experiments-dir="experiments_label_guided/aime_train"
```

**Parameters**:
- `--experiments-dir`: Path to experiments directory (relative to arc_memo root)
- `--arc-memo-root`: Path to arc_memo repository (auto-detected)

**Output**:
- Per-experiment token usage and costs
- Grand total across all runs
- Breakdown by model (GPT-4.1, o4-mini, Gemini, etc.)

**Pricing Table** (configurable in script):
```python
MODEL_PRICING = {
    "o4-mini-2025-04-16": (1.10, 4.40),  # input, output per 1M tokens
    "gpt-4.1-2025-04-14": (5.00, 15.00),
    "google/gemini-2.5-flash-lite-preview-09-2025": (0.20, 0.60),
    # ... add more models as needed
}
```

**Example Output**:
```
================================================================================
AIME Experiment Cost Analysis
================================================================================

aime_train/solve_20251120-120000
  ======================================================================
  Model: o4-mini-2025-04-16
    Tokens: 1,234,567 in | 567,890 out
    Requests: 120 | Completions: 360
    Cost: $1.357 + $2.498 = $3.855

...

GRAND TOTAL COST: $48.32
```

---

### 4. `reflective_usage_analysis.py`

**Purpose**: Analyze how "reflective" lessons (from initially incorrect training problems) are used during validation.

**Context**: 
- **Label-Guided**: "Reflective" = lessons from problems that were wrong on first attempt but corrected via multi-attempt (n=3, pass@2)
- **Self-Reflective**: All lessons are "reflective" by nature (no correctness labels used)

**Usage**:
```bash
python reflective_usage_analysis.py \
  --train-solutions="experiments/aime_train/o4_solve/solutions.json" \
  --retrieved-concepts="experiments/aime_val/selection/retrieved_concept_uids.json" \
  --baseline-solutions="experiments/aime_val/gemini_baseline/solutions.json" \
  --with-memory-solutions="experiments/aime_val/gemini_with_memory/solutions.json" \
  --output-dir="experiments/aime_val/analysis_reflective"
```

**Parameters**:
- `--train-solutions`: Training problem solutions
- `--retrieved-concepts`: Which lessons were retrieved for each validation problem
- `--baseline-solutions`: Validation solutions without memory
- `--with-memory-solutions`: Validation solutions with memory
- `--output-dir`: Where to write analysis reports
- `--arc-memo-root`: Path to arc_memo repository (auto-detected)

**Output Files**:

1. `summary.json`: High-level statistics
```json
{
  "total_validation_problems": 60,
  "problems_with_reflective_retrieval": 25,
  "problems_with_reflective_and_correct": 18,
  "problems_with_reflective_flip": 7,
  "unique_reflective_origins_seen": 30,
  "unique_reflective_origins_helped": 22,
  "unique_reflective_origins_flip": 10
}
```

2. `problems_with_reflective_retrieval.json`: Which validation problems used reflective lessons
3. `problems_with_reflective_correct.json`: Which ones were solved correctly
4. `problems_with_reflective_flip.json`: Which went from wrong→correct
5. `reflective_origin_usage.json`: Per-training-problem usage stats
6. `reflective_origin_helped.json`: Which training problems' lessons led to correct solves
7. `reflective_origin_flip.json`: Which training problems' lessons caused flips

---

## Integration with Pipelines

All analysis scripts are automatically called at the end of pipeline runs:

### Debug Pipelines:
- `RUN_AIME_SELF_REFLECTIVE_DEBUG.md`
- `RUN_AIME_LABEL_GUIDED_DEBUG.md`

Both include an "Analysis & Reports (Automatic)" section that:
1. Evaluates all solver runs
2. Generates cost analysis
3. (Label-guided only) Runs reflective usage analysis

### Full Pipelines:
- `RUN_AIME_SELF_REFLECTIVE.md`
- `RUN_AIME_LABEL_GUIDED.md`

Both include an "Analysis & Reports" section that:
1. Evaluates training and validation solves
2. Generates cost breakdowns (train + val)
3. (Label-guided only) Runs reflective usage analysis
4. Provides detailed comparison summaries

---

## Common Use Cases

### 1. Evaluate a new solver run
```bash
python evaluate_aime.py \
  --solutions="experiments/aime_val/new_run/solutions.json"
```

### 2. Check if training problems were solved correctly
```bash
python evaluate_aime.py \
  --solutions="experiments/aime_train/o4_solve/solutions.json" \
  --dataset="data/aime/train.json"
```

### 3. Compare costs across different approaches
```bash
python analyze_costs.py --experiments-dir="experiments_self_reflective" > costs_self_reflective.txt
python analyze_costs.py --experiments-dir="experiments_label_guided" > costs_label_guided.txt
diff costs_self_reflective.txt costs_label_guided.txt
```

### 4. Find which lessons are most helpful
```bash
# Run reflective usage analysis
python reflective_usage_analysis.py \
  --train-solutions="..." \
  --retrieved-concepts="..." \
  --baseline-solutions="..." \
  --with-memory-solutions="..." \
  --output-dir="analysis_out"

# Check which training problems' lessons caused the most flips
cat analysis_out/reflective_origin_flip.json | python -m json.tool
```

### 5. Filter lessons for a new abstraction run
```bash
# First, solve training set
python -m concept_mem.data.aime_simple_solver_v3 data=aime_train ...

# Then extract lessons
python -m concept_mem.abstraction.analysis_concepts ...

# Finally, filter to correct-only
python filter_correct_lessons.py \
  --solutions="experiments/aime_train/solve/solutions.json" \
  --lessons-in="experiments/aime_train/abstraction/lessons.json" \
  --lessons-out="experiments/aime_train/abstraction/lessons_correct.json"
```

---

## Output Directory Structure

After running pipelines with analysis, expect:

```
experiments_{self_reflective|label_guided}/
├── aime_train/
│   ├── solve_*/
│   │   └── evaluation_results.json     # Training accuracy
│   └── abstraction_*/
│       ├── lessons.json                # All lessons
│       └── lessons_correct.json        # Filtered (label-guided only)
└── aime_val/
    ├── baseline_*/
    │   └── evaluation_results.json     # Baseline accuracy
    ├── with_memory_*/
    │   └── evaluation_results.json     # With-memory accuracy
    └── analysis/
        ├── cost_analysis_train.txt     # Training costs
        ├── cost_analysis_val.txt       # Validation costs
        ├── summary.json                # Reflective usage summary
        ├── problems_with_reflective_*.json
        └── reflective_origin_*.json
```

---

## Customization

### Adding New Models to Cost Analysis

Edit `MODEL_PRICING` in `analyze_costs.py`:

```python
MODEL_PRICING = {
    "your-model-name": (input_price_per_1M, output_price_per_1M),
}
```

### Using Different Ground Truth Datasets

```bash
python evaluate_aime.py \
  --solutions="..." \
  --dataset="data/aime/full_1983_2025.json"  # Use larger dataset
```

### Filtering with Multiple Datasets

```bash
python filter_correct_lessons.py \
  --solutions="..." \
  --lessons-in="..." \
  --lessons-out="..." \
  --dataset "data/aime/train.json" "data/aime/full_1983_2025.json"
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'orjson'"
```bash
cd arc_memo
pip install orjson
```

### "FileNotFoundError: Solutions file not found"
- Check that paths are relative to `arc_memo/` root
- Use `--arc-memo-root` to specify a different location

### Cost analysis shows "Unknown pricing"
- Add your model to `MODEL_PRICING` in `analyze_costs.py`
- Or accept zero cost for quick testing

### Reflective usage shows 0 reflective problems
- This means all training problems were solved correctly on first try
- Expected for high-performing models or easy training sets
- In label-guided pipeline, this is actually desirable

---

## Dependencies

All scripts use standard library except:
- `orjson` (optional, only if `arc_memo/concept_mem/utils/common.py` uses it)

Install if needed:
```bash
pip install orjson
```

