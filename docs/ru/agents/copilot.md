# GitHub Copilot

**Русский** | [English](../../en/agents/copilot.md)

## Project integration

Repository-wide entrypoint:

```text
.github/copilot-instructions.md
```

Тематические canonical groups:

```text
.github/instructions/airules/*.instructions.md
```

Native files используют `applyTo: "**"`. Project-specific содержимое `.ai-rules/project.md` включается в managed repository instructions при `sync`.

```bash
airules init --ide copilot
airules sync
```

## Global bootstrap

```bash
airules bootstrap --ide copilot
```

Target: `$COPILOT_HOME/copilot-instructions.md` или `~/.copilot/copilot-instructions.md`.
