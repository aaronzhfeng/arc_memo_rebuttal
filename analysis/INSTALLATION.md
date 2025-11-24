# Installation Guide for Memory Analysis

## Prerequisites

- Python 3.8+ (check: `python3 --version`)
- pip or conda package manager

## Step 1: Create/Activate Virtual Environment

### Option A: Using venv (recommended)

```bash
cd /Users/aaronfeng/Repo/ARC_AGI/arc_memo

# Create virtual environment (if not already created)
python3 -m venv .venv

# Activate it
source .venv/bin/activate
```

### Option B: Using conda

```bash
conda create -n arcmemo python=3.10
conda activate arcmemo
```

## Step 2: Install Dependencies

The memory analyzer requires additional ML libraries:

```bash
pip install sentence-transformers scikit-learn numpy
```

**Note:** This will also install PyTorch as a dependency. If you have GPU support, you may want to install PyTorch separately first:

```bash
# For GPU (CUDA 11.8)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# For CPU only (smaller download)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Step 3: Verify Installation

```bash
cd /Users/aaronfeng/Repo/ARC_AGI/rebuttal/analysis
python3 test_basic.py
```

Should output: `✓ Basic functionality works!`

## Step 4: Test ML Libraries (Optional)

```bash
python3 -c "from sentence_transformers import SentenceTransformer; print('✓ ML libraries ready')"
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'sentence_transformers'"

Install the dependencies:
```bash
pip install sentence-transformers scikit-learn
```

### "Segmentation fault (core dumped)" or Exit code 139

This usually indicates PyTorch compatibility issues. Try:

1. Reinstall PyTorch:
   ```bash
   pip uninstall torch
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

2. Use CPU-only version:
   ```bash
   export PYTORCH_ENABLE_MPS_FALLBACK=1  # For Mac M1/M2
   ```

3. Check Python version (need 3.8+):
   ```bash
   python3 --version
   ```

### "RuntimeError: Attempting to deserialize object on a CUDA device"

Force CPU usage:
```bash
export CUDA_VISIBLE_DEVICES=""
python run_analysis.py ...
```

### Import errors in sandbox mode

The analysis scripts don't require network access after models are downloaded once. First run may need network to download the sentence-transformer model (~80MB).

## Post-Installation

Once installed, you can run analysis:

```bash
cd /Users/aaronfeng/Repo/ARC_AGI/rebuttal/analysis

# Basic analysis
python run_analysis.py \
  --concepts ../../arc_memo/data/memory/compressed_v1.json \
  --output memory_report.json
```

See `README.md` for full usage instructions.

## Alternative: Analysis Without ML Libraries

If you can't install the ML dependencies, you can still use the analyzer structure:

1. The basic data loading and structure work without ML libraries
2. Redundancy analysis will be skipped (requires sentence transformers)
3. Transferability analysis will work if you have retrieval logs

The analyzer will automatically detect missing libraries and skip redundancy analysis gracefully.

