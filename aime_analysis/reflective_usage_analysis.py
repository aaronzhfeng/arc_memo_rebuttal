"""
Analyze how often reflective (corrected) training concepts are retrieved during
AIME validation inference, using artifacts saved in the main `arc_memo` repo.

Outputs several JSON reports under `arc_memo/experiments/aime_val/analysis_reflective/`.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


def load_answer_map(path: Path) -> Dict[str, str]:
    with path.open() as f:
        blob = json.load(f)
    problems = blob.get("problems", blob)
    return {entry["id"]: str(entry["answer"]).strip() for entry in problems}


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def determine_reflective_origins(train_answers: Dict[str, str], train_solutions: Dict[str, str]) -> Set[str]:
    reflective = set()
    for pid, correct in train_answers.items():
        pred = str(train_solutions.get(pid, "")).strip()
        if pred != correct:
            reflective.add(pid)
    return reflective


def main():
    default_repo_root = Path(__file__).resolve().parents[2]
    default_arc_memo_root = default_repo_root / "arc_memo"

    parser = argparse.ArgumentParser(description="Analyze reflective lesson usage in AIME validation runs.")
    parser.add_argument("--arc-memo-root", type=Path, default=default_arc_memo_root)
    parser.add_argument(
        "--train-solutions",
        type=Path,
        default=Path("experiments/aime_train/o4_solve/solutions.json"),
    )
    parser.add_argument(
        "--retrieved-concepts",
        type=Path,
        default=Path("experiments/aime_val/selection/retrieved_concept_uids.json"),
    )
    parser.add_argument(
        "--baseline-solutions",
        type=Path,
        default=Path("experiments/aime_val/gemini_baseline/solutions.json"),
    )
    parser.add_argument(
        "--with-memory-solutions",
        type=Path,
        default=Path("experiments/aime_val/gemini_with_memory/solutions.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments/aime_val/analysis_reflective"),
    )

    args = parser.parse_args()
    arc_memo_root = args.arc_memo_root

    train_answers = load_answer_map(arc_memo_root / "data" / "aime" / "train.json")
    val_answers = load_answer_map(arc_memo_root / "data" / "aime" / "validation.json")

    train_solutions = load_json(arc_memo_root / args.train_solutions)
    retrieved = load_json(arc_memo_root / args.retrieved_concepts)
    baseline_solutions = load_json(arc_memo_root / args.baseline_solutions)
    with_mem_solutions = load_json(arc_memo_root / args.with_memory_solutions)

    reflective_origins = determine_reflective_origins(train_answers, train_solutions)

    problems_with_reflective = []
    reflective_usage_by_origin: Dict[str, List[str]] = defaultdict(list)
    reflective_helped_by_origin: Dict[str, List[str]] = defaultdict(list)
    reflective_flip_by_origin: Dict[str, List[str]] = defaultdict(list)

    baseline_correct: Dict[str, bool] = {}
    with_mem_correct: Dict[str, bool] = {}
    for pid, answer in val_answers.items():
        baseline_pred = str(baseline_solutions.get(pid, "")).strip()
        with_mem_pred = str(with_mem_solutions.get(pid, "")).strip()
        baseline_correct[pid] = baseline_pred == answer
        with_mem_correct[pid] = with_mem_pred == answer

    for pid, concept_list in retrieved.items():
        reflective_origins_used = sorted({origin for origin, _idx in concept_list if origin in reflective_origins})
        if not reflective_origins_used:
            continue

        entry = {
            "problem_id": pid,
            "origins": reflective_origins_used,
            "baseline_correct": baseline_correct.get(pid, False),
            "with_memory_correct": with_mem_correct.get(pid, False),
        }
        problems_with_reflective.append(entry)

        for origin in reflective_origins_used:
            reflective_usage_by_origin[origin].append(pid)
            if entry["with_memory_correct"]:
                reflective_helped_by_origin[origin].append(pid)
            if entry["with_memory_correct"] and not entry["baseline_correct"]:
                reflective_flip_by_origin[origin].append(pid)

    analysis_dir = arc_memo_root / args.output_dir
    analysis_dir.mkdir(parents=True, exist_ok=True)

    problems_with_reflective.sort(key=lambda x: x["problem_id"])
    for mapping in (reflective_usage_by_origin, reflective_helped_by_origin, reflective_flip_by_origin):
        for key in mapping:
            mapping[key] = sorted(set(mapping[key]))

    reflective_correct = [d for d in problems_with_reflective if d["with_memory_correct"]]
    reflective_flips = [d for d in problems_with_reflective if d["with_memory_correct"] and not d["baseline_correct"]]

    summary = {
        "total_validation_problems": len(val_answers),
        "problems_with_reflective_retrieval": len(problems_with_reflective),
        "problems_with_reflective_and_correct": len(reflective_correct),
        "problems_with_reflective_flip": len(reflective_flips),
        "unique_reflective_origins_seen": len(reflective_usage_by_origin),
        "unique_reflective_origins_helped": len({origin for origin, vals in reflective_helped_by_origin.items() if vals}),
        "unique_reflective_origins_flip": len({origin for origin, vals in reflective_flip_by_origin.items() if vals}),
    }

    def dump(obj, name: str):
        path = analysis_dir / name
        with path.open("w") as f:
            json.dump(obj, f, indent=2, sort_keys=True)

    dump(summary, "summary.json")
    dump(problems_with_reflective, "problems_with_reflective_retrieval.json")
    dump(reflective_correct, "problems_with_reflective_correct.json")
    dump(reflective_flips, "problems_with_reflective_flip.json")
    dump(reflective_usage_by_origin, "reflective_origin_usage.json")
    dump(reflective_helped_by_origin, "reflective_origin_helped.json")
    dump(reflective_flip_by_origin, "reflective_origin_flip.json")


if __name__ == "__main__":
    main()


