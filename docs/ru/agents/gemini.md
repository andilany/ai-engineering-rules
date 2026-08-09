# Gemini CLI

**Русский** | [English](../../en/agents/gemini.md)

## Project integration

При выборе `gemini` airules управляет корневым `GEMINI.md` как thin adapter к `.ai-rules/generated.md` и `.ai-rules/project.md`.

```bash
airules init --ide gemini
airules sync
```

Существующий пользовательский текст сохраняется; airules обновляет только свой managed block.

## Global bootstrap

```bash
airules bootstrap --ide gemini
```

Universal Core записывается в `~/.gemini/GEMINI.md` как managed block.
