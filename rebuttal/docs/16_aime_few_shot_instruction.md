# AIME Few-Shot Instruction Framework

**Date:** 2025-11-18  
**Status:** ✅ Drafted (AIME-specific abstraction guidelines)

---

Context:
This document supplements AIME problem analysis with a reusable framework for writing **situation–suggestion** abstractions. It introduces the idea of describing when a mathematical technique is appropriate (the **situation**) and explaining what to try (the **suggestion**). The purpose is to generate abstractions that can guide solvers on new problems by reusing patterns from earlier ones.

---

Below is a more complete set of instructions for writing `situation`–`suggestion` pairs for AIME-style problems, using the 2019 problems as the mental template. It is written as if instructing a person or model who needs to generate their own pairs. It avoids examples and stays general, focusing on principles, structure, and quality control — similar to how ARC documentation teaches how to write robust concept rules.


## 0. What you are trying to produce

The goal of a situation / suggestion pair is to provide concise, generalizable guidance for recognizing when a mathematical technique is applicable and what action should follow. These pairs should be reusable across many problems, not tied to a single instance.

For each nontrivial idea in a solution, you want a pair:

- situation: a short, structural description of when this idea is relevant.
- suggestion: a short, procedural description of what to try.

Both must be:

- general (work for many problems, not just one);
- precise enough to be actionable;
- about mathematical structure, not about the specific problem text.

An example shape (not tied to any specific problem):

- situation: "When the problem’s condition depends only on the difference of two chosen numbers from a fixed range."  
  suggestion: "Reinterpret the experiment as choosing an ordered pair on a grid and count the number of integer pairs satisfying the inequality."

---

## 1. Workflow for extracting situation–suggestion pairs from a solved problem

Use this procedure on each problem (like the 2019 AIME set):

1. Solve or read the full solution. Do not write pairs until you really understand the logic.
2. List the key nontrivial steps. Ignore routine algebra or geometry; focus on the idea pivots: the first major reinterpretation, the non-obvious counting model, geometric transformations, number-theoretic structure, probabilistic recurrences, and similar.
3. For each such step, write:
   - a trigger condition: what structural pattern in the problem tells you this idea is relevant (this becomes the situation);
   - a method: what algebraic, combinatorial, or geometric move you actually used (this becomes the suggestion).
4. Abstract away all concrete numbers and names. Replace numbers like "20" or "673" and names like "triangle PQR" with generic phrases such as “a finite range of integers” or “a triangle with fixed side lengths.”
5. Check generality. Ask whether the pair could apply to similar AIME problems from other years and whether it references only structure, not specific data.
6. Keep only the strong pairs. Discard pairs that are too specific or too vague. Each problem typically yields one to three strong pairs.

---

## 2. How to write a good "situation"

A situation is a recognition rule. It should answer:

> "What does the problem look like when this technique is relevant?"

Guidelines for writing a situation:

- Use structural language (“when the expression involves…”, “when the behavior of digits…”, etc.).
- Avoid explicit numbers or formulas from any one problem.
- Refer to patterns, not instances.
- Keep the sentence short, readable, and conceptual.
- Describe only the trigger condition, not the technique itself.

A strong situation points to the shape of the problem, not its data.

---

## 3. How to write a good "suggestion"

A suggestion is an action rule. It should answer:

> "Once the solver recognizes the situation, what principle or technique should they apply?"

Guidelines for writing a suggestion:

- State the core mathematical action needed (rewrite, convert, consider modular behavior, count structure, etc.).
- Focus on the method, not the solution of any one problem.
- Keep the language general (“rewrite in terms of”, “analyze carries”, “check for invariants”).
- The suggestion should feel like a nudge, not a worked solution.
- Make sure it can transfer to many other AIME problems.

A strong suggestion should feel like a technique the solver can use repeatedly.

---

## 4. Choosing the right granularity

Do not make concepts too microscopic or too bloated.

- Too small: “When you see a triangle, draw an altitude.” Useless; it applies almost everywhere.
- Too big: “When a geometry problem involves circles, chords, parallel lines, and weird numbers, combine power of a point, radical axis, and inversion.” Overloaded; not a single recognizable skill.

Target: each pair corresponds to a single nontrivial idea you would be annoyed to miss during a timed contest. If you cannot summarize it in one sentence without “and then also…,” you probably have two separate concepts.

---

## 5. Covering the main AIME concept families

Below are the main families you should expect from AIME-style problems (2019 has examples of all). For each family, you should be able to generate multiple situation–suggestion templates.

### 5.1 Digit structure / base representation

Typical structure: repeated digits, digit sums, constraints on decimal form.

- situation: When the problem is about digit sums or patterns of a huge integer built from long blocks of repeating digits or base 10 powers.
- suggestion: Express the repeated-digit blocks using powers of 10, simplify the algebraic sum, and then analyze the decimal representation by tracking carries or borrows and counting uniform digit patterns.

### 5.2 Basic discrete probability and counting on integer grids

Typical structure: choose integers from a range, conditions like B minus J at least 2, or structured seating.

- situation: When objects are chosen from a finite integer range and the condition involves inequalities or adjacency between indices or positions.
- suggestion: Model the choices as points or configurations in a discrete grid (or circular arrangement), describe the allowed region combinatorially, and count it directly or via a complement argument.

