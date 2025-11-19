#!/usr/bin/env python3
"""
Build example prompts for AIME pipeline
Demonstrates what prompts are used at each stage
"""

import json
import yaml
from pathlib import Path

# ==============================================================================
# Prompt Templates
# ==============================================================================

# 1. o4 Solver Prompt (from aime_solver.py)
AIME_SOLVE_PROMPT = """
Solve this AIME problem. First explain your reasoning, then give the answer.

Problem: {problem}

Instructions:
1. REASONING: Explain your approach, key insights, and solution steps
2. ANSWER: Provide only the final numerical answer (integer between 0-999)

Format your response exactly as:

REASONING:
[Your detailed thought process and solution steps]

ANSWER: [just the number]
"""

AIME_SYSTEM_PROMPT = "You are an expert mathematics problem solver. Provide clear, step-by-step reasoning."


# 2. Thought Process Prompt (from thought_process.py) - NOT USED for AIME
# For reference only - AIME uses o4's self-generated reasoning instead
THOUGHT_PROCESS_TEMPLATE_ARC = """### Introduction
Consider a class of "ARC" puzzles where each puzzle has a hidden transformation rule...

Your task is to analyze a puzzle and its solution (the transformation rule) write 
out a thought process of someone solving the puzzle including things they might 
try but may not work.

### Examples
{examples}

### Your Puzzle Grid Pairs
{puzzle}

### Your Puzzle Solution
{solution}

### Instruction
Write out the thought process of someone solving the puzzle.
"""


# 3. gpt41 Abstraction Prompt (from analysis_concept_prompts.py)
EXTRACT_LESSON_FROM_TRACE_FS_TEMPLATE = """### Introduction
Consider a class of "ARC" puzzles where each puzzle has a hidden transformation rule 
that maps input grids to output grids. Each puzzle presents several input-output grid 
pairs as reference examples and the task is to predict the transformation rule. Grids 
are 2D numpy integer arrays with integers representing colors. 0 represents black and 
should be treated as the background.

We are trying to learn from puzzles solutions to improve our puzzle solving capabilities. 
Your task is to analyze a puzzle solution and the puzzle solving thought process to 
extract reusable lessons for solving other puzzles. Write problem solving "rules" that 
can be applied to other puzzles. The "rule" format describes a **situation** where it 
might be useful and includes a **suggestion** for what to try out/consider in that situation. 
The given thought process (a sequence of observations and thoughts) demonstrates the 
reasoning process of solving this particular puzzle. Please try to generalize the lessons 
from this puzzle to be broadly useful for other puzzles that may have similar or related 
concepts.

### Instructions
We will provide you with a puzzle solution and a thought process.
- The "situation" component of the lesson should be about what to look for in the puzzle 
  that suggests that a certain concept is in play.
  - Please consider generalizing from the specific observations such that the situation 
    description can handle a class of related puzzles and not just this one.
- Make the lesson general and reusable for other puzzles.
  - Focus on high level ideas.
  - If there are hardcoded values (colors, number, orientation, shape), try to generealize 
    into a broader statement that parameterizes these hardcoded values.
- Write your lessons in a markdown yaml block (have a "```yaml" line before and "```" 
  line after) in the following format:
```yaml
- situation: [description of the conditions/situations/observations where this rule applies]
  suggestion: [suggestion of what to try out/consider in that situation]
```
- Please limit the number of lessons to the most important or broadly useful ones.

### Examples
{examples}

### Puzzle Solution
{solution}

### Puzzle Solving Thought Process
{thought_process}
"""

# Adapt for AIME
AIME_ABSTRACTION_PROMPT = """### Introduction
You are analyzing AIME (American Invitational Mathematics Examination) problems to 
extract reusable mathematical reasoning patterns. AIME problems span various domains 
including algebra, geometry, number theory, and combinatorics.

Your task is to analyze a solved AIME problem and the solver's reasoning process to 
extract reusable lessons for solving other AIME problems. Write problem-solving "rules" 
that describe a **situation** (what patterns to recognize) and a **suggestion** (what 
techniques to try).

### Instructions
We will provide you with a problem, solution, and reasoning process.
- The "situation" should describe mathematical patterns, structures, or conditions
- The "suggestion" should recommend specific techniques or approaches
- Make lessons general and reusable across different problems
- Focus on high-level mathematical insights
- Parameterize specific values (use "when coefficient pattern is..." not "when a=5")

Format:
```yaml
- situation: [mathematical pattern or condition to recognize]
  suggestion: [technique or approach to try]
```

### Examples
{examples}

### Problem
{problem}

### Solution Answer
{answer}

### Solver's Reasoning
{reasoning}
"""


