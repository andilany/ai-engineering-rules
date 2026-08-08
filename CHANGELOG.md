# Changelog

## 0.2.2 — 2026-08-08

- Added whole-catalog integrity validation across profiles, required core rules, and every manifest feature mapping.
- Incomplete packaged rule catalogs now report all missing canonical modules in one error instead of failing one module at a time.
- Added regression coverage for missing infrastructure mappings.
- Release validation now includes an installed-package smoke with Docker Compose detection and Cursor-only initialization.

## 0.2.1 — 2026-08-08

- Fixed the published `dev` rule catalog by restoring the missing `rules/infrastructure/` category.
- Restored `infrastructure.docker`, required by the `python-backend` profile.
- No project files or adapter-selection behavior changed.

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
