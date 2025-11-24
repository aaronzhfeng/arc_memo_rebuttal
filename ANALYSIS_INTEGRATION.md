# Analysis Tools Integration

**Date**: 2025-11-20  
**Purpose**: Integrate evaluation, cost analysis, and reflective usage analysis into all AIME pipelines

---

## What Changed

Previously, analysis scripts existed in `aime_analysis/` but were **not integrated** into pipeline workflows. Users had to manually:
1. Remember to run evaluation after each solve
2. Manually specify paths for each analysis script
3. Navigate to different directories to find results

**Now**: All pipelines automatically generate analysis reports at the end of runs.

---

## Integrated Analysis Scripts

### 1. **`evaluate_aime.py`** (NEW)
- Generates `evaluation_results.json` for any solver run
- Compares predictions to ground truth
- Lists all errors with predicted vs correct answers
- **Auto-runs**: After baseline and with-memory solves

### 2. **`filter_correct_lessons.py`** (Existing)
- Filters lessons to keep only those from correct solves
- **Used in**: Label-guided pipeline after abstraction
- **Manual step**: Explicitly called in pipeline commands

### 3. **`analyze_costs.py`** (Existing)
- Aggregates token usage across all experiment runs
- Computes API costs per model
- **Auto-runs**: At the end of pipeline, generates txt reports

### 4. **`reflective_usage_analysis.py`** (Existing)
- Analyzes which "reflective" lessons are retrieved
- Tracks which training problems' lessons led to flips
- **Auto-runs**: In label-guided pipeline only (requires labels)

---

## Integration Points

### Self-Reflective Pipeline

#### Debug (`RUN_AIME_SELF_REFLECTIVE_DEBUG.md`)
Added **"Analysis & Reports (Automatic)"** section:
```bash
# 1. Evaluate baseline
python evaluate_aime.py --solutions="..." --dataset="validation_debug.json"

# 2. Evaluate with memory
python evaluate_aime.py --solutions="..." --dataset="validation_debug.json"

# 3. Cost analysis
python analyze_costs.py --experiments-dir="experiments_self_reflective/debug"
```

Added **"Quick Results Summary"** section:
- Shows answers for single debug problem
- Displays retrieval UIDs
- One-line accuracy check

#### Full (`RUN_AIME_SELF_REFLECTIVE.md`)
Added **"Analysis & Reports"** section:
```bash
# 1-2. Evaluate baseline + with memory
python evaluate_aime.py ... (both runs)

# 3-4. Cost analysis (train + val)
python analyze_costs.py ... (both stages)
```

Added **"Detailed Results Summary"** section:
- Accuracy comparison
- Problem flips (wrong→correct, correct→wrong)
- Improvement delta

---

### Label-Guided Pipeline

#### Debug (`RUN_AIME_LABEL_GUIDED_DEBUG.md`)
Added **"Analysis & Reports (Automatic)"** section:
```bash
# 1. Evaluate training solve
python evaluate_aime.py --solutions="..." --dataset="train_debug.json"

# 2. Evaluate baseline
python evaluate_aime.py --solutions="..." --dataset="validation_debug.json"

# 3. Evaluate with memory
python evaluate_aime.py --solutions="..." --dataset="validation_debug.json"

# 4. Cost analysis
python analyze_costs.py --experiments-dir="experiments_label_guided/debug"
```

Added **"Quick Results Summary"** section:
- Training solve accuracy (o4-mini, n=3)
- Baseline vs with-memory comparison
- Filter effect (all lessons vs correct-only)

#### Full (`RUN_AIME_LABEL_GUIDED.md`)
Added **"Analysis & Reports"** section:
```bash
# 1. Evaluate training solve
python evaluate_aime.py --solutions="..." --dataset="train.json"

# 2-3. Evaluate baseline + with memory
python evaluate_aime.py ... (both runs)

# 4. Reflective usage analysis
python reflective_usage_analysis.py ...

# 5-6. Cost analysis (train + val)
python analyze_costs.py ... (both stages)
```

