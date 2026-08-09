# Claude Code

[Русский](../../ru/agents/claude.md) | **English**

## Project integration

Canonical groups are rendered to:

```text
.claude/rules/airules/*.md
```

The root `CLAUDE.md` stays a short managed entrypoint and connects the user-owned `.ai-rules/project.md`.

```bash
airules init --ide claude
airules sync
```

Airules removes stale native files only when they carry its ownership marker and leaves unrelated Claude rules untouched.

## Global bootstrap

```bash
airules bootstrap --ide claude
```

The Universal Core is written to `~/.claude/rules/airules/000-core.md`.
