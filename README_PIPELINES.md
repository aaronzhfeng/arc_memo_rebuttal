# AIME Memory-Augmented Pipelines

Two approaches to learn and retrieve lessons for AIME problem solving.

---

## 📁 Pipeline Structure

### **Self-Reflective Learning**
- **Files**: `RUN_AIME_SELF_REFLECTIVE.md` (full), `RUN_AIME_SELF_REFLECTIVE_DEBUG.md` (debug)
- **Directory**: `experiments_self_reflective/`
- **Approach**: Model learns from its own reasoning without ground truth labels
- **Philosophy**: Meta-cognitive self-improvement through reflection

### **Label-Guided Learning**
- **Files**: `RUN_AIME_LABEL_GUIDED.md` (full), `RUN_AIME_LABEL_GUIDED_DEBUG.md` (debug)
- **Directory**: `experiments_label_guided/`
- **Approach**: Model learns only from verified correct solutions
- **Philosophy**: Quality through correctness filtering

---

## 🔄 Pipeline Comparison

| Aspect | Self-Reflective | Label-Guided |
|--------|----------------|--------------|
| **Training Data** | All problems | Only correct problems |
| **Label Dependency** | ❌ No labels needed | ✅ Requires ground truth |
| **Lesson Quality** | Mixed (includes mistakes) | High (verified correct) |
| **Lesson Coverage** | 100% of training set | ~70-80% (pass@2 rate) |
| **Scalability** | ✅ Works without labels | ⚠️ Needs verification |
| **Use Case** | Exploration, no labels | Maximizing accuracy |

---

## 🎯 Key Features (Both Pipelines)

### 1. **Top 2 Lessons**
- `prompt.hint_lessons_limit=2`
- Reduces noise, keeps most relevant guidance
- Down from previous 5 lessons

### 2. **Self-Assessment Prompt**
- *"If you consider this problem straightforward to solve, you may disregard the following lessons..."*
- Gives model agency to ignore unhelpful lessons
- Prevents memory from hurting on easy problems

### 3. **Automated Analysis Reports**
- ✅ `evaluation_results.json` - Accuracy, errors, comparison
- ✅ Cost analysis - Token usage and API costs per stage
- ✅ Reflective usage - Which lessons helped (label-guided)
- ✅ Generated automatically at the end of each run

### 4. **Organized Output Structure**
```
experiments_{self_reflective|label_guided}/
├── aime_train/          # Training stage outputs
│   ├── joint_*/         # OR solve_*/
│   │   └── evaluation_results.json  # Training accuracy
│   ├── self_reflect_*/  # OR reasoning_*/
│   └── abstraction_*/
│       ├── lessons.json              # All lessons
│       └── lessons_correct.json      # Filtered (label-guided)
├── aime_val/            # Validation stage outputs
│   ├── baseline_*/      # No memory baseline
│   │   └── evaluation_results.json  # Baseline accuracy
│   ├── selection_*/     # Lesson retrieval
│   ├── with_memory_*/   # With retrieved lessons
│   │   └── evaluation_results.json  # With-memory accuracy
│   └── analysis/        # Aggregated analysis reports
│       ├── cost_analysis_train.txt
│       ├── cost_analysis_val.txt
│       └── summary.json  # Reflective usage (label-guided)
└── debug/               # Single-problem testing
    └── [same structure + analysis/]
```

---

## 🐛 Debug Workflows

Both pipelines have debug versions that run on **1 training + 1 validation problem**:

### Purpose:
- Inspect prompts in detail
- Verify lesson quality
- Check retrieval relevance
- Compare baseline vs with-memory
- Tune formatting and phrasing

### Training Problem: `2020-I-1` (geometry)
### Validation Problem: `2024_I_10` (geometry, matching domain)

### Key Inspection Points:
1. ✅ Lesson quality and specificity
2. ✅ Retrieval relevance (are top 2 lessons actually helpful?)
3. ✅ Prompt formatting (self-assessment + lessons)
4. ✅ Model behavior (did it use or ignore lessons?)
5. ✅ Performance impact (did memory help or hurt?)

---

## 📊 Expected Results

### Baseline (No Memory):
- **Target**: ~73% pass@1 on validation

### With Memory (Top 2 + Self-Assessment):
- **Goal**: ≥73% pass@1 (don't hurt performance)
- **Stretch Goal**: >75% pass@1 (beat baseline)

### Success Criteria:
- ✅ No easy problems (1-8) go from correct→wrong
- ✅ At least 2-3 hard problems (9-15) go from wrong→correct
- ✅ Overall pass@1 ≥ baseline

---

## 🚀 Quick Start

### Run Full Pipeline:
```bash
cd arc_memo
source .venv/bin/activate
export OPENAI_API_KEY="sk-..."
export OPENROUTER_API_KEY="sk-or-..."

# Choose one:
# Follow RUN_AIME_SELF_REFLECTIVE.md
# OR
# Follow RUN_AIME_LABEL_GUIDED.md
```

### Run Debug Version:
```bash
# Choose one:
# Follow RUN_AIME_SELF_REFLECTIVE_DEBUG.md
# OR
# Follow RUN_AIME_LABEL_GUIDED_DEBUG.md
```

---

## 📝 Recent Changes

### v2.0 (2025-11-20)
- ✅ Renamed pipelines: 2P5 → Self-Reflective, Correct-Only → Label-Guided
- ✅ Organized outputs into dedicated directories
- ✅ Added debug workflows for both pipelines
- ✅ Reduced from 5 to 2 lessons per problem
- ✅ Added self-assessment prompt
- ✅ Standardized naming conventions

### v1.0 (Previous)
- ✅ Initial 2P5 pipeline (uncertain reflections)
- ✅ Initial correct-only pipeline
- ✅ Baseline 5 lessons per problem

---

## 🔍 Deprecated Files

The following files are superseded by the new structure:

- ~~`RUN_AIME_2P5.md`~~ → Use `RUN_AIME_SELF_REFLECTIVE.md`
- ~~`RUN_AIME_CORRECT_ONLY.md`~~ → Use `RUN_AIME_LABEL_GUIDED.md`
- ~~`RUN_AIME_2P5_DEBUG.md`~~ → Use `RUN_AIME_SELF_REFLECTIVE_DEBUG.md`
- ~~`RUN_AIME_QUICK.md`~~ → Functionality merged into debug versions

---

## 📚 Documentation

- `docs/27_self_assessment_prompt_for_lessons.md` - Design doc for self-assessment feature
- `CHANGES_TOP2_LESSONS.md` - Summary of top-k reduction from 5 to 2
- `docs/26_aime_abstraction_domain_template_bug_fix.md` - Historical bug fixes
- `aime_analysis/README.md` - **Analysis tools documentation** (evaluation, costs, filtering)

---

## 🎯 Next Steps

1. Run debug versions to verify prompt quality
2. Run full pipelines on 60 validation problems
3. Compare results: self-reflective vs label-guided vs baseline
4. Iterate on lesson formatting based on inspection
5. Consider k=1 or k=3 if k=2 isn't optimal

