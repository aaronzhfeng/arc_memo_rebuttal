#!/usr/bin/env python3
"""
Filter ArcMemo lesson files to keep only entries from correctly solved problems.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable


def normalize_variants(problem_id: str) -> Iterable[str]:
    yield problem_id
    if "_" in problem_id:
        yield problem_id.replace("_", "-")
    if "-" in problem_id:
        yield problem_id.replace("-", "_")


def load_answers(data_paths: Iterable[Path]) -> Dict[str, str]:
    answers: Dict[str, str] = {}
    for path in data_paths:
        if not path.exists():
            continue
        with path.open() as f:
            raw = json.load(f)
        problems = raw.get("problems", raw)
        for entry in problems:
            pid = entry.get("id")
            ans = entry.get("answer")
            if not pid:
                continue
            ans_str = "" if ans is None else str(ans).strip()
            for variant in normalize_variants(pid):
                answers.setdefault(variant, ans_str)
    return answers


def load_json_dict(path: Path) -> Dict:
    with path.open() as f:
        return json.load(f)


def main() -> None:
    default_root = Path(__file__).resolve().parents[2]
    default_arc_memo = default_root / "arc_memo"

    parser = argparse.ArgumentParser(description="Filter lessons to only correct solves.")
    parser.add_argument(
        "--arc-memo-root",
        type=Path,
        default=default_arc_memo,
        help="Path to the arc_memo repository root.",
    )
    parser.add_argument(
        "--solutions",
        type=Path,
        default=Path("experiments/aime_train/o4_solve/solutions.json"),
        help="Path (relative to arc_memo root) to the solver solutions JSON.",
    )
    parser.add_argument(
        "--lessons-in",
        type=Path,
        default=Path("experiments/aime_train/abstraction/lessons.json"),
        help="Path (relative to arc_memo root) to the lessons JSON to filter.",
    )
    parser.add_argument(
        "--lessons-out",
        type=Path,
        default=Path("experiments/aime_train/abstraction/lessons_correct.json"),
        help="Destination (relative to arc_memo root) for filtered lessons.",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        nargs="*",
        default=[
            "data/aime/train.json",
            "data/aime/full_1983_2025.json",
        ],
        help="One or more dataset JSON files (relative to arc_memo root) containing ground-truth answers.",
    )
    args = parser.parse_args()

    arc_memo_root = args.arc_memo_root

    solutions = load_json_dict(arc_memo_root / args.solutions)
    lessons = load_json_dict(arc_memo_root / args.lessons_in)

    solution_map: Dict[str, str] = {}
    for pid, ans in solutions.items():
        solver_ans = "" if ans is None else str(ans).strip()
        for variant in normalize_variants(pid):
            solution_map.setdefault(variant, solver_ans)

    answer_paths = [arc_memo_root / Path(p) for p in args.dataset]
    answer_map = load_answers(answer_paths)

    filtered: Dict[str, list] = {}
    kept = dropped = missing_solution = missing_answer = 0

    for pid, lesson_list in lessons.items():
        answer = next((answer_map.get(v) for v in normalize_variants(pid) if answer_map.get(v) is not None), None)
        solution = next((solution_map.get(v) for v in normalize_variants(pid) if solution_map.get(v) is not None), None)

        if answer is None:
            missing_answer += 1
            dropped += 1
            continue
        if solution is None:
            missing_solution += 1
            dropped += 1
            continue
        if solution and solution == answer:
            filtered[pid] = lesson_list
            kept += 1
        else:
            dropped += 1

    output_path = arc_memo_root / args.lessons_out
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(filtered, f, indent=2, sort_keys=True)

    print(f"Input lessons: {len(lessons)}")
    print(f"Kept (correct): {kept}")
    print(f"Dropped: {dropped} (missing answer: {missing_answer}, missing solution: {missing_solution})")
    print(f"Wrote filtered lessons to: {output_path}")


if __name__ == "__main__":
    main()


