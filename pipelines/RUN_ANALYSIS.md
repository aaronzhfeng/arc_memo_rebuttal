# Memory Analysis Commands

Commands for analyzing ArcMemo memory behavior (redundancy, transferability, diversity).

Run from project root.

---

## Setup (One-time)

**Requirements:** Python 3.8+ (check: `python3 --version`)

### Quick Setup

```bash
cd rebuttal/analysis
./install_deps.sh
```

### Manual Setup

```bash
# Set up virtual environment (if not already created)
cd arc_memo
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install sentence-transformers scikit-learn numpy

# Verify installation
cd ../rebuttal/analysis
python3 test_basic.py
```

**Remember to activate venv before running analysis:**
```bash
cd arc_memo
source .venv/bin/activate
cd ../rebuttal/analysis
```

See `rebuttal/analysis/INSTALLATION.md` for detailed setup and troubleshooting.

---

## Run Analysis

```bash
cd rebuttal/analysis

# Basic (redundancy only)
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --output memory_report.json

# With transferability (if retrieval logs available)
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --retrievals ../../arc_memo/experiments/400pz/arcmemo_ps_r1/retrieved_ids.json \
  --output memory_report.json

# Skip contradiction detection (faster)
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --no-contradiction \
  --output memory_report.json
```

---

## Output

- `memory_report.json` - Full analysis
- `memory_report_interpretation.txt` - Summary for rebuttal

---

## Key Metrics

**Transfer Rate:** % cross-puzzle retrievals (goal: >70%)  
**Redundancy:** % similar concepts (indicates reusability)  
**Self-Retrieval:** % same-puzzle retrievals (low = good)

---

See `docs/05_memory_analysis.md` for details.

