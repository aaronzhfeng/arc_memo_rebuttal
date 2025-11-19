# Memory Analysis

**Purpose:** Validate that ArcMemo learns generalizable concepts, not just memorizes solutions

---

## Why This Matters

**Reviewer concern (j2wS):** "Limited analysis of why memory helps. Difficult to assess whether improvement arises from genuine conceptual reuse or simple example recall."

**Our response:** Quantitative analysis of memory behavior

---

## Three Key Questions

### 1. Redundancy
**Question:** Do similar concepts get produced multiple times?

**Method:** Semantic similarity (>85%) between concepts from different puzzles

**Interpretation:**
- High redundancy → Common reusable patterns
- Low redundancy → Puzzle-specific concepts

### 2. Transferability
**Question:** Are concepts reused across puzzles?

**Method:** % of retrievals from different vs same puzzle

**Critical metric:**
- **>70% cross-puzzle:** Strong evidence of generalization ✓
- **<40% cross-puzzle:** May indicate memorization ✗

### 3. Self-Retrieval
**Question:** Do puzzles retrieve their own concepts?

**Method:** Track if puzzle retrieves concepts it generated

**Purpose:** Validate not just "saving solutions"

---

## Implementation

### Tools
- `rebuttal/analysis/memory_analyzer.py` - Full analyzer
- `rebuttal/analysis/run_analysis.py` - Command-line interface

### Run Analysis

```bash
cd rebuttal/analysis

# Basic (redundancy only)
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --output report.json

# With transferability (need retrieval logs)
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --retrievals ../../arc_memo/experiments/400pz/arcmemo_ps_r1/retrieved_ids.json \
  --output report.json
```

### Output
- `memory_analysis_report.json` - Full data
- `memory_analysis_report_interpretation.txt` - Summary

---

## Expected Results

Based on your previous work (`1_personal_arc_agi_work/ARC_code/A_retrieval/z_analysis.ipynb`):

**Global replication counts:**
- Concept `5168d44c_1`: 14 retrievals
- Concept `007bbfb7_1`: 11 retrievals
- Shows concepts ARE being reused across puzzles

**Target metrics:**
- Transfer rate: >60% (goal: >70%)
- Redundancy: 10-20% (moderate overlap)
- Self-retrieval: <30% (low memorization)

---

## For Rebuttal

### Table: Memory Behavior Analysis

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Transfer Rate | X% | Cross-puzzle concept reuse |
| Self-Retrieval | Y% | Same-puzzle retrieval (low = good) |
| Redundancy | Z% | Concept overlap across puzzles |

### Example Text

```markdown
**Memory Analysis (Addresses j2wS concern about "why memory helps"):**

We conducted comprehensive analysis of memory behavior across 400 puzzles:

1. **Transferability:** X% of concept retrievals were cross-puzzle (from different 
   puzzles), with only Y% self-retrieval. This demonstrates genuine abstraction 
   and reuse rather than simple solution memorization.

2. **Redundancy:** Z% of concept pairs showed high semantic similarity (>85%), 
   indicating emergence of common reusable patterns. Examples include [list 2-3 
   concept clusters].

3. **Case Studies:** [Show 2 examples of concept transfer between puzzles]

These metrics validate that ArcMemo extracts generalizable abstractions that 
transfer across problems, addressing concerns about example recall vs conceptual reuse.
```

---

## Case Studies

After running analysis, extract top examples:

```python
# From report.json
top_transfers = report['transferability_analysis']['per_puzzle_breakdown']

# Find good examples where:
# 1. High cross-puzzle retrieval
# 2. Successful solve
# 3. Clear concept connection

# Document in case_studies/
```

---

## Addressing Concerns

### Contradiction & Obsolescence

**Current status:**
- No contradiction in current experiments (~100-400 puzzles)
- Memory size manageable
- No obsolescence issues observed

**For rebuttal:**
```markdown
**Memory Maintenance (Addresses qa1C scalability concern):**

While long-term memory maintenance is future work, we propose:

1. **Contradiction Detection:** Semantic similarity between concepts with 
   conflicting advice. Flag for manual review or automatic resolution.

2. **Obsolescence Handling:** Track concept usage and success rates. Remove 
   concepts with <2 retrievals or <20% success rate after sufficient trials.

3. **Scalability:** Current experiments (~400 puzzles, ~100 concepts) show 
   no maintenance issues. For larger deployments, implement periodic pruning 
   and hierarchical concept merging.

Our evaluation focuses on demonstrating benefit; production systems would 
implement these safeguards.
```

---

## Timeline

1. **Day 1:** Run analysis on existing 100-puzzle data
2. **Day 3:** Run on 400-puzzle results (after experiments complete)
3. **Day 5:** Create case studies
4. **Day 7:** Integrate into rebuttal

---

## Dependencies

```bash
pip install sentence-transformers scikit-learn numpy
```

---

## References

- Previous work: `1_personal_arc_agi_work/ARC_code/A_retrieval/z_analysis.ipynb`
- Concept ID format: `{puzzle_id}_{concept_num}`
- Retrieval tracking: Already implemented in `concept_retrieval.py`

