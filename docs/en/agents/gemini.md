# Gemini CLI

[Русский](../../ru/agents/gemini.md) | **English**

## Project integration

When `gemini` is selected, airules manages the root `GEMINI.md` as a thin adapter to `.ai-rules/generated.md` and `.ai-rules/project.md`.

```bash
airules init --ide gemini
airules sync
```

Existing user content is preserved; airules updates only its managed block.

## Global bootstrap

```bash
airules bootstrap --ide gemini
```

The Universal Core is written to `~/.gemini/GEMINI.md` as a managed block.
