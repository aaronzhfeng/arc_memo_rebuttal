# AIME Prompt Templates

This document summarizes the prompt templates used in `RUN_AIME_COMPACT.md`.

Templates are pulled directly from the `arc_memo` codebase so the summary stays in sync with implementation.

## Step 1 / Step 4 — Solver Prompts (o4-mini & Gemini)

**AIME_SYSTEM_PROMPT**  
_Source: `concept_mem/data/aime_simple_solver_v3.py`_
```text
You are solving AIME (American Invitational Mathematics Examination) problems.

You may think step by step internally, but your final answer MUST appear exactly once as \boxed{XYZ}.

Requirements for the final output:
- Use \boxed{XYZ} for the answer and nowhere else in the response.
- \boxed{XYZ} must contain only the integer (0–999) with no spaces, wording, punctuation, or leading zeros (unless the answer is 0).
- Do not print unboxed standalone integers on their own lines; embed intermediate numbers inside sentences or equations.

Example of correct output: \boxed{237}

Examples of incorrect output: "Final Answer: 237", "237 ", "\boxed{The answer is 237}", "\boxed{0237}", or any response with multiple boxed expressions.
```

**AIME_SOLVE_PROMPT**  
_Source: `concept_mem/data/aime_simple_solver_v3.py`_
```text
Solve this AIME problem:

{problem}
```

**AIME_OUTPUT_REQUIREMENT**  
_Source: `concept_mem/data/aime_simple_solver_v3.py`_
```text
Output only the integer answer, and wrap it exactly once as \boxed{XYZ}.

Guidelines:
- Mention intermediate numbers only inside sentences/equations so they are not mistaken for answers.
- Do not use \boxed anywhere else in the response.
- The grader will read the boxed integer wherever it appears.
```


## Step 2 — Thought Process / Reflection (o4-mini)

**AIME_THOUGHT_PROCESS_TEMPLATE (correct solve)**  
_Source: `concept_mem/data/aime_thought_process.py`_
```text
You are a mathematics expert who has just solved an AIME problem. Your task is to explain your reasoning process - how you approached the problem, what insights led to the solution, and what techniques you used.

### Your Problem
{problem}

### Your Answer
{correct_answer}

### Instruction
Explain your thought process for solving this problem.
- Focus on key insights and reasoning steps
- Explain why you chose this approach
- Mention what you tried or considered
- Organize as a coherent narrative (not code)

Format: Write a clear explanation of your solution approach and reasoning.
```

**REFLECTIVE_THOUGHT_PROCESS_TEMPLATE (when initial attempt was wrong)**  
_Source: `concept_mem/data/aime_thought_process.py`_
```text
You are a math expert helping to analyze solutions. For each problem, you will be given:
- The Problem.
- An initial Solution Attempt (with the answer given by the solver).
- The Correct Answer.

Your job: Explain **why the attempt was wrong and how to correctly solve the problem**. Identify any mistakes in the attempt, then provide a step-by-step corrected solution that leads to the correct answer.

**Example 1:**
Problem: A jar has 5 red and 3 blue marbles. If 2 marbles are drawn without replacement, what is the probability both are red?
Initial Attempt and Answer: "We treat it as independent draws: P(red, then red) = 5/8 × 5/8 = 25/64. So the answer is 25/64."
Correct Answer: 5/14.
**Reflection:** The attempt assumed the draws were independent with replacement, which was a mistake. After drawing one red, the total marbles and red count change. The correct calculation is P(red then red) = (5/8) × (4/7) = 20/56 = 5/14. The error was not accounting for the decreased total and red count on the second draw.

**Example 2:**
Problem: How many ways can you choose 2 people out of 5 people to form a team?
Initial Attempt and Answer: "Order might matter, so compute 5P2 = 5 × 4 = 20 ways."
Correct Answer: 10.
**Reflection:** The attempt counted each pair twice because order doesn’t matter in a combination. The correct approach is to use combinations: C(5,2) = (5 × 4)/2! = 10. The mistake was treating it as an ordered permutation instead of an unordered selection.

**Now your turn:**
Problem: {problem}
Initial Attempt and Answer: "{attempt}" (Incorrect)
Correct Answer: {correct_answer}
**Reflection:**
```


