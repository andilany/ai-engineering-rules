# Agent adapters

`airules` хранит один canonical rule graph и рендерит его в нативный формат выбранного агента. `.ai-rules/generated.md` остаётся полным IDE-independent snapshot, а `.ai-rules/project.md` — user-owned project-specific source.

## Codex

Глобальный Universal Core: `$CODEX_HOME/AGENTS.md`, а если переменная не задана — `~/.codex/AGENTS.md`.

Проектный `AGENTS.md` получает короткий managed block: Codex должен прочитать `.ai-rules/generated.md` и `.ai-rules/project.md`. `airules` не создаёт `AGENTS.override.md` и не управляет nested `AGENTS.md`.

## Claude Code

Глобальный Universal Core: `~/.claude/rules/airules/000-core.md`.

На уровне проекта canonical groups рендерятся в `.claude/rules/airules/*.md`. Корневой `CLAUDE.md` остаётся коротким managed entrypoint и импортирует только `.ai-rules/project.md`, чтобы generated snapshot не дублировался в контексте.

## Cursor

Проектные canonical groups рендерятся непосредственно в `.cursor/rules/airules-*.mdc` с `alwaysApply: true`. `airules-999-project.mdc` содержит generated projection `.ai-rules/project.md`. Старый owned `.cursor/rules/engineering.mdc` мигрируется и удаляется; чужой файл без ownership marker не трогается.

Глобальные Cursor User Rules находятся в Settings, поэтому `bootstrap` создаёт `~/.ai-rules/cursor-user-rules.txt` для ручной вставки.

## GitHub Copilot

Проектный repository-wide entrypoint: `.github/copilot-instructions.md`. Canonical groups рендерятся в `.github/instructions/airules/*.instructions.md` с `applyTo: "**"`. Project-specific текст из `.ai-rules/project.md` включается в managed block repository-wide instructions при `sync`.

Глобальный Universal Core для Copilot CLI: `$COPILOT_HOME/copilot-instructions.md`, либо `~/.copilot/copilot-instructions.md`.

## Gemini CLI

Глобальный файл: `~/.gemini/GEMINI.md`. Проектный `GEMINI.md` сохраняет thin-adapter модель и импортирует `.ai-rules/generated.md` и `.ai-rules/project.md`.

## Ownership

Native files, имена которых зарезервированы `airules`, содержат `<!-- ai-engineering-rules:owned -->`. `sync` удаляет stale files только при наличии этого marker и только внутри известных adapter directories. User-owned rules не удаляются и не перезаписываются.
