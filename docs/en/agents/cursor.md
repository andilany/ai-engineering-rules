# Cursor

[Русский](../../ru/agents/cursor.md) | **English**

## Project integration

Cursor uses native **Project Rules**:

```text
.cursor/rules/airules-*.mdc
```

```bash
airules init --ide cursor
airules sync
```

Every generated `.mdc` starts with YAML frontmatter; the ownership marker is placed after the closing `---` so Cursor can parse rule metadata correctly.

`airules-999-project.mdc` is a generated projection of the user-owned `.ai-rules/project.md`.

## Global bootstrap

Airules does not manage global Cursor User Rules and no longer creates `~/.ai-rules/cursor-user-rules.txt`.

```bash
airules bootstrap --ide cursor
```

fails with clear guidance to use project integration via `airules init --ide cursor`.

## Legacy migration

During `sync`, an old `.cursor/rules/engineering.mdc` is deleted only if it contains the airules ownership marker. This is a temporary upgrade path for older projects; airules never creates new files with that legacy name.
