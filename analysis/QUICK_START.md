# Quick Start Guide

## TL;DR

```bash
# 1. Install dependencies (one-time)
cd /Users/aaronfeng/Repo/ARC_AGI/arc_memo
source .venv/bin/activate  # or create with: python3 -m venv .venv
pip install sentence-transformers scikit-learn

# 2. Run analysis
cd ../rebuttal/analysis
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --output memory_report.json

# 3. View results
cat memory_report_interpretation.txt
```

## What This Does

Analyzes ArcMemo's memory to answer:

1. **Redundancy**: Do similar concepts emerge from different puzzles? (10-20% = good)
2. **Transferability**: Are concepts reused across puzzles? (>70% = excellent)
3. **Self-Retrieval**: Do puzzles just retrieve their own concepts? (<30% = good)

## Current Status

✅ **Implementation**: Complete and tested
✅ **Data Available**: 270 concepts from `compressed_v1.json`
⚠️ **ML Libraries**: Need to be installed (see INSTALLATION.md)
⚠️ **Retrieval Logs**: Need to be generated from experiments

## Next Steps

### If you have retrieval logs:

```bash
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --retrievals ../../arc_memo/experiments/YOUR_EXP/retrieved_ids.json \
  --output full_report.json
```

### If you don't have retrieval logs yet:

The analyzer can still run redundancy analysis:

```bash
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --output redundancy_only.json
```

This will analyze which concepts are semantically similar.

## Expected Output

Two files:
1. `memory_report.json` - Full quantitative data
2. `memory_report_interpretation.txt` - Human-readable summary for rebuttal

The interpretation file includes:
- Transfer rate (goal: >70%)
- Self-retrieval rate (goal: <30%)
- Redundancy rate (10-20% is good)
- Recommendations for rebuttal

## For the Rebuttal

Use the interpretation file to:
- Address reviewer j2wS's concern about "why memory helps"
- Show quantitative evidence of conceptual reuse
- Demonstrate genuine abstraction vs memorization

See `README.md` for detailed usage and `INSTALLATION.md` for setup help.

