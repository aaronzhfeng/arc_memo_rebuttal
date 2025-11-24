# AIME Domain Generalization

**Purpose:** Demonstrate ArcMemo transfers to mathematical reasoning (addresses qa1C domain generality)

---

## Overview

**Approach:**
- Training: AIME 2020-2023 (~120 problems)
- Validation: AIME 2024-2025 (~60 problems)
- Format: OE (situation-suggestion) - natural for math
- Pipeline: o4 solve + reason → gpt41 abstract → GPT 4.1 Mini test

---

## Key Design Decisions

### 1. Use OE Format (Not PS)
- Situation-suggestion pairs map naturally to math patterns
- No need for artificial "types" and "parameters"
- Simpler pipeline (skip pseudocode conversion)

### 2. o4 Generates Own Reasoning
- o4 solves + explains in ONE call
- Authentic reasoning (not post-hoc reconstruction by gpt41)
- Richer information for abstraction

### 3. Test Model: GPT 4.1 Mini (49.4% baseline)
- Room for improvement (not 95% like o4)
- Accessible via OpenAI API
- Good baseline performance

---

## Pipeline

```
Step 1: o4 solves training problems (2020-2023, 120 problems)
        Input: AIME problem
        Output: Reasoning + Answer
        Model: o4-mini
        
Step 2: gpt41 abstracts concepts
        Input: Problem + o4's reasoning
        Output: Situation-suggestion pairs
        Model: gpt41
        
Step 3: GPT 4.1 Mini baseline (2024-2025, 60 problems)
        Input: Problem only
        Output: Answer
        Model: gpt41_mini
        
Step 4: GPT 4.1 Mini with memory
        Input: Problem + Retrieved concepts
        Output: Answer
        Model: gpt41_mini
```

---

## Implementation

### Setup
```bash
cd arc_memo/data/aime

# 1. Download datasets (requires: pip install datasets pandas)
python download_and_prepare.py

# This creates:
# - train.json (2020-2023, ~120 problems)
# - validation.json (2024-2025, ~60 problems)  
# - full_1983_2025.json (all years, ~960 problems)
```

### Run Experiment
```bash
cd arc_memo

# Full pipeline
bash experiments/aime_pilot.sh

# Or step-by-step (see experiments/README.md)
```

### Evaluate
```bash
cd data/aime

# Check baseline accuracy
python evaluate_results.py \
  ../../experiments/aime_pilot/baseline/o4_solutions.json

# Check with memory
python evaluate_results.py \
  ../../experiments/aime_pilot/with_memory/o4_solutions.json
```

---

## Expected Results

**Baseline (GPT 4.1 Mini):** ~49% (from leaderboard)

**With ArcMemo-OE:** ~54-59% (+5-10% absolute)

**For rebuttal:**
```
Domain Generalization Pilot (AIME):
- Training: 120 problems (2020-2023) → 50-100 concepts
- Testing: GPT 4.1 Mini baseline 49% → with memory 55% (+6%)
- Demonstrates transfer to mathematical reasoning
```

---

## Differences from ARC Pipeline

| Aspect | ARC | AIME |
|--------|-----|------|
| Solver | o4-mini | o4-mini |
| Reasoning gen | gpt41 (post-hoc) | o4 (self-explain) |
| Abstraction | gpt41 | gpt41 |
| Format | PS + OE | OE only |
| Test model | o4-mini | GPT 4.1 Mini |
| Answer type | Python code | Single number |

---

## Files Created

### Data handling
- `data/aime/download_and_prepare.py` - Dataset downloader
- `data/aime/create_validation_ids.py` - Generate ID list
- `data/aime/evaluate_results.py` - Score predictions
- `concept_mem/data/aime_math.py` - Data loader
- `concept_mem/data/aime_solver.py` - o4 solver with reasoning

### Configs
- `configs/data/aime_train.yaml`
- `configs/data/aime_val.yaml`
- `configs/abstraction/aime_thought_process.yaml` (reference only)
- `configs/abstraction/aime_lesson_from_trace.yaml`
- `configs/model/gpt41_mini.yaml`

### Experiment
- `experiments/aime_pilot.sh` - Full pipeline

---

## Status

**Created:** ✅ All files ready  
**Tested:** 🔴 Not yet  
**Priority:** MEDIUM-LOW (optional for rebuttal)

---

## Next Steps

1. Run dataset download (requires network + HuggingFace)
2. Test on 5-10 problems first
3. If promising, run full 120 training problems
4. Evaluate baseline vs with-memory

---

## Decision Point

**For rebuttal, recommend:**
- Skip if time-limited (use logical argument)
- Run if time permits (stronger empirical evidence)

**Rationale:** qa1C already accepts (rating 6); this is enhancement not requirement.

