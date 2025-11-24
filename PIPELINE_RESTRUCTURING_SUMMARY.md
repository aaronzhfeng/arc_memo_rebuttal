# Pipeline Restructuring Summary

**Date**: 2025-11-20  
**Purpose**: Better organization, naming, and debug workflows for AIME memory-augmented pipelines

---

## 📝 What Changed

### 1. **Renamed Pipelines** for Clarity

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| "2P5" / "Uncertain" | **Self-Reflective** | Describes learning from model's own reflection |
| "Correct-Only" | **Label-Guided** | Describes filtering by ground truth labels |

### 2. **Organized Output Directories**

**Old Structure** (everything mixed):
```
experiments_2p5/
experiments/
├── various runs mixed together
└── hard to track which approach
```

**New Structure** (separated by approach):
```
experiments_self_reflective/
├── aime_train/
│   ├── joint_*
│   ├── self_reflect_*
│   └── abstraction_*
├── aime_val/
│   ├── baseline_*
│   ├── selection_*
│   └── with_memory_*
└── debug/
    └── [same structure, 1 problem each]

experiments_label_guided/
├── aime_train/
│   ├── solve_*
│   ├── reasoning_*
│   └── abstraction_*
├── aime_val/
│   ├── baseline_*
│   ├── selection_*
│   └── with_memory_*
└── debug/
    └── [same structure, 1 problem each]
```

### 3. **Added Debug Workflows**

Both pipelines now have dedicated debug versions:
- `RUN_AIME_SELF_REFLECTIVE_DEBUG.md`
- `RUN_AIME_LABEL_GUIDED_DEBUG.md`

**Debug Features**:
- ✅ Run on 1 training + 1 validation problem
- ✅ Inspect prompts, lessons, and outputs in detail
- ✅ Compare baseline vs with-memory side-by-side
- ✅ Verify lesson quality and retrieval relevance
- ✅ Faster iteration on prompt engineering

### 4. **Standardized Naming Conventions**

**Self-Reflective Stages**:
1. `joint_*` - Joint solve + reasoning
2. `self_reflect_*` - Reflection without labels
3. `abstraction_*` - Lesson extraction
4. `selection_*` - Lesson retrieval
5. `with_memory_*` - Solve with lessons
6. `baseline_*` - Solve without lessons

**Label-Guided Stages**:
1. `solve_*` - Initial solutions (with labels)
2. `reasoning_*` - Detailed thought processes
3. `abstraction_*` - Lesson extraction + filtering
4. `selection_*` - Lesson retrieval
5. `with_memory_*` - Solve with correct-only lessons
6. `baseline_*` - Solve without lessons

---

## 📁 New File Structure

### Main Pipelines:
- ✅ `RUN_AIME_SELF_REFLECTIVE.md` (replaces `RUN_AIME_2P5.md`)
- ✅ `RUN_AIME_LABEL_GUIDED.md` (replaces `RUN_AIME_CORRECT_ONLY.md`)

### Debug Workflows:
- ✅ `RUN_AIME_SELF_REFLECTIVE_DEBUG.md` (NEW)
- ✅ `RUN_AIME_LABEL_GUIDED_DEBUG.md` (NEW)

### Documentation:
- ✅ `README_PIPELINES.md` - Overview and comparison
- ✅ `PIPELINE_RESTRUCTURING_SUMMARY.md` (this file)

### Deprecated (marked but preserved):
- ⚠️ `RUN_AIME_2P5.md` - Use `RUN_AIME_SELF_REFLECTIVE.md` instead
- ⚠️ `RUN_AIME_CORRECT_ONLY.md` - Use `RUN_AIME_LABEL_GUIDED.md` instead
- ⚠️ `RUN_AIME_QUICK.md` - Functionality merged into debug versions

---

## 🎯 Key Improvements

### For Users:
1. **Clearer naming**: "Self-Reflective" vs "Label-Guided" is self-explanatory
2. **Better organization**: Each approach has its own directory
3. **Debug workflow**: Single-problem testing for prompt engineering
4. **Easier comparison**: Standardized structure makes it easy to compare

