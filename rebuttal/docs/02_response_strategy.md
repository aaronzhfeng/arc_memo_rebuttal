# Response Strategy

## Core Message

**ArcMemo introduces parameterized, compositional concept memory with test-time updates—distinct from prior work.**

---

## Key Differentiators vs Prior Work

### vs RLAD
- RLAD: Aggregates multiple traces during training
- ArcMemo: Extracts single parameterized concept at test-time
- ArcMemo: Reasoning-based selection (not embedding)
- ArcMemo: Typed parameters + compositional reuse

### vs Metacognitive Reuse
- Focuses on recurring fragments → behaviors
- ArcMemo: Explicit parameterization with typed interfaces
- ArcMemo: Test-time only, no weight updates

### vs NuRL
- NuRL: Integrates into RL training loop
- ArcMemo: Inference-only, no fine-tuning
- ArcMemo: PS format enables higher-order composition

---

## Evidence Strategy

### For j2wS (Most Critical)
**Concerns:** Novelty, narrow eval, missing analysis

**Response:**
1. Clear differentiation table (see above)
2. 400-puzzle results → tighter statistics
3. ARC-AGI-2 results → generalization
4. Memory reuse analysis → why it helps

### For qa1C (Strengthen Support)
**Concerns:** Domain generality, scalability

**Response:**
1. Argue domain-agnostic design (OE = natural language)
2. Propose scalability solutions (pruning, hierarchical)
3. Cross-model results → general approach

### For GA2r (Maintain Support)
**Concerns:** Model specificity, missing details

**Response:**
1. Cross-model results (Claude, Gemini)
2. Complete appendix with prompts
3. Baseline comparison shows o4-mini ≈ Sonnet-4

### For rFxx (Flip to Accept)
**Concerns:** Statistical power, complexity

**Response:**
1. 400-puzzle results → statistical significance
2. Contextualize 4% gain as meaningful on ARC-AGI
3. Ablations justify each component

---

## Rebuttal Structure

### Opening
- Thank reviewers for thoughtful feedback
- Acknowledge valid concerns
- Summarize new experiments

### Main Sections
1. **Novelty Clarification** (j2wS)
   - Comparison table
   - Unique contributions

2. **Expanded Evaluation** (j2wS, rFxx)
   - 400-puzzle results
   - ARC-AGI-2 results
   - Statistical significance

3. **Cross-Model Validation** (GA2r, rFxx)
   - Claude Sonnet-4 results
   - Gemini results
   - Model-agnostic conclusion

4. **Memory Analysis** (j2wS)
   - Concept reuse statistics
   - Transfer examples
   - Diversity metrics

5. **Component Justification** (rFxx)
   - Ablation results
   - Each component's contribution

### Closing
- Summary of improvements
- Commitment to camera-ready updates
- Future work acknowledgment

---

## Tone Guidelines

**Do:**
- Lead with evidence
- Acknowledge limitations honestly
- Thank reviewers specifically

**Don't:**
- Be defensive
- Over-promise
- Dismiss concerns

