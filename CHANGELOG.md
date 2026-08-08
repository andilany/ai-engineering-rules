# Changelog

## 0.2.0 — 2026-08-08

- Added repeatable `--ide` selection for `init`, `sync`, and `bootstrap`.
- Persist selected project adapters in `.ai-rules.toml` while keeping legacy manifests backward-compatible.
- Added temporary `sync --ide ...` overrides that do not change persisted IDE selection.
- Prevented unselected existing adapter files from being deleted or rewritten.
- Added IDE validation, ordered de-duplication, filtered Cursor bootstrap notes, and regression coverage.

## 0.1.0 — 2026-08-08

- Added modular canonical engineering rules and profile system.
- Added `airules bootstrap`, `init`, `sync`, `add`, `detect`, `explain`, and `doctor`.
- Added native adapters for Codex, Claude Code, Gemini CLI, and Cursor.
- Added safe managed blocks, atomic scoped writes, dry-run mode, stack detection, and project-owned overrides.
- Added Python/FastAPI/Django, frontend, ML/GPU, security, messaging, data, testing, and infrastructure rules.
