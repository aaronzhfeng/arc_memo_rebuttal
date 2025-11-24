#!/usr/bin/env python3
"""
Command-line interface for ArcMemo memory analysis

Usage:
    python run_analysis.py --concepts path/to/concepts.json --output report.json
    
    python run_analysis.py \
        --concepts path/to/concepts.json \
        --retrievals path/to/retrievals.json \
        --output report.json
"""

import argparse
import sys
from pathlib import Path

from memory_analyzer import MemoryAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description='Analyze ArcMemo memory behavior',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis (redundancy only)
  python run_analysis.py \\
    --concepts ../../arc_memo/data/memory/compressed_v1.json \\
    --output memory_report.json
  
  # With transferability analysis
  python run_analysis.py \\
    --concepts ../../arc_memo/data/memory/compressed_v1.json \\
    --retrievals ../../arc_memo/experiments/400pz/arcmemo_ps_r1/retrieved_ids.json \\
    --output memory_report.json
  
  # Skip contradiction detection (faster)
  python run_analysis.py \\
    --concepts ../../arc_memo/data/memory/compressed_v1.json \\
    --no-contradiction \\
    --output memory_report.json
        """
    )
    
    parser.add_argument(
        '--concepts',
        type=str,
        required=True,
        help='Path to concepts JSON file (e.g., compressed_v1.json)'
    )
    
    parser.add_argument(
        '--retrievals',
        type=str,
        default=None,
        help='Path to retrieval logs JSON file (optional, enables transferability analysis)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='memory_report.json',
        help='Output path for analysis report (default: memory_report.json)'
    )
    
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=0.85,
        help='Similarity threshold for redundancy detection (default: 0.85)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Sentence transformer model name (default: all-MiniLM-L6-v2)'
    )
    
    parser.add_argument(
        '--no-contradiction',
        action='store_true',
        help='Skip contradiction detection (faster analysis)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    concepts_path = Path(args.concepts)
    if not concepts_path.exists():
        print(f"Error: Concepts file not found: {concepts_path}")
        sys.exit(1)
    
    if args.retrievals:
        retrievals_path = Path(args.retrievals)
        if not retrievals_path.exists():
            print(f"Error: Retrievals file not found: {retrievals_path}")
            sys.exit(1)
    else:
        retrievals_path = None
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    try:
        analyzer = MemoryAnalyzer(
            similarity_threshold=args.similarity_threshold,
            model_name=args.model
        )
        
        report = analyzer.run_full_analysis(
            concepts_path=str(concepts_path),
            retrievals_path=str(retrievals_path) if retrievals_path else None,
            skip_contradiction=args.no_contradiction
        )
        
        # Save report
        analyzer.save_report(report, str(output_path))
        
        # Print interpretation
        print("\n")
        print(report.interpretation)
        
        print(f"\n✓ Analysis complete. Report saved to: {output_path}")
        print(f"✓ Interpretation saved to: {output_path.with_suffix('').as_posix()}_interpretation.txt")
        
    except Exception as e:
        print(f"\n✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

