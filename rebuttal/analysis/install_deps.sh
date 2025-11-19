#!/bin/bash
# Install dependencies for memory analysis

set -e

echo "=================================="
echo "Memory Analysis Dependency Setup"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo ""
    echo "⚠️  WARNING: Not in a virtual environment"
    echo "   Consider activating one first:"
    echo "   cd ../../arc_memo && source .venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Installing dependencies..."
echo ""

# Install packages
pip install sentence-transformers scikit-learn numpy

echo ""
echo "=================================="
echo "✓ Installation complete!"
echo "=================================="
echo ""
echo "Test installation:"
echo "  python3 test_basic.py"
echo ""
echo "Run analysis:"
echo "  python run_analysis.py --concepts ../../arc_memo/data/memory/compressed_v1.json --output report.json"
echo ""

