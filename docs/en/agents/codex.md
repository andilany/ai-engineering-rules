# OpenAI Codex

[Русский](../../ru/agents/codex.md) | **English**

## Project integration

When `codex` is selected, airules manages a short root `AGENTS.md` entrypoint. It directs Codex to `.ai-rules/generated.md` and `.ai-rules/project.md` without duplicating the complete rule pack in the root file.

```bash
airules init --ide codex
airules sync
```

Existing user content in `AGENTS.md` is preserved; airules modifies only its managed block.

## Global bootstrap

```bash
airules bootstrap --ide codex
```

Target: `$CODEX_HOME/AGENTS.md`, or `~/.codex/AGENTS.md` when the environment variable is not set.
