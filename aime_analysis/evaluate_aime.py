#!/usr/bin/env python3
"""
Evaluate AIME solutions against ground truth and generate evaluation_results.json.

This script compares predicted solutions to ground truth answers and produces
a summary with accuracy, correct count, and detailed error list.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def load_answer_map(path: Path) -> Dict[str, str]:
    """Load ground truth answers from AIME dataset file."""
    with path.open() as f:
        blob = json.load(f)
    problems = blob.get("problems", blob)
    return {entry["id"]: str(entry["answer"]).strip() for entry in problems}


def normalize_answer(answer) -> str:
    """Normalize an answer to a string for comparison."""
    if answer is None or answer == "":
        return ""
    return str(answer).strip()


def evaluate_solutions(
    solutions: Dict[str, str],
    ground_truth: Dict[str, str]
) -> Dict:
    """
    Evaluate solutions against ground truth.
    
    Returns:
        dict with keys: correct, total, accuracy, errors
    """
    errors = []
    correct = 0
    total = len(ground_truth)
    
    for problem_id, gt_answer in ground_truth.items():
        predicted = normalize_answer(solutions.get(problem_id))
        gt_normalized = normalize_answer(gt_answer)
        
        if predicted == gt_normalized:
            correct += 1
        else:
            errors.append({
                "id": problem_id,
                "predicted": predicted,
                "ground_truth": gt_normalized
            })
    
    accuracy = correct / total if total > 0 else 0.0
    
    return {
        "correct": correct,
        "total": total,
        "accuracy": accuracy,
        "errors": errors
    }


def main():
    default_repo_root = Path(__file__).resolve().parents[2]
    default_arc_memo_root = default_repo_root / "arc_memo"
    
    parser = argparse.ArgumentParser(
        description="Evaluate AIME solutions and generate evaluation_results.json"
    )
    parser.add_argument(
        "--arc-memo-root",
        type=Path,
        default=default_arc_memo_root,
        help="Path to the arc_memo repository root."
    )
    parser.add_argument(
        "--solutions",
        type=Path,
        required=True,
        help="Path (relative to arc_memo root) to solutions.json file"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/aime/validation.json",
        help="Path (relative to arc_memo root) to ground truth dataset"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (relative to arc_memo root). Defaults to same dir as solutions."
    )
    
    args = parser.parse_args()
    arc_memo_root = args.arc_memo_root
    
    # Load data
    solutions_path = arc_memo_root / args.solutions
    if not solutions_path.exists():
        raise FileNotFoundError(f"Solutions file not found: {solutions_path}")
    
    with solutions_path.open() as f:
        solutions = json.load(f)
    
    dataset_path = arc_memo_root / args.dataset
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    
    ground_truth = load_answer_map(dataset_path)
    
    # Evaluate
    results = evaluate_solutions(solutions, ground_truth)
    
    # Determine output path
    if args.output:
        output_path = arc_memo_root / args.output
    else:
        output_path = solutions_path.parent / "evaluation_results.json"
    
    # Write results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"AIME Evaluation Results")
    print(f"{'='*60}")
    print(f"Correct: {results['correct']}/{results['total']}")
    print(f"Accuracy: {results['accuracy']:.2%}")
    print(f"\nErrors: {len(results['errors'])}")
    if results['errors']:
        print("\nFirst 5 errors:")
        for error in results['errors'][:5]:
            print(f"  {error['id']}: predicted={error['predicted']}, truth={error['ground_truth']}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more")
    print(f"\nResults written to: {output_path.relative_to(arc_memo_root)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

