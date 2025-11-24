# AIME Prompt Assets

This directory now stores auto-generated Python modules that mirror the prompt
templates used in both AIME pipelines.  Markdown examples and ad-hoc prompt
builders have been archived for reference under `archive/`.

## Generated Modules

- `generated/aime_prompt_templates.py`  
  Strict o4 → gpt-4.1 pipeline (baseline) templates.
- `generated/aime_2p5_prompt_templates.py`  
  Gemini 2.5 self-reflection pipeline templates.

Each module exposes a `PROMPTS` dictionary keyed by descriptive names.

## Regenerating

```bash
cd arc_memo_rebuttal/prompts
python scripts/export_prompt_templates.py
```

This will refresh both generated modules with the latest strings imported
directly from the `arc_memo` codebase.

## Archived Material

Previously shipped markdown examples and handcrafted prompt builders are now
under `archive/original/`.  They are kept for historical context but are no
longer maintained.
