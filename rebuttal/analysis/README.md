# ArcMemo Memory Analysis

Quantitative analysis of ArcMemo memory behavior to validate conceptual learning vs memorization.

## Purpose

Addresses reviewer concerns about whether performance improvements come from:
- ✓ **Genuine conceptual reuse** (goal)
- ✗ **Simple example recall** (concern)

## Three Core Analyses

### 1. Redundancy Analysis
**Question:** Do similar concepts emerge from different puzzles?

- **Method:** Semantic similarity using sentence transformers
- **Threshold:** >85% similarity = redundant
- **Interpretation:** 
  - High redundancy (10-20%) → Common reusable patterns ✓
  - Low redundancy → Puzzle-specific concepts

### 2. Transferability Analysis ⭐
**Question:** Are concepts reused across puzzles?

- **Method:** Track cross-puzzle vs same-puzzle retrievals
- **Success Criteria:**
  - **>70% cross-puzzle retrieval** → Strong generalization ✓
  - **<30% self-retrieval** → Not just saving solutions ✓

### 3. Self-Retrieval Analysis
**Question:** Do puzzles retrieve their own concepts?

- **Method:** Measure same-puzzle retrieval rate
- **Goal:** Low rate indicates true abstraction

## Installation

```bash
# Activate your virtual environment first
cd arc_memo
source .venv/bin/activate

# Install dependencies
pip install sentence-transformers scikit-learn numpy
```

## Usage

### Basic Analysis (Redundancy Only)

```bash
cd rebuttal/analysis

python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --output memory_report.json
```

### Full Analysis (With Transferability)

```bash
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --retrievals ../../arc_memo/experiments/400pz/arcmemo_ps_r1/retrieved_ids.json \
  --output memory_report.json
```

### Fast Analysis (Skip Contradiction Detection)

```bash
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --no-contradiction \
  --output memory_report.json
```

## Input Files

### Concepts File (Required)
Path: `arc_memo/data/memory/compressed_v1.json`

Format:
```json
{
  "concepts": {
    "puzzle_id_1": {
      "name": "extract objects",
      "kind": "routine",
      "description": "...",
      "parameters": [...],
      "used_in": ["puzzle1", "puzzle2", ...]
    }
  }
}
```

### Retrievals File (Optional, enables transferability)
Path: `experiments/{exp_name}/retrieved_ids.json`

Format:
```json
{
  "puzzle_1": ["concept_a_1", "concept_b_2", ...],
  "puzzle_2": ["concept_a_1", "concept_c_3", ...],
  ...
}
```

## Output Files

### `memory_report.json`
Complete analysis with all metrics and data:
- Redundancy analysis (similarity matrix, clusters, pairs)
- Transferability analysis (per-puzzle breakdown, top concepts)
- Metadata

### `memory_report_interpretation.txt`
Human-readable summary for the rebuttal:
- Key metrics and their interpretation
- Success criteria evaluation
- Recommendations

## Expected Results

Based on preliminary work:

| Metric | Target | Interpretation |
|--------|--------|----------------|
| Transfer Rate | >70% | Strong cross-puzzle reuse |
| Self-Retrieval | <30% | Low memorization |
| Redundancy | 10-20% | Common patterns emerge |

## Advanced Options

```bash
# Custom similarity threshold
python run_analysis.py \
  --concepts concepts.json \
  --similarity-threshold 0.90 \
  --output report.json

# Different sentence transformer model
python run_analysis.py \
  --concepts concepts.json \
  --model all-mpnet-base-v2 \
  --output report.json
```

## Programmatic Usage

```python
from memory_analyzer import MemoryAnalyzer

# Initialize analyzer
analyzer = MemoryAnalyzer(similarity_threshold=0.85)

# Run analysis
report = analyzer.run_full_analysis(
    concepts_path='path/to/concepts.json',
    retrievals_path='path/to/retrievals.json'
)

# Save results
analyzer.save_report(report, 'output.json')

# Access results
print(f"Transfer rate: {report.transferability.transfer_rate:.2%}")
print(f"Redundancy: {report.redundancy.redundancy_rate:.2%}")
```

## Troubleshooting

### "sentence-transformers not installed"
```bash
pip install sentence-transformers scikit-learn
```

### "CUDA out of memory"
Use a smaller model:
```bash
python run_analysis.py --model all-MiniLM-L6-v2 ...
```

### "File not found"
Make sure you're running from `rebuttal/analysis/` directory and paths are relative to there.

## For the Rebuttal

After running analysis, use the interpretation file to:

1. **Show transferability metrics** in response to reviewer concerns
2. **Include concept clusters** as examples of common patterns
3. **Highlight top transferred concepts** as case studies
4. **Compare against success criteria** (>70% transfer, <30% self-retrieval)

Example rebuttal text structure available in `memory_report_interpretation.txt` after analysis.

## References

- Design doc: `rebuttal/docs/05_memory_analysis.md`
- Usage guide: `rebuttal/RUN_ANALYSIS.md`
- Previous analysis: `1_personal_arc_agi_work/ARC_code/A_retrieval/z_analysis.ipynb`

