# Experiments

## Location
Primary experiments in: `/Users/aaronfeng/Repo/ARC_AGI/arc_memo/experiments/`

See: `arc_memo/experiments/README.md` for commands

---

## Core Experiments

### 1. 400-Puzzle Evaluation (CRITICAL)
**Addresses:** rFxx (statistical power), j2wS (sample size)

**Runs:**
- Baseline (retry 0,1,2) on 400 puzzles
- ArcMemo-PS (retry 0,1,2) on 400 puzzles

**Expected:**
- Tighter confidence intervals
- Statistical significance
- Addresses overlapping error bars

**Command:**
```bash
cd arc_memo
bash experiments/run.sh  # Includes 400-puzzle runs
```

---

### 2. ARC-AGI-2 Evaluation (CRITICAL)
**Addresses:** j2wS (narrow evaluation)

**Setup:**
- Create `configs/data/arc_agi_2.yaml`
- Point to ARC-AGI-2 dataset

**Runs:**
- Baseline on ARC-AGI-2
- ArcMemo-PS on ARC-AGI-2

**Expected:**
- Consistent relative improvement
- Demonstrates generalization

---

### 3. Cross-Model Evaluation (HIGH)
**Addresses:** GA2r, rFxx (model specificity)

**Models:**
- Claude Sonnet-4 (val100)
- Gemini 2.5 Flash (val100)

**Expected:**
- Similar relative gains
- Proves model-agnostic approach

---

## Analysis Tasks

### Memory Reuse Analysis
**Addresses:** j2wS (why memory helps)

**Steps:**
1. Parse selection logs
2. Count concept reuse per puzzle
3. Measure cross-problem transfer
4. Compute diversity metrics

**Output:** Statistics + case studies

---

### Ablation Studies
**Addresses:** rFxx (complexity justification)

**Tests:**
1. Empty vs seeded memory
2. Retry=3 (diminishing returns)
3. Reference existing: selection, OE vs PS

---

## Timeline

**Week 1:**
- Launch 400-puzzle runs
- Start ARC-AGI-2 setup
- Begin memory analysis

**Week 2:**
- Complete experiments
- Run analysis
- Generate tables

---

## Results Location

```
arc_memo/experiments/
├── 400pz/baseline_r{0,1,2}/
├── 400pz/arcmemo_ps_r{0,1,2}/
├── claude/
└── gemini/
```

Analysis outputs:
```
rebuttal/analysis/
├── memory_reuse_stats/
├── case_studies/
└── tables/
```

