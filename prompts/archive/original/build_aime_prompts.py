#!/usr/bin/env python3
"""
Build example prompts for the AIME pipeline by reusing the exact prompt
definitions from the `arc_memo` codebase. This prevents the docs from
drifting when the solver templates change upstream.
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Dict, Iterable

# ==============================================================================
# Import prompt builders from arc_memo
# ==============================================================================

ARC_MEMO_ROOT = Path(__file__).resolve().parents[2] / "arc_memo"
if not ARC_MEMO_ROOT.exists():
    raise FileNotFoundError(
        f"Expected arc_memo repository at {ARC_MEMO_ROOT}. "
        "Please clone or adjust the path before running this script."
    )

if str(ARC_MEMO_ROOT) not in sys.path:
    sys.path.insert(0, str(ARC_MEMO_ROOT))

from concept_mem.data.aime_simple_solver_v3 import (  # type: ignore  # noqa:E402
    AIME_SYSTEM_PROMPT,
    build_problem_prompt,
)
from concept_mem.abstraction.analysis_concepts import (  # type: ignore  # noqa:E402
    build_abstraction_prompt,
)


# ==============================================================================
# Utility helpers
# ==============================================================================


def normalize_problem_ids(problem_id: str) -> Iterable[str]:
    """Return possible ID variants (underscore vs dash)."""
    yield problem_id
    if "_" in problem_id:
        yield problem_id.replace("_", "-")
    if "-" in problem_id:
        yield problem_id.replace("-", "_")


def load_json_dict(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def load_problem_reasoning(problem_id: str) -> str:
    """Fetch solver reasoning text if available, otherwise return a placeholder."""
    candidate_paths = [
        ARC_MEMO_ROOT
        / "experiments"
        / "aime_train"
        / "o4_reasoning"
        / "thought_processes.json",
        ARC_MEMO_ROOT
        / "experiments"
        / "aime_test_v3"
        / "o4_reasoning"
        / "thought_processes.json",
        ARC_MEMO_ROOT
        / "experiments"
        / "aime_test"
        / "o4_reasoning"
        / "thought_processes.json",
    ]
    for path in candidate_paths:
        data = load_json_dict(path)
        if not data:
            continue
        for variant in normalize_problem_ids(problem_id):
            entry = data.get(variant)
            if entry:
                # stored as list of completions; grab the first
                return entry[0] if isinstance(entry, list) and entry else str(entry)
    return f"[Placeholder reasoning for {problem_id}]"


def load_example_reasonings(example_ids: Iterable[str]) -> Dict[str, str]:
    """Return example reasoning text for ICL examples when available."""
    reasonings = {}
    data = load_json_dict(
        ARC_MEMO_ROOT
        / "experiments"
        / "aime_test_v3"
        / "o4_reasoning"
        / "thought_processes.json"
    )
    for eid in example_ids:
        text = None
        if data:
            for variant in normalize_problem_ids(eid):
                entry = data.get(variant)
                if entry:
                    text = entry[0] if isinstance(entry, list) and entry else str(entry)
                    break
        if not text:
            text = f"[Placeholder reasoning for {eid}]"
        reasonings[eid] = text
    return reasonings


def load_prompt_context(problem_id: str) -> dict | None:
    """Load retrieval context (description + hints) if prompt_info is available."""
    candidate_paths = [
        ARC_MEMO_ROOT
        / "experiments"
        / "aime_val"
        / "selection"
        / "prompt_info.json",
        ARC_MEMO_ROOT
        / "experiments"
        / "run_saves"
        / "aime_val_24_28"
        / "selection"
        / "prompt_info.json",
    ]
    for path in candidate_paths:
        data = load_json_dict(path)
        if not data:
            continue
        for variant in normalize_problem_ids(problem_id):
            entry = data.get(variant)
            if not entry:
                continue
            # prompt_info stores variant -> key -> payload
            first_variant = next(iter(entry.values()), None)
            if isinstance(first_variant, dict):
                return first_variant
    return None


# ==============================================================================
# Helper Functions
# ==============================================================================

def load_aime_problem(problem_id: str) -> dict:
    """Load an AIME problem by ID, searching multiple dataset files."""
    candidate_files = [
        ARC_MEMO_ROOT / "data" / "aime" / "full_1983_2025.json",
        ARC_MEMO_ROOT / "data" / "aime" / "train.json",
        ARC_MEMO_ROOT / "data" / "aime" / "validation.json",
        ARC_MEMO_ROOT / "data" / "aime" / "test.json",
    ]
    for path in candidate_files:
        if not path.exists():
            continue
        with open(path) as f:
            data = json.load(f)
        problems = data.get("problems", data)
        for problem in problems:
            pid = problem.get("id")
            if not pid:
                continue
            for variant in normalize_problem_ids(problem_id):
                if pid == variant:
                    return problem
    raise ValueError(
        f"Problem {problem_id} not found in {', '.join(str(p.name) for p in candidate_files)}"
    )


def load_few_shot_examples(example_ids: Iterable[str]) -> Dict[str, list[dict]]:
    """Load few-shot concept lessons from YAML"""
    examples_file = Path(__file__).parent.parent.parent / "arc_memo" / "data" / "abstract_anno" / "aime_icl_examples.yaml"
    
    with open(examples_file) as f:
        all_examples = yaml.safe_load(f)
    
    filled_examples: Dict[str, list[dict]] = {}
    for pid in example_ids:
        entry = all_examples.get(pid)
        if entry is None:
            continue
        if isinstance(entry, dict) and "concepts" in entry:
            concept_list = entry["concepts"]
        elif isinstance(entry, list):
            concept_list = entry
        else:
            continue
        cleaned = [
            {"situation": concept["situation"], "suggestion": concept["suggestion"]}
            for concept in concept_list
            if concept.get("situation") and concept.get("suggestion")
        ]
        if cleaned:
            filled_examples[pid] = cleaned
    return filled_examples


class DummyProblem:
    """Minimal placeholder used by build_abstraction_prompt for AIME."""

    def __init__(self, uid: str):
        self.uid = uid


# ==============================================================================
# Prompt Builders
# ==============================================================================

def build_solver_prompt_payload(problem_text: str, context: dict | None = None) -> dict:
    """Compose the exact user/system prompts used by the solver."""
    user_prompt = build_problem_prompt(
        problem_text=problem_text,
        context=context,
        lesson_limit=None,
    )
    return {
        "system_prompt": AIME_SYSTEM_PROMPT,
        "user_prompt": user_prompt,
    }


def build_abstraction_prompt_payload(
    problem_id: str,
    answer: str,
    reasoning: str,
    few_shot_examples: Dict[str, list[dict]],
    example_reasonings: Dict[str, str],
) -> str:
    """Compose the abstraction prompt via the arc_memo helper."""
    # `build_abstraction_prompt` only inspects `problem.uid` for AIME runs.
    dummy_problem = DummyProblem(problem_id)
    return build_abstraction_prompt(
        problem=dummy_problem,
        solution=answer,
        thought_process=reasoning,
        fixed_examples=few_shot_examples,
        retrieved_examples=None,
        example_thought_processes=example_reasonings,
        domain_template="aime",
    )


# ==============================================================================
# Main
# ==============================================================================

def main():
    """Build example prompts for an AIME problem using upstream templates."""
    
    print("=" * 70)
    print("Building Example Prompts for AIME Pipeline")
    print("=" * 70)
    
    output_dir = Path(__file__).parent / "aime_example_prompts"
    output_dir.mkdir(exist_ok=True)
    
    # Problem selection – pick one that appears in the test set so reasoning logs exist.
    problem_id = "2019_II_1"
    print(f"\nLoading problem: {problem_id}")
    problem = load_aime_problem(problem_id)
    print(f"  Question: {problem['problem'][:100]}...")
    print(f"  Answer: {problem['answer']}")
    
    problem_reasoning = load_problem_reasoning(problem_id)

    # Few-shot examples used during abstraction (match config defaults).
    example_ids = ["2019-I-1", "2019-I-2", "2019-I-3"]
    print("\nLoading few-shot examples...")
    few_shot_examples = load_few_shot_examples(example_ids)
    example_reasonings = load_example_reasonings(few_shot_examples.keys())
    print(f"  Loaded {len(few_shot_examples)} examples with filled concepts")
    
    # ==========================================================================
    # Prompt 1: Solver (baseline)
    # ==========================================================================
    print("\n1. Building solver prompts...")
    
    baseline_prompt = build_solver_prompt_payload(problem["problem"])
    with open(output_dir / "1a_solver_prompt_baseline.json", "w") as f:
        json.dump(baseline_prompt, f, indent=2)
    with open(output_dir / "1a_solver_prompt_baseline.txt", "w") as f:
        f.write("=" * 70 + "\n")
        f.write("PROMPT 1A: Solver (Baseline, no retrieval)\n")
        f.write("=" * 70 + "\n\n")
        f.write("SYSTEM PROMPT:\n")
        f.write(baseline_prompt["system_prompt"] + "\n\n")
        f.write("USER PROMPT:\n")
        f.write(baseline_prompt["user_prompt"])
    print(f"  ✓ Baseline prompt saved to {output_dir}/1a_solver_prompt_baseline.*")

    context = load_prompt_context(problem_id)
    if context:
        memory_prompt = build_solver_prompt_payload(problem["problem"], context=context)
        with open(output_dir / "1b_solver_prompt_with_memory.json", "w") as f:
            json.dump(memory_prompt, f, indent=2)
        with open(output_dir / "1b_solver_prompt_with_memory.txt", "w") as f:
            f.write("=" * 70 + "\n")
            f.write("PROMPT 1B: Solver (With retrieved lessons)\n")
            f.write("=" * 70 + "\n\n")
            f.write("SYSTEM PROMPT:\n")
            f.write(memory_prompt["system_prompt"] + "\n\n")
            f.write("USER PROMPT:\n")
            f.write(memory_prompt["user_prompt"])
        print(f"  ✓ Memory-augmented prompt saved to {output_dir}/1b_solver_prompt_with_memory.*")
    else:
        print("  ⚠ No prompt_info.json found – skipping memory-augmented solver prompt")
    
    # ==========================================================================
    # Prompt 2: Example solver output (reasoning + boxed answer)
    # ==========================================================================
    print("\n2. Capturing solver output snapshot...")
    solver_output = {
        "answer": str(problem["answer"]),
        "reasoning": problem_reasoning,
    }
    with open(output_dir / "2_solver_output.json", "w") as f:
        json.dump(solver_output, f, indent=2)
    print(f"  ✓ Saved solver output snapshot to {output_dir}/2_solver_output.json")
    
    # ==========================================================================
    # Prompt 3: Abstraction input for GPT-4.1
    # ==========================================================================
    print("\n3. Building abstraction prompt...")
    abstraction_prompt = build_abstraction_prompt_payload(
        problem_id=problem_id,
        answer=str(problem["answer"]),
        reasoning=problem_reasoning,
        few_shot_examples=few_shot_examples,
        example_reasonings=example_reasonings,
    )
    with open(output_dir / "3_abstraction_prompt.txt", "w") as f:
        f.write("=" * 70 + "\n")
        f.write("PROMPT 3: Abstraction (Extract situation–suggestion lessons)\n")
        f.write("=" * 70 + "\n\n")
        f.write(abstraction_prompt)
    print(f"  ✓ Saved abstraction prompt to {output_dir}/3_abstraction_prompt.txt")
    
    # ==========================================================================
    # Summary
    # ==========================================================================
    print("\n" + "=" * 70)
    print("Example Prompts Created")
    print("=" * 70)
    print(f"\nOutput directory: {output_dir}")
    print("\nFiles created:")
    print("  1a_solver_prompt_baseline.json / .txt   - Solver prompt without retrieval")
    if context:
        print("  1b_solver_prompt_with_memory.json / .txt - Solver prompt with retrieved lessons")
    print("  2_solver_output.json                    - Sample solver reasoning + answer")
    print("  3_abstraction_prompt.txt                - Abstraction prompt for GPT-4.1")
    
    print("\nPipeline flow:")
    print("  Solver prompt → Model answer + reasoning → Abstraction prompt → Lessons")
    
    print("\nNote:")
    print("  - Prompts are sourced directly from arc_memo modules.")
    print("  - Edit arc_memo prompt definitions to update downstream docs automatically.")


if __name__ == "__main__":
    main()

