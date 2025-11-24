# ICLR Reviews for ArcMemo (Submission 14154)

**Paper:** ArcMemo: Abstract Reasoning Composition with Lifelong LLM Memory  
**ArXiv:** https://arxiv.org/abs/2509.04439  
**Status:** Borderline (avg 4.5/10)

---

## Summary

| Reviewer | Rating | Confidence | Key Concerns |
|----------|--------|------------|--------------|
| j2wS | 2 (reject) | 5 (certain) | Novelty vs RLAD/NuRL; narrow eval |
| qa1C | 6 (accept) | 3 (fair) | Domain generality; scalability |
| GA2r | 6 (accept) | 3 (fair) | Model specificity (o4-mini only) |
| rFxx | 4 (reject) | 3 (fair) | Statistical power; complexity |

**Average:** 4.5 (borderline)

---

## Critical Issues

### 1. Novelty (j2wS)
- Similar to RLAD, Metacognitive Reuse, NuRL
- Need clear differentiation

### 2. Evaluation Scope (j2wS, rFxx)
- Only 100 puzzles → overlapping error bars
- Only ARC-AGI-1 → generalization unclear
- **Solution:** Expand to 400 puzzles, test ARC-AGI-2

### 3. Model Specificity (GA2r, rFxx)
- Only tested o4-mini
- **Solution:** Test Claude, Gemini

### 4. Analysis Depth (j2wS)
- Why does memory help?
- **Solution:** Quantify concept reuse

---

## Detailed Reviews

### Reviewer j2wS (Rating: 2)

**Weaknesses:**
1. Limited novelty vs RLAD/Metacognitive/NuRL
2. Narrow evaluation (ARC-AGI-1 only)
3. Insufficient analysis of memory behavior

**Questions:**
- How does one concept per puzzle enable cross-problem learning?
- Oracle@k vs pass@k metrics?
- Why does retry increase std deviation?

---

### Reviewer qa1C (Rating: 6)

**Strengths:**
- Novel conceptual framework
- Strong empirical results

**Concerns:**
- Domain generality unclear
- Memory scalability challenges
- Heavy reliance on correct traces

---

### Reviewer GA2r (Rating: 6)

**Strengths:**
- Interesting and original
- Effective retrieval mechanism

**Concerns:**
- Only o4-mini tested
- Missing implementation details

---

### Reviewer rFxx (Rating: 4)

**Weaknesses:**
- Limited scale (100 puzzles)
- Overlapping error bars
- Complexity vs modest gains

**Questions:**
- Would stronger models benefit?
- Need more ablations

---

## Action Items

**Must Do (Critical):**
1. ✅ Expand to 400 puzzles
2. ✅ Test on ARC-AGI-2
3. ✅ Cross-model evaluation (Claude, Gemini)
4. ✅ Quantify memory reuse
5. ✅ Differentiate from RLAD/NuRL

**Should Do:**
6. Ablations (component justification)
7. Case studies (concept transfer examples)
8. Full prompts in appendix

**Nice to Have:**
9. Domain generalization (or logical argument)