# ==============================================================================
# Helper Functions
# ==============================================================================

def load_aime_problem(problem_id):
    """Load a specific AIME problem"""
    train_file = Path(__file__).parent.parent.parent / "arc_memo" / "data" / "aime" / "train.json"
    
    with open(train_file) as f:
        data = json.load(f)
    
    # Try both formats: dash and underscore
    for p in data['problems']:
        if p['id'] == problem_id or p['id'] == problem_id.replace('_', '-'):
            return p
    
    raise ValueError(f"Problem {problem_id} not found (tried both _ and - formats)")


def load_few_shot_examples():
    """Load few-shot examples from YAML"""
    examples_file = Path(__file__).parent.parent.parent / "arc_memo" / "data" / "abstract_anno" / "aime_icl_examples.yaml"
    
    with open(examples_file) as f:
        all_examples = yaml.safe_load(f)
    
    # Get the first 3 with filled concepts
    filled_examples = {}
    for pid in ['2019-I-1', '2019-I-2', '2019-I-3', '2019-I-4', '2019-I-5']:
        if pid in all_examples:
            example = all_examples[pid]
            # Check if concepts are filled
            if example['concepts'][0]['situation']:
                filled_examples[pid] = example
    
    return filled_examples


def format_few_shot_examples(examples, problems_data):
    """Format few-shot examples for prompt"""
    formatted = []
    
    for i, (pid, data) in enumerate(examples.items(), start=1):
        # Get actual problem text from data
        problem_text = "Problem text not found"
        answer = "N/A"
        for p in problems_data:
            if p['id'] == pid or p['id'] == pid.replace('_', '-'):
                problem_text = p['problem']
                answer = p['answer']
                break
        
        example_str = f"#### Example {i} ({pid})\n"
        example_str += f"Problem: {problem_text}\n"
        example_str += f"Answer: {answer}\n\n"
        example_str += "Extracted Concepts:\n```yaml\n"
        for concept in data['concepts']:
            example_str += f"- situation: \"{concept['situation']}\"\n"
            example_str += f"  suggestion: \"{concept['suggestion']}\"\n"
        example_str += "```"
        formatted.append(example_str)
    
    return "\n\n".join(formatted)


# ==============================================================================
# Prompt Builders
# ==============================================================================

def build_o4_solve_prompt(problem_text):
    """Build prompt for o4 to solve AIME problem"""
    return {
        'system_prompt': AIME_SYSTEM_PROMPT,
        'user_prompt': AIME_SOLVE_PROMPT.format(problem=problem_text)
    }


def build_abstraction_prompt(problem_text, answer, reasoning, few_shot_examples, all_problems):
    """Build prompt for gpt41 to abstract concepts"""
    examples_formatted = format_few_shot_examples(few_shot_examples, all_problems)
    
    return AIME_ABSTRACTION_PROMPT.format(
        examples=examples_formatted,
        problem=problem_text,
        answer=answer,
        reasoning=reasoning
    )


# ==============================================================================
# Main
# ==============================================================================

