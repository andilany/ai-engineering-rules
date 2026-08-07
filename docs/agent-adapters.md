# Agent adapters

## Codex

Глобальный Universal Core: `$CODEX_HOME/AGENTS.md`, а если переменная не задана — `~/.codex/AGENTS.md`.

На уровне проекта `AGENTS.md` получает managed block, который требует прочитать `.ai-rules/generated.md` и `.ai-rules/project.md`. Остальной пользовательский текст файла сохраняется.

## Claude Code

Глобальный файл: `~/.claude/CLAUDE.md`.

Проектный `CLAUDE.md` получает managed block с импортами:

```text
@.ai-rules/generated.md
@.ai-rules/project.md
```

## Gemini CLI

Глобальный файл: `~/.gemini/GEMINI.md`.

Проектный `GEMINI.md` получает:

```text
@./.ai-rules/generated.md
@./.ai-rules/project.md
```

## Cursor

Проектное правило полностью принадлежит airules и хранится в `.cursor/rules/engineering.mdc`. Если файл с этим именем уже существует и не содержит ownership marker, `airules` отказывается его перезаписывать.

Глобальные Cursor User Rules находятся в Settings, поэтому `bootstrap` только создаёт `~/.ai-rules/cursor-user-rules.txt` для ручной вставки.