### For Development:
1. **Prompt inspection**: Debug versions let you see exact prompts
2. **Faster iteration**: Test on 1 problem instead of 120+60
3. **Quality control**: Verify lessons before full runs
4. **Modularity**: Each stage has clear inputs/outputs

---

## 🔄 Migration Guide

### If you were using `RUN_AIME_2P5.md`:
```bash
# Old
cd experiments_2p5/

# New - follow RUN_AIME_SELF_REFLECTIVE.md
cd experiments_self_reflective/
```

### If you were using `RUN_AIME_CORRECT_ONLY.md`:
```bash
# Old
cd experiments/

# New - follow RUN_AIME_LABEL_GUIDED.md
cd experiments_label_guided/
```

### If you were using `RUN_AIME_QUICK.md`:
```bash
# Old - single comparison file

# New - use debug versions for detailed inspection:
# RUN_AIME_SELF_REFLECTIVE_DEBUG.md
# RUN_AIME_LABEL_GUIDED_DEBUG.md
```

---

## 🐛 Debug Workflow Benefits

### Before (no debug workflow):
1. Run full pipeline on 120 training + 60 validation problems
2. Wait 30-60 minutes
3. Inspect results
4. If prompts need adjustment, go back to step 1
5. ❌ Slow iteration

### After (with debug workflow):
1. Run debug on 1 training + 1 validation problem
2. Wait 2-3 minutes
3. Inspect prompts, lessons, and outputs in detail
4. Adjust formatting, phrasing, or parameters
5. Repeat until satisfied
6. Run full pipeline with confidence
7. ✅ Fast iteration

---

## 📊 What Stayed the Same

- ✅ Core algorithms unchanged
- ✅ Model selection unchanged (Gemini 2.5 Flash Lite)
- ✅ Top 2 lessons + self-assessment (recent improvement)
- ✅ Evaluation metrics (pass@1, pass@2)

---

## 🚀 Recommended Workflow

### Step 1: Debug First
```bash
# Choose your approach and run debug version
# Inspect lessons, prompts, and outputs
# Iterate until prompts look good
```

### Step 2: Full Run
```bash
# Once debug looks good, run full pipeline
# Compare baseline vs with-memory
# Measure pass@1 and pass@2
```

### Step 3: Analysis
```bash
# Which problems did memory help?
# Which problems did memory hurt?
# Are lessons relevant and specific?
# Is retrieval working well?
```

### Step 4: Iterate
```bash
# Based on analysis, adjust:
# - Lesson formatting (situation/suggestion structure)
# - Retrieval prompt
# - Self-assessment phrasing
# - top_k value (1, 2, or 3)
```

---

## ✅ Completed Tasks

- [x] Renamed pipeline files with clear descriptive names
- [x] Created organized directory structure
- [x] Added debug workflows for both pipelines
- [x] Standardized naming conventions across stages
- [x] Created README_PIPELINES.md overview
- [x] Marked deprecated files with migration notes
- [x] Documented restructuring rationale

---

## 🔮 Future Improvements

### Potential Additions:
1. **Comparison script**: Automatically compare self-reflective vs label-guided
2. **Lesson quality metrics**: Score lessons for specificity, generality, etc.
3. **Retrieval analysis**: Visualize which lessons are retrieved most often
4. **A/B testing framework**: Systematic comparison of variations

### Nice to Have:
1. **One-command run**: Script that runs debug → full → analysis
2. **Lesson curation**: Manual filtering of high-quality lessons
3. **Cross-domain testing**: Apply AIME lessons to other math problems
4. **Lesson clustering**: Group similar lessons to reduce redundancy

---

## 📞 Questions?

See `README_PIPELINES.md` for:
- Pipeline comparison table
- Quick start guide
- Expected results
- Success criteria

For prompt engineering details:
- `docs/27_self_assessment_prompt_for_lessons.md`
- `CHANGES_TOP2_LESSONS.md`