def main():
    """Build example prompts for 2020-I-1"""
    
    print("="*70)
    print("Building Example Prompts for AIME Pipeline")
    print("="*70)
    
    output_dir = Path(__file__).parent / "aime_example_prompts"
    output_dir.mkdir(exist_ok=True)
    
    # Load problem (use correct ID format with underscore)
    problem_id = "2020_I_1"  # Config format
    problem_id_data = problem_id.replace('_', '_')  # Data might use dash or underscore
    print(f"\nLoading problem: {problem_id}")
    problem = load_aime_problem(problem_id)
    
    print(f"  Question: {problem['problem'][:100]}...")
    print(f"  Answer: {problem['answer']}")
    
    # Load few-shot examples
    print("\nLoading few-shot examples...")
    few_shot_examples = load_few_shot_examples()
    print(f"  Loaded {len(few_shot_examples)} examples with concepts")
    
    # Load all problems for full dataset (needed for few-shot formatting)
    full_file = Path(__file__).parent.parent.parent / "arc_memo" / "data" / "aime" / "full_1983_2025.json"
    with open(full_file) as f:
        full_data = json.load(f)
    all_problems = full_data['problems']
    
    # ===========================================================================
    # Prompt 1: o4 Solver
    # ===========================================================================
    print("\n1. Building o4 solver prompt...")
    
    prompt_1 = build_o4_solve_prompt(problem['problem'])
    
    with open(output_dir / "1_o4_solve_prompt.json", 'w') as f:
        json.dump(prompt_1, f, indent=2)
    
    # Also save as readable text
    with open(output_dir / "1_o4_solve_prompt.txt", 'w') as f:
        f.write("="*70 + "\n")
        f.write("PROMPT 1: o4 Solver (Solve + Reasoning)\n")
        f.write("="*70 + "\n\n")
        f.write("SYSTEM PROMPT:\n")
        f.write(prompt_1['system_prompt'] + "\n\n")
        f.write("USER PROMPT:\n")
        f.write(prompt_1['user_prompt'])
    
    print(f"  ✓ Saved to {output_dir}/1_o4_solve_prompt.*")
    
    # ===========================================================================
    # Prompt 2: Simulate o4's output (for demonstration)
    # ===========================================================================
    print("\n2. Creating simulated o4 output...")
    
    # In real pipeline, this would be o4's actual output
    simulated_o4_output = {
        'answer': problem['answer'],
        'reasoning': "[This would be o4's actual reasoning about the problem]\n\nExample reasoning might include:\n- Identifying key patterns\n- Choosing solution approach\n- Step-by-step solution\n- Verification"
    }
    
    with open(output_dir / "2_o4_output_simulated.json", 'w') as f:
        json.dump(simulated_o4_output, f, indent=2)
    
    print(f"  ✓ Saved to {output_dir}/2_o4_output_simulated.json")
    print(f"  Note: In real pipeline, run aime_solver.py to get actual o4 output")
    
    # ===========================================================================
    # Prompt 3: gpt41 Abstraction
    # ===========================================================================
    print("\n3. Building gpt41 abstraction prompt...")
    
    prompt_3 = build_abstraction_prompt(
        problem_text=problem['problem'],
        answer=simulated_o4_output['answer'],
        reasoning=simulated_o4_output['reasoning'],
        few_shot_examples=few_shot_examples,
        all_problems=all_problems
    )
    
    with open(output_dir / "3_gpt41_abstraction_prompt.txt", 'w') as f:
        f.write("="*70 + "\n")
        f.write("PROMPT 3: gpt41 Abstraction (Extract Concepts)\n")
        f.write("="*70 + "\n\n")
        f.write(prompt_3)
    
    print(f"  ✓ Saved to {output_dir}/3_gpt41_abstraction_prompt.txt")
    
    # ===========================================================================
    # Summary
    # ===========================================================================
    print("\n" + "="*70)
    print("Example Prompts Created")
    print("="*70)
    print(f"\nOutput directory: {output_dir}")
    print("\nFiles created:")
    print("  1_o4_solve_prompt.json / .txt    - o4 solves with reasoning")
    print("  2_o4_output_simulated.json       - Example o4 output")
    print("  3_gpt41_abstraction_prompt.txt   - gpt41 extracts concepts")
    
    print("\nPipeline flow:")
    print("  Prompt 1 (o4) → Output 2 (answer + reasoning) → Prompt 3 (gpt41) → Concepts")
    
    print("\nNote:")
    print("  - For AIME, we skip separate thought process generation")
    print("  - o4 generates reasoning during solving (Prompt 1)")
    print("  - gpt41 abstracts from o4's reasoning (Prompt 3)")


if __name__ == "__main__":
    main()