### 5.3 Random walks / Markov-style recurrences

Typical structure: moving step-by-step on a lattice or numbered pads, with fixed transition rules.

- situation: When a process moves stepwise between states according to fixed probabilistic rules and you are asked for the probability of ever reaching a target or boundary.
- suggestion: Assign an unknown probability or expected value to each state and write recurrence relations based on one-step transitions, using boundary conditions to solve the system.

### 5.4 Euclidean geometry with parallel lines / similar triangles

Typical structure: multiple segments along sides, parallels to sides, inner polygons.

- situation: When segments parallel to triangle sides cut off smaller similar triangles and you need areas, perimeters, or lengths of resulting polygons.
- suggestion: Use similarity ratios induced by the parallel lines to express key lengths, and then convert these to area or perimeter relations for the inner polygon.

### 5.5 Euclidean geometry with circles, chords, and intersection points

Typical structure: multiple circles through shared points, tangencies, intersections, chords.

- situation: When several circles share common points or tangencies and you need distances involving their intersection points and chords.
- suggestion: Use power of a point and, if needed, homothety or radical axis to relate products of segment lengths from common points, then translate these relations into the desired quantity.

### 5.6 Algebra of gcd/lcm, divisor functions, pretty numbers

Typical structure: gcd and lcm, tau(n), conditions on divisors, consecutive integers.

- situation: When the problem involves gcd, lcm, or divisor-count functions of integers, often in equations or constraints relating multiple numbers or consecutive integers.
- suggestion: Factor the integers into primes, use standard identities like gcd times lcm equals xy and the formula for tau(n), and translate the conditions into constraints on prime exponents to classify all possible factorizations.

### 5.7 Trigonometric power sums and symmetry

Typical structure: expressions like sin^k x plus cos^k x or sign patterns of tan of a doubling angle.

- situation: When symmetric expressions in sin x and cos x or iterated angle-doubling trigonometric functions appear with fixed relationships between multiple powers or angles.
- suggestion: Introduce a simpler variable for a symmetric pair, such as s = sin^2 x and 1 minus s = cos^2 x, or express the angle as a rational multiple of pi, then use identities or recurrences to relate the different powers or iterates.

### 5.8 Polynomials, roots, and symmetric sums

Typical structure: a polynomial with a special point given, roots repeated, complex root-of-unity inputs.

- situation: When a polynomial is specified by a product form or by its value at special complex points and only a few leading coefficients are known, but the question asks about sums or products of roots.
- suggestion: Use Vieta’s formulas and algebraic relations satisfied by the special points, such as roots of unity identities, to express the needed symmetric sums of roots in terms of known coefficients or function values.

### 5.9 Counting factorizations / systems of multiplicative equations

Typical structure: products like abc = 70, cde = 71, efg = 72.

- situation: When several products of overlapping sets of variables are fixed integers, and you need to count integer solutions.
- suggestion: Factor each fixed integer, determine how prime exponents must be distributed among the variables consistently across equations, and count all exponent distributions that satisfy the system.

### 5.10 Structured combinatorics with constraints

Typical structure: seating around a circle, substitutions, adjacency constraints, etc.

- situation: When objects must be arranged with adjacency or position constraints that are local, such as each advisor sitting next to their ambassador or substitutions affecting which players are available later.
- suggestion: Choose a convenient ordering strategy, such as placing constrained objects first, breaking circular symmetry by fixing a reference, or modeling the process as a sequence of states. Then count arrangements or sequences by multiplying choices at each stage.

---

## 6. Multi-concept problems: splitting vs merging

Many AIME problems require multiple ideas. You need to decide whether to write:

- one pair per idea, or
- a single pair that captures the core composite pattern.

Guidelines:

- If the ideas are standard and separable, split them. For example, “translate to DP” and later “solve a linear recurrence” might be separate concepts.
- If one idea is completely subordinate to another (for example, simple algebra cleanup after a power-of-a-point setup), drop the subordinate one as a separate concept.
- If the ideas are inseparable in practice, merge them. For instance, in many circle geometry problems, using power of a point and similarity together might be a single concept if they always appear together in that configuration.

---

## 7. Quality checklist for each situation–suggestion pair

Before accepting a pair, verify:

1. **Recognition:** Could a solver know to apply this just from reading the situation?
2. **Transfer:** Does it clearly apply to many different problems with similar structure?
3. **Actionability:** Does the suggestion tell a concrete technique, not just “think harder”?
4. **Nontriviality:** Is this a step whose absence would genuinely block a typical AIME solver?
5. **Independence from specific data:** No problem numbers and no specific constants unless they are structural.

If any of these fail, revise or discard the pair.

---

## 8. Minimal template to give to a model

You can boil this down to the following instructions for a model or person given a solved AIME problem:

1. Identify one to three nontrivial ideas (not routine algebra or cleanup).
2. For each idea:
   - Write a **situation**: “When a problem’s structure has [X pattern] …”
   - Write a **suggestion**: “Use [Y technique] to [Z purpose] …”
3. Ensure each pair is general, transferable, and not tied to exact numbers or names.
4. Keep each line to one clear, focused sentence.

That is the core protocol. The earlier sections just tell you what “X pattern” and “Y technique” look like across the 2019 AIME landscape.


