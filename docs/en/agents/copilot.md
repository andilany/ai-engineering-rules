# GitHub Copilot

[Русский](../../ru/agents/copilot.md) | **English**

## Project integration

Repository-wide entrypoint:

```text
.github/copilot-instructions.md
```

Thematic canonical groups:

```text
.github/instructions/airules/*.instructions.md
```

Native files use `applyTo: "**"`. Project-specific content from `.ai-rules/project.md` is included in managed repository instructions during `sync`.

```bash
airules init --ide copilot
airules sync
```

## Global bootstrap

```bash
airules bootstrap --ide copilot
```

Target: `$COPILOT_HOME/copilot-instructions.md` or `~/.copilot/copilot-instructions.md`.