## Step 3 — Memory Abstraction (gpt-4.1)

**EXTRACT_LESSON_FROM_AIME_FS_TEMPLATE_STRICT**  
_Source: `concept_mem/abstraction/analysis_concept_prompts.py`_
```text
### Introduction

You are analyzing AIME (American Invitational Mathematics Examination) problems to extract reusable mathematical reasoning patterns. AIME problems span algebra, geometry, number theory, combinatorics, and probability, and are typically solvable with high-school level contest techniques.

Your task is to analyze a solved problem and its reasoning process to extract reusable lessons for solving other AIME problems. These lessons should be phrased as problem-solving "rules" that describe:

- a **situation** (what structural pattern to recognize), and
- a **suggestion** (what concrete technique to try).

### Instructions

We will provide you with a problem answer and the solver's reasoning process.

Your job is to output ONLY a markdown YAML block containing 2–5 lessons, each of the form:

```yaml
- situation: [mathematical pattern or condition to recognize]
  suggestion: [technique or approach to try]
```

No extra prose, no headings, no explanation outside the YAML list.

Design the lessons with the following constraints:

1. **General but Detectable Situations**
   - Describe structural patterns, not specific numbers.
   - Parameterize values: e.g. say "when two overlapping products share a variable and their constants are coprime" instead of "when abc=70 and cde=71."
   - It is acceptable to mention qualitative properties like "prime," "perfect square," "consecutive integers," "equally spaced points," "similar triangles," etc.

2. **Concrete, Executable Suggestions**
   - Each *suggestion* must describe specific mathematical actions a capable student could carry out: introduce a variable, write a recurrence, apply similarity, set up a system, use the shoelace formula, count lattice points, etc.
   - Avoid vague advice like "analyze carefully," "be systematic," or "consider symmetry" unless you immediately follow it with a concrete procedure.
   - At least **one** lesson must encode the **main key step** from the solution in an explicit way (for example, "define P(k) as … and write a recurrence P(k) = …", or "view each k-digit block of 9s as 10^k − 1 and sum these as a geometric series").

3. **AIME-Level Methods Only**
   - Use tools appropriate for AIME: algebraic manipulation, inequalities, modular arithmetic, recurrences, casework, combinatorial counting, similarity, Pythagorean triples, coordinate geometry, area/ratio arguments, parity, basic number theory (gcd/lcm, prime factorization, divisor-count formulas), etc.
   - Do NOT invoke heavy or unnecessary methods such as Fourier analysis, character sums, measure theory, advanced group theory, or anything beyond typical high-school olympiad/AIME level.

4. **Avoid Problem-Specific Overfitting**
   - Do not refer to problem labels, specific variable names from the statement, or the problem's numerical constants.
   - Do NOT restate the original problem in disguise.
   - Ask yourself: "Would this lesson still be useful if all the numbers were changed but the structure stayed the same?" If not, generalize it.

5. **No Trivial or Meta Advice**
   - Do not include lessons like "re-read the problem," "check your arithmetic," or "answer the question at the end."
   - Focus only on *mathematical structure* and *methods*.

6. **Faithfulness to the Given Solution**
   - Base your lessons on actual reasoning steps visible in the solver's process.
   - You may compress, reorganize, or generalize those steps, but do not invent fundamentally different solution methods that are not suggested by the reasoning.
   - If the reasoning describes a correction of a previous error, formulate the lesson as the correct strategy (and optionally a brief warning of the pitfall) in general terms.

### Examples
{examples}

### Problem Answer
{solution}

### Solver's Reasoning
{thought_process}
```

