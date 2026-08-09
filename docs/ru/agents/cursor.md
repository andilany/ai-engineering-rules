# Cursor

**Русский** | [English](../../en/agents/cursor.md)

## Project integration

Cursor использует native **Project Rules**:

```text
.cursor/rules/airules-*.mdc
```

```bash
airules init --ide cursor
airules sync
```

Каждый generated `.mdc` начинается с YAML frontmatter; ownership marker находится после закрывающего `---`, чтобы Cursor корректно распознавал metadata.

`airules-999-project.mdc` является generated projection user-owned `.ai-rules/project.md`.

## Global bootstrap

Airules не управляет глобальными Cursor User Rules и больше не создаёт `~/.ai-rules/cursor-user-rules.txt`.

```bash
airules bootstrap --ide cursor
```

завершается понятной ошибкой и предлагает использовать project integration: `airules init --ide cursor`.

## Legacy migration

При `sync` старый `.cursor/rules/engineering.mdc` удаляется только если содержит airules ownership marker. Это временный upgrade-path для проектов старых версий; новые файлы с таким именем airules не создаёт.