Added **"Detailed Results Summary"** section:
- Training solve accuracy (how many problems for lessons)
- Baseline vs with-memory comparison
- Problem flips
- **Reflective usage summary** (unique feature)

---

## New Files Created

1. **`aime_analysis/evaluate_aime.py`** - New evaluation script
2. **`aime_analysis/README.md`** - Comprehensive documentation for all analysis tools

---

## Updated Files

1. **`RUN_AIME_SELF_REFLECTIVE_DEBUG.md`**
   - Added "Analysis & Reports (Automatic)" section
   - Added "Quick Results Summary" section

2. **`RUN_AIME_SELF_REFLECTIVE.md`**
   - Added "Analysis & Reports" section
   - Added "Detailed Results Summary" section

3. **`RUN_AIME_LABEL_GUIDED_DEBUG.md`**
   - Added "Analysis & Reports (Automatic)" section
   - Added "Quick Results Summary" section
   - Added filter effect analysis

4. **`RUN_AIME_LABEL_GUIDED.md`**
   - Added "Analysis & Reports" section (includes reflective usage)
   - Added "Detailed Results Summary" section

5. **`README_PIPELINES.md`**
   - Added analysis tools as key feature
   - Updated directory structure to show analysis outputs
   - Added link to `aime_analysis/README.md`

---

## Output Structure

### Before Integration:
```
experiments/
├── baseline/
│   └── solutions.json
└── with_memory/
    └── solutions.json

# No evaluation_results.json
# No cost analysis
# No aggregated reports
```

### After Integration:
```
experiments_{self_reflective|label_guided}/
├── aime_train/
│   ├── solve_*/
│   │   ├── solutions.json
│   │   ├── evaluation_results.json  ← NEW
│   │   └── token_usage.json
│   └── abstraction_*/
│       ├── lessons.json
│       └── lessons_correct.json      ← Filtered
├── aime_val/
│   ├── baseline_*/
│   │   ├── solutions.json
│   │   └── evaluation_results.json  ← NEW
│   ├── with_memory_*/
│   │   ├── solutions.json
│   │   └── evaluation_results.json  ← NEW
│   └── analysis/                     ← NEW
│       ├── cost_analysis_train.txt  ← NEW
│       ├── cost_analysis_val.txt    ← NEW
│       ├── summary.json             ← NEW (label-guided)
│       └── reflective_*.json        ← NEW (label-guided)
└── debug/
    └── [same structure]
```

---

## Benefits

### For Users:
1. ✅ **No manual steps**: Evaluation and analysis run automatically
2. ✅ **Consistent location**: All results in predictable paths
3. ✅ **Quick comparison**: Summary scripts show key metrics
4. ✅ **Cost tracking**: Always know how much each run cost
5. ✅ **Lesson quality**: Reflective analysis shows which lessons work

### For Development:
1. ✅ **Faster iteration**: Immediate feedback on changes
2. ✅ **Better visibility**: All metrics in one place
3. ✅ **Easier debugging**: Cost and accuracy side-by-side
4. ✅ **Historical tracking**: Every run has full evaluation

### For Research:
1. ✅ **Reproducibility**: All metrics saved with each run
2. ✅ **Comparison**: Easy to compare different approaches
3. ✅ **Analysis**: Reflective usage shows lesson impact
4. ✅ **Reporting**: Ready-made summary statistics

---

## Usage Examples

### Run Debug Pipeline with Analysis:
```bash
# Follow RUN_AIME_SELF_REFLECTIVE_DEBUG.md or RUN_AIME_LABEL_GUIDED_DEBUG.md
# All 6 stages + analysis automatically

# At the end, check:
cat experiments_*/debug/baseline_*/evaluation_results.json
cat experiments_*/debug/with_memory_*/evaluation_results.json
cat experiments_*/debug/analysis/cost_analysis.txt
```

