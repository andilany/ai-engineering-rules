# Claude Code

**Русский** | [English](../../en/agents/claude.md)

## Project integration

Canonical groups рендерятся в:

```text
.claude/rules/airules/*.md
```

Корневой `CLAUDE.md` остаётся коротким managed entrypoint и подключает user-owned `.ai-rules/project.md`.

```bash
airules init --ide claude
airules sync
```

Airules удаляет stale native files только при наличии ownership marker и не трогает чужие Claude rules.

## Global bootstrap

```bash
airules bootstrap --ide claude
```

Universal Core записывается в `~/.claude/rules/airules/000-core.md`.
