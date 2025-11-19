# AIME Pipeline Prompts

Example prompts for each stage of the AIME experiment.

**Generated for:** Problem 2020-I-1

---

## Pipeline Overview

```
Prompt 1 (o4-mini)
    ↓
Answer + Reasoning
    ↓
Prompt 3 (gpt41)
    ↓
Concepts (situation-suggestion pairs)
```

**Note:** For AIME, we skip separate thought process generation (Prompt 2).  
o4 generates reasoning during solving.

---

## Files

### 1_o4_solve_prompt.txt
**Model:** o4-mini  
**Purpose:** Solve AIME problem with self-explanation  
**Output:** Answer (number) + Reasoning (text)

### 2_o4_output_simulated.json
**Purpose:** Example of o4's output  
**Note:** In real run, this comes from `aime_solver.py`

### 3_gpt41_abstraction_prompt.txt
**Model:** gpt41  
**Purpose:** Extract concepts from o4's solution  
**Input:** Problem + Answer + o4's reasoning + Few-shot examples  
**Output:** Situation-suggestion pairs

---

## Generate Custom Prompts

```bash
cd rebuttal/prompts
python build_aime_prompts.py
```

Edit the script to change target problem ID.

---

## Actual Pipeline Commands

See `../RUN_AIME.md` for running the full experiment.

