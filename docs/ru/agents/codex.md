# OpenAI Codex

**Русский** | [English](../../en/agents/codex.md)

## Project integration

При выборе `codex` airules управляет коротким `AGENTS.md` entrypoint в корне проекта. Он направляет Codex к `.ai-rules/generated.md` и `.ai-rules/project.md`, не дублируя весь rule-pack в корневом файле.

```bash
airules init --ide codex
airules sync
```

Существующий пользовательский текст `AGENTS.md` сохраняется; airules изменяет только свой managed block.

## Global bootstrap

```bash
airules bootstrap --ide codex
```

Target: `$CODEX_HOME/AGENTS.md`, либо `~/.codex/AGENTS.md`, если переменная не задана.
