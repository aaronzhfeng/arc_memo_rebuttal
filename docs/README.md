# ArcMemo Rebuttal Documentation

**Paper:** ArcMemo: Abstract Reasoning Composition with Lifelong LLM Memory  
**ArXiv:** https://arxiv.org/abs/2509.04439  
**Status:** ICLR Rebuttal Phase (Borderline 4.5/10)

---

## Quick Start

1. **Read reviews:** [01_iclr_reviews.md](01_iclr_reviews.md)
2. **Understand strategy:** [02_response_strategy.md](02_response_strategy.md)
3. **Run experiments:** [03_experiments.md](03_experiments.md) → `arc_memo/experiments/`
4. **Track progress:** [04_progress.md](04_progress.md)
5. **Run analysis:** [05_memory_analysis.md](05_memory_analysis.md)

---

## Document Index

### Phase 1: Understanding (00-01)
- **[00_overview.md](00_overview.md)** - What changed, reorganization summary
- **[01_iclr_reviews.md](01_iclr_reviews.md)** - All reviewer feedback, ratings, key concerns

### Phase 2: Strategy (02)
- **[02_response_strategy.md](02_response_strategy.md)** - How to address each reviewer, differentiation from prior work

### Phase 3: Core Execution (03-05, 09)
- **[03_experiments.md](03_experiments.md)** - Main experiment plan (400 puzzles, cross-model, ARC-AGI-2)
- **[04_progress.md](04_progress.md)** - Daily progress tracking
- **[05_memory_analysis.md](05_memory_analysis.md)** - Memory behavior analysis (overview)
- **[09_memory_analysis_experimental_design.md](09_memory_analysis_experimental_design.md)** - ⭐ Detailed experimental design for memory analysis

### Phase 4: AIME Domain Generalization (06-08, 10-15)
- **[06_aime_implementation.md](06_aime_implementation.md)** - AIME domain generalization (optional)
- **[07_aime_pipeline_corrected.md](07_aime_pipeline_corrected.md)** - Updated AIME approach (two-call pattern)
- **[08_aime_empty_response_fix.md](08_aime_empty_response_fix.md)** - o4-mini empty response issue & v2 solver fix
- **[10_aime_o4mini_expand_multi_fix.md](10_aime_o4mini_expand_multi_fix.md)** - o4-mini `n>1` parameter issue & expand_multi fix
- **[11_aime_changes_summary.md](11_aime_changes_summary.md)** - Summary of all AIME fixes and changes (v1→v2)
- **[12_aime_solver_v3_improvements.md](12_aime_solver_v3_improvements.md)** - ⭐ v3 solver with ultra-strict output format
- **[13_aime_domain_specific_prompts.md](13_aime_domain_specific_prompts.md)** - AIME-specific abstraction prompts (no ARC references)
- **[14_aime_prompt_comparison.md](14_aime_prompt_comparison.md)** - A/B test: original vs strict abstraction prompts
- **[15_aime_lesson_format_verification.md](15_aime_lesson_format_verification.md)** - ⭐ Lesson format verification (459 lessons, ready for retrieval)
- **[16_aime_few_shot_instruction.md](16_aime_few_shot_instruction.md)** - Situation–suggestion writing guide for math lessons
- **[17_aime_pipeline_status.md](17_aime_pipeline_status.md)** - Training status and validation plan (AIME run)
- **[18_aime_v3_pipeline_test.md](18_aime_v3_pipeline_test.md)** - Checklist for the 10-problem v3 pipeline dry run
- **[19_aime_prompt_adaptation.md](19_aime_prompt_adaptation.md)** - How solver prompts shifted from ARC grids to AIME boxed answers
- **[20_llmplus_reinstall_guide.md](20_llmplus_reinstall_guide.md)** - Reinstall instructions for the customized `llmplus` package
- **[21_aime_reflection_modes.md](21_aime_reflection_modes.md)** - Overview of corrective, correct-only, and mistake-only reflection pipelines

---

## Critical Tasks

**Must Do:**
1. ✅ Expand to 400 puzzles (statistical power)
2. ✅ Test ARC-AGI-2 (generalization)
3. ✅ Cross-model (Claude, Gemini)
4. ✅ Memory reuse analysis (NEW)
5. ✅ Differentiate from RLAD/NuRL

---

## New: Memory Analysis

**Location:** `rebuttal/analysis/`

**Purpose:** Address j2wS concern "why memory helps"

**Metrics:**
- **Transfer rate:** % cross-puzzle retrieval (goal: >70%)
- **Redundancy:** Concept overlap (indicates reusability)
- **Self-retrieval:** % same-puzzle retrieval (low = good)

**Run:**
```bash
cd rebuttal/analysis
python run_analysis.py --concepts <memory.json> --retrievals <retrievals.json>
```

See [05_memory_analysis.md](05_memory_analysis.md) for details.

---

## Folder Structure

```
rebuttal/
├── docs/              # This folder - organized documentation
│   ├── README.md      # This file
│   ├── 00_overview.md
│   ├── 01_iclr_reviews.md
│   ├── 02_response_strategy.md
│   ├── 03_experiments.md
│   ├── 04_progress.md
│   └── 05_memory_analysis.md (NEW)
├── analysis/          # Memory analysis tools (NEW)
│   ├── memory_analyzer.py
│   ├── run_analysis.py
│   └── README.md
├── writing/           # Draft rebuttal sections
└── arcmemo.pdf        # Original paper

arc_memo/              # Experiment code (separate repo)
├── experiments/
│   ├── README.md
│   └── run.sh
├── concept_mem/data/
│   └── aime_math.py   # (NEW) AIME dataset support
└── configs/
    ├── data/
    │   ├── aime_train.yaml     (NEW)
    │   └── aime_val.yaml       (NEW)
    └── abstraction/
        ├── aime_thought_process.yaml      (NEW)
        └── aime_lesson_from_trace.yaml    (NEW)
```

---

## Timeline

**Week 1:** Run experiments + analysis  
**Week 2:** Writing + internal review  
**Week 3:** Submit rebuttal

---

## Key Reviewers

- **j2wS (Rating 2):** Most critical - focus on novelty + analysis
- **rFxx (Rating 4):** Swing vote - focus on statistics
- **qa1C (Rating 6):** Supportive - address scalability
- **GA2r (Rating 6):** Supportive - address model specificity

---

**Goal:** Move from 4.5 → 6+ average rating

**Updated:** 2025-11-18 (AIME v3 pipeline complete: 107 solved, 459 lessons, ready for validation)