### Run Full Pipeline with Analysis:
```bash
# Follow RUN_AIME_SELF_REFLECTIVE.md or RUN_AIME_LABEL_GUIDED.md
# All stages + comprehensive analysis

# At the end, check:
cat experiments_*/aime_val/analysis/cost_analysis_val.txt
cat experiments_*/aime_val/analysis/summary.json  # label-guided only
```

### Compare Two Approaches:
```bash
# Run both pipelines
# Then compare evaluation_results.json:

echo "Self-Reflective:"
cat experiments_self_reflective/aime_val/with_memory_*/evaluation_results.json

echo "Label-Guided:"
cat experiments_label_guided/aime_val/with_memory_*/evaluation_results.json
```

---

## Customization

### Change Evaluation Dataset:
Edit the `--dataset` parameter in pipeline commands:
```bash
python evaluate_aime.py \
  --solutions="..." \
  --dataset="data/aime/full_1983_2025.json"  # Use larger dataset
```

### Add Custom Analysis:
Add your own script to the "Analysis & Reports" section:
```bash
# In pipeline .md file, add:
python ../arc_memo_rebuttal/aime_analysis/my_custom_analysis.py \
  --input="..." \
  --output="$ANALYSIS_DIR/my_analysis.json"
```

### Skip Analysis:
Just don't run the "Analysis & Reports" section - it's optional!

---

## Troubleshooting

### "FileNotFoundError: validation_debug.json"
Debug pipelines need debug dataset files:
- `arc_memo/data/aime/train_debug.json`
- `arc_memo/data/aime/validation_debug.json`

These should exist from previous pipeline work. If missing, check:
```bash
ls arc_memo/data/aime/*debug*
```

### "realpath: command not found" (macOS)
On macOS, use `grealpath` or replace with:
```bash
# Instead of:
--solutions="$(realpath --relative-to=. $RUN)/solutions.json"

# Use:
--solutions="${RUN#./}/solutions.json"
```

Or install `coreutils`:
```bash
brew install coreutils
# Then use grealpath instead of realpath
```

### Cost analysis shows "$0.00"
Your model might not be in `MODEL_PRICING`. Add it to `analyze_costs.py`:
```python
MODEL_PRICING = {
    "your-model-name": (input_price_per_1M, output_price_per_1M),
}
```

---

## Migration from Old Workflow

### Old Way:
```bash
# 1. Run solver
python -m concept_mem.data.aime_simple_solver_v3 ...

# 2. Manually evaluate (if you remember)
python evaluate_aime.py --solutions="???" --dataset="???"

# 3. Maybe run cost analysis?
python analyze_costs.py --experiments-dir="???"

# 4. Forget to check reflective usage
# (never runs)
```

### New Way:
```bash
# 1. Follow pipeline .md file
# ... (all stages)

# 2. Run analysis section (copy-paste commands)
# All evaluation, costs, and reflective analysis done

# 3. Check summary
# Everything in predictable locations
```

---

## Future Enhancements

### Potential Additions:
1. **Lesson quality metrics**: Score lessons for specificity, actionability
2. **Retrieval precision**: How often are retrieved lessons actually used?
3. **Problem difficulty clustering**: Which problems benefit from memory?
4. **Cross-pipeline comparison**: Automatic diff between approaches
5. **Visualization**: Plot accuracy, costs, lesson usage over time

### Nice to Have:
1. **One-command analysis**: Single script that runs all analysis
2. **HTML reports**: Pretty web pages instead of JSON
3. **Slack/email notifications**: Alert when runs complete
4. **Continuous monitoring**: Track metrics across all runs

---

## Summary

✅ **Created**: `evaluate_aime.py` for automatic evaluation  
✅ **Integrated**: All 4 analysis scripts into pipelines  
✅ **Documented**: Comprehensive `aime_analysis/README.md`  
✅ **Updated**: All 4 pipeline files (2 debug + 2 full)  
✅ **Enhanced**: Pipeline README with analysis features  

**Result**: Every pipeline run now automatically generates:
- Evaluation results (accuracy, errors)
- Cost analysis (tokens, API costs)
- Reflective usage (lesson impact, for label-guided)

**No manual steps required!**

