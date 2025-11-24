#!/usr/bin/env python3
"""
Summarize token usage and approximate costs for AIME runs in arc_memo/experiments.

Usage:
    python -m arc_memo_rebuttal.aime_analysis.analyze_costs \
        [--experiments-dir /path/to/arc_memo/experiments]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Pricing (as of Nov 2024, adjust as needed)
# Format: {model_name: (input_price_per_1M, output_price_per_1M)}
MODEL_PRICING = {
    "o4-mini-2025-04-16": (1.10, 4.40),  # $1.10 input, $4.40 output per 1M tokens
    "gpt-4.1-2025-04-14": (5.00, 15.00),
    "gpt-4.1-mini-2025-04-14": (0.40, 1.60),
    "gpt-4o-2025-05-13": (2.50, 10.00),
    "claude-sonnet-4-20250514": (3.00, 15.00),
    "google/gemini-2.5-flash": (0.35, 1.05),  # example OpenRouter rate; adjust if needed
    "google/gemini-2.5-flash-lite-preview-09-2025": (0.20, 0.60),
}


def find_token_usage_files(base_dir: Path) -> List[Tuple[str, Path]]:
    """Find all token_usage.json files in experiment folders."""
    files = []
    for exp_dir in base_dir.iterdir():
        if exp_dir.is_dir() and not exp_dir.name.startswith("."):
            for token_file in exp_dir.rglob("token_usage.json"):
                rel_path = token_file.relative_to(base_dir)
                files.append((str(rel_path.parent), token_file))
    return sorted(files)


def analyze_token_usage(token_file: Path) -> Dict:
    """Analyze a single token_usage.json file."""
    with token_file.open() as f:
        data = json.load(f)

    after = data.get("after", {})
    results = {}
    for model_name, stats in after.items():
        input_tokens = stats.get("input_tokens", 0)
        output_tokens = stats.get("output_tokens", 0)
        reasoning_tokens = stats.get("reasoning_tokens", 0)
        requests = stats.get("requests", 0)
        completions = stats.get("completions", 0)

        if model_name in MODEL_PRICING:
            input_price, output_price = MODEL_PRICING[model_name]
            input_cost = (input_tokens / 1_000_000) * input_price
            output_cost = (output_tokens / 1_000_000) * output_price
            total_cost = input_cost + output_cost
        else:
            input_cost = output_cost = total_cost = 0.0

        visible_tokens = output_tokens - reasoning_tokens

        results[model_name] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
            "visible_tokens": visible_tokens,
            "requests": requests,
            "completions": completions,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
        }

    return results


def print_experiment_summary(exp_name: str, analysis: Dict):
    """Pretty-print one experiment summary."""
    print(f"\n{exp_name}")
    print("  " + "=" * 70)

    total_cost = 0.0
    for model_name, stats in analysis.items():
        print(f"  Model: {model_name}")
        print(f"    Tokens: {stats['input_tokens']:,} in | {stats['output_tokens']:,} out")
        if stats["reasoning_tokens"] > 0:
            print(
                f"            ({stats['reasoning_tokens']:,} reasoning + {stats['visible_tokens']:,} visible)"
            )
        print(f"    Requests: {stats['requests']} | Completions: {stats['completions']}")
        if stats["total_cost"] > 0:
            print(
                f"    Cost: ${stats['input_cost']:.3f} + ${stats['output_cost']:.3f} = ${stats['total_cost']:.3f}"
            )
        else:
            print("    Cost: Unknown pricing")
        total_cost += stats["total_cost"]

    if len(analysis) > 1:
        print(f"  TOTAL COST: ${total_cost:.3f}")


def main():
    default_repo_root = Path(__file__).resolve().parents[2]
    default_experiments_dir = default_repo_root / "arc_memo" / "experiments"

    parser = argparse.ArgumentParser(description="Summarize token/cost usage for AIME experiments.")
    parser.add_argument(
        "--experiments-dir",
        type=Path,
        default=default_experiments_dir,
        help="Path to the arc_memo/experiments directory.",
    )
    args = parser.parse_args()
    experiments_dir = args.experiments_dir

    if not experiments_dir.exists():
        raise FileNotFoundError(f"Experiments directory not found: {experiments_dir}")

    print("=" * 80)
    print("AIME Experiment Cost Analysis")
    print("=" * 80)
    print(f"\nScanning: {experiments_dir}")

    token_files = find_token_usage_files(experiments_dir)
    if not token_files:
        print("\nNo token_usage.json files found!")
        return

    print(f"Found {len(token_files)} experiments with token usage data\n")

    all_analyses = {}
    grand_total_cost = 0.0

    for exp_name, token_file in token_files:
        try:
            analysis = analyze_token_usage(token_file)
            all_analyses[exp_name] = analysis
            print_experiment_summary(exp_name, analysis)
            for stats in analysis.values():
                grand_total_cost += stats["total_cost"]
        except Exception as exc:
            print(f"\n{exp_name}")
            print(f"  ERROR: {exc}")

    print("\n" + "=" * 80)
    print("GRAND TOTAL")
    print("=" * 80)

    model_totals = {}
    for analysis in all_analyses.values():
        for model_name, stats in analysis.items():
            totals = model_totals.setdefault(
                model_name,
                {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "reasoning_tokens": 0,
                    "requests": 0,
                    "completions": 0,
                    "total_cost": 0.0,
                },
            )
            totals["input_tokens"] += stats["input_tokens"]
            totals["output_tokens"] += stats["output_tokens"]
            totals["reasoning_tokens"] += stats["reasoning_tokens"]
            totals["requests"] += stats["requests"]
            totals["completions"] += stats["completions"]
            totals["total_cost"] += stats["total_cost"]

    for model_name, totals in model_totals.items():
        print(f"\n{model_name}:")
        print(f"  Total tokens: {totals['input_tokens']:,} in | {totals['output_tokens']:,} out")
        if totals["reasoning_tokens"] > 0:
            print(f"                ({totals['reasoning_tokens']:,} reasoning)")
        print(f"  Total requests: {totals['requests']}")
        print(f"  Total cost: ${totals['total_cost']:.2f}")

    print("\n" + "=" * 80)
    print(f"GRAND TOTAL COST: ${grand_total_cost:.2f}")
    print("=" * 80)


if __name__ == "__main__":
    main()


