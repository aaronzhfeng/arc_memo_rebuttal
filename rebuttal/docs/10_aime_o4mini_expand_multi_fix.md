# AIME o4-mini Expand Multi Fix

**Date:** 2025-11-15  
**Status:** 🔍 Root cause identified, fix ready to test  
**Issue:** Empty API responses with `n>1` parameter

---

## Problem

Even with v2 solver (reasoning-friendly prompts), still getting **3/10 empty responses** (2019-II-1, 2019-II-5, 2019-II-7).

---

## Root Cause Discovered

### Issue: o4-mini doesn't support `n>1` properly

**Evidence from token usage:**
```json
{
  "requests": 10,
  "completions": 10  // Should be 30 with n=3!
}
```

With `generation.n=3`, we should get 30 completions total (3 per problem × 10 problems).  
But we only got 10 completions = **o4-mini is ignoring `n=3`** and returning only 1 completion per request.

**What's happening:**
1. OpenAI provider is marked as `supports_multi=True` in model registry
2. Client makes 1 API call with `n=3` parameter
3. o4-mini **silently ignores `n`** and returns only 1 completion
4. Client thinks it got 3 attempts, but actually only got 1
5. That 1 attempt was empty → problem marked as failed

---

## The Fix

### Force `expand_multi=true`

This tells the client to make **3 separate API calls** instead of 1 call with `n=3`:

```bash
python -m concept_mem.data.aime_simple_solver_v2 \
  data=aime_test \
  model=o4_mini \
  generation.n=3 \
  generation.expand_multi=true \  # <-- ADD THIS
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  hydra.run.dir="experiments/aime_test_v3/o4_solve"
```

---

## Why This Should Work

With `expand_multi=true`:
- 10 problems × 3 attempts = **30 separate API calls**
- Each call requests `n=1` (which o4-mini supports)
- If attempt 1 is empty, attempts 2 and 3 get fresh chances
- Should get full 30 completions instead of 10

Expected result: **10/10 problems solved** (vs current 7/10)

---

## Test Command

```bash
cd arc_memo
source .venv/bin/activate

# Run with expand_multi fix
python -m concept_mem.data.aime_simple_solver_v2 \
  data=aime_test \
  model=o4_mini \
  generation.ignore_cache=true \
  generation.max_tokens=4096 \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="experiments/aime_test_v3/o4_solve"

# Check results
cd experiments/aime_test_v3/o4_solve
cat solutions.json | jq '[.[] | select(. != "")] | length'  # Should be 10
cat token_usage.json | jq '.after.["o4-mini-2025-04-16"].completions'  # Should be 30
```

---

## Timeline of Issues

1. **v1 solver:** 6/10 empty (prompt conflict + n>1 issue)
2. **v2 solver:** 3/10 empty (fixed prompts, but n>1 still broken)
3. **v3 (this fix):** Expected 0/10 empty (prompts + expand_multi)

---

## Why We Didn't Catch This Earlier

1. Assumed OpenAI API honors `n` parameter for all models
2. o4-mini **silently ignores** `n>1` (no error, just returns 1)
3. Token usage looked "reasonable" (76K tokens for 10 problems)
4. Only when we checked completions count did we notice (10 instead of 30)

---

## Files Updated

- `rebuttal/RUN_AIME.md` - Added `generation.expand_multi=true` to all o4_mini commands
- This file documents the root cause and fix

---

## Key Insight

**Reasoning models may have API limitations:**
- o4-mini doesn't properly support `n>1` parameter
- Must use `expand_multi=true` to force separate API calls
- Always verify token usage matches expected completions count

---

## Related Documentation

- **Implementation:** [06_aime_implementation.md](06_aime_implementation.md)
- **Pipeline:** [07_aime_pipeline_corrected.md](07_aime_pipeline_corrected.md)
- **Empty response fix:** [08_aime_empty_response_fix.md](08_aime_empty_response_fix.md)
- **Changes summary:** [11_aime_changes_summary.md](11_aime_changes_summary.md)

---

**Status:** ✅ Fix identified, ready for testing  
**Next:** Run test command to verify 10/10 solve rate

