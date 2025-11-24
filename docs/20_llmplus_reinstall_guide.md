# Reinstalling llmplus with Per-Request Token Tracking

**Date:** 2025-11-19  
**Status:** ✅ Ready to run

---

## Purpose

We customized `llmplus` to capture per-request token usage (including reasoning tokens) for AIME experiments. Whenever the virtualenv is rebuilt, reinstall `llmplus` from the local fork so that `token_usage.json` continues to log detailed request metadata.

---

## Source of Truth

- **Fork:** <https://github.com/aaronzhfeng/llm_wrapper.git>  
- **Local copy:** `/Users/aaronfeng/Repo/ARC_AGI/llm_wrapper/`

---

## Quick Reinstall (Editable Mode – recommended)

```bash
cd arc_memo
source .venv/bin/activate

# Remove any previously installed wheel
pip uninstall llmplus -y

# Install your local fork in editable mode
cd ../llm_wrapper
pip install -e .

# Sanity check: include_per_request flag should be exposed
cd ../arc_memo
python -c "from llmplus.client import LLMClient; import inspect; sig = inspect.signature(LLMClient.get_token_usage_dict); print('✓ include_per_request parameter:', 'include_per_request' in sig.parameters)"
```

This keeps the development environment linked to your working tree so code tweaks take effect immediately.

---

## Alternative: Install from GitHub Fork

Use this when local changes are committed and pushed.

```bash
cd arc_memo
source .venv/bin/activate

pip uninstall llmplus -y
pip install git+https://github.com/aaronzhfeng/llm_wrapper.git

# Verify install
python -c "from llmplus import ModelTokenUsage; print('✓ llmplus installed from fork')"
```

---

## Modifications in the Fork

1. **`llmplus/model_token_usage.py`**  
   - Adds `per_request_details` list (input, output, reasoning tokens per API call).  
   - Tracks total `reasoning_tokens`.

2. **`llmplus/client.py`**  
   - Adds `include_per_request` parameter to `LLMClient.get_token_usage_dict()`.

3. **`arc_memo/concept_mem/utils/llm_job.py`**  
   - Requests `get_token_usage_dict(include_per_request=True)` so runs automatically persist detailed usage.

---

## Expected `token_usage.json` Structure

```json
{
  "after": {
    "o4-mini-2025-04-16": {
      "input_tokens": 7464,
      "output_tokens": 44636,
      "reasoning_tokens": 42000,
      "requests": 30,
      "completions": 30,
      "per_request_details": [
        {
          "request_num": 1,
          "input_tokens": 248,
          "output_tokens": 1487,
          "reasoning_tokens": 1450,
          "total_tokens": 1735,
          "num_completions": 1
        },
        ...
      ]
    }
  }
}
```

The new `per_request_details` list mirrors the number of API calls, enabling detailed cost analysis and debugging.

---

## Post-Reinstall Validation

```bash
cd arc_memo
source .venv/bin/activate

python -m concept_mem.data.aime_simple_solver_v3 \
  data=aime_test \
  model=o4_mini \
  generation.ignore_cache=true \
  generation.max_tokens=2048 \
  generation.n=3 \
  generation.expand_multi=true \
  hydra.run.dir="experiments/aime_test_v3_with_per_request/o4_solve"

cat experiments/aime_test_v3_with_per_request/o4_solve/token_usage.json \
  | jq '.after."o4-mini-2025-04-16" | keys'
# Expected keys: ["completions", "input_tokens", "output_tokens", "per_request_details", "reasoning_tokens", "requests"]
```

---

## Troubleshooting

- **`include_per_request` missing:** reinstall in editable mode; a cached wheel is probably still active.  
- **No reasoning tokens recorded:** confirm you are using the fork (not the upstream PyPI release).  
- **Hydra output missing `token_usage.json`:** ensure the run finished successfully; partial runs skip aggregation.

---

## Next Steps

- Keep the fork up to date with upstream `llmplus` changes.  
- Consider pushing a PR upstream once the per-request tracking API stabilizes.  
- Automate the verification script inside CI so we detect regressions when upgrading dependencies.


