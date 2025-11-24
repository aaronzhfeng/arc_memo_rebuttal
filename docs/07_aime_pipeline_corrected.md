# AIME Pipeline (Corrected)

**Updated:** 2025-11-15  
**Key change:** Two separate API calls (solve, then explain)

---

## ✅ Corrected Pipeline

```
Step 1: o4 solves → Just answers
        python -m concept_mem.data.aime_simple_solver
        Output: solutions.json = {problem_id: "547"}

Step 2: o4 explains → Thought processes
        python -m concept_mem.data.aime_thought_process
        Input: problem + answer
        Output: thought_processes.json = {problem_id: "reasoning..."}

Step 3: gpt41 abstracts → Concepts
        python -m concept_mem.abstraction.analysis_concepts
        (REUSES existing ArcMemo code)
        Output: lessons.json
```

---

## 🔄 Why Two Calls?

**Benefits:**
1. ✅ Clean answer extraction (no regex parsing)
2. ✅ Separate concerns (solve vs explain)
3. ✅ Matches ArcMemo-OE pattern
4. ✅ Richer reasoning (dedicated call)

**Matches ArcMemo:**
```bash
# ArcMemo-OE does same thing:
python -m concept_mem.abstraction.thought_process  # Step 1
python -m concept_mem.abstraction.analysis_concepts # Step 2
```

---

## 📁 Code Reuse

**New code (minimal):**
- `aime_simple_solver.py` (125 lines) - Just get answers
- `aime_thought_process.py` (150 lines) - Generate reasoning

**Reused from ArcMemo:**
- `analysis_concepts.py` - Abstraction (no changes)
- `selection/description/select.py` - Retrieval (no changes)
- `evaluation/driver.py` - If needed for inference

**Total new code: ~275 lines** (vs 1500 before)

---

## Commands

See `arc_memo/experiments/aime_pilot.sh` for updated pipeline.

