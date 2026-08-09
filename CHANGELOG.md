# Changelog

## [Unreleased]

- No unreleased changes yet.

## [0.3.2] — 2026-08-09

- Added guided project-specific onboarding: new `.ai-rules/project.md` files start with an explicit incomplete marker and a structured template for project purpose, architecture, workflow, verification, business, operational, and approval constraints.
- `airules init` now prints a ready-to-use prompt for the user's own AI coding agent so repository-specific instructions are completed collaboratively instead of being left as an empty template.
- `airules doctor` now reports `project_rules_incomplete` until the onboarding marker is removed after the user confirms the project instructions.
- Removed the obsolete Cursor global bootstrap helper and `~/.ai-rules/cursor-user-rules.txt`; Cursor is now project-only through `.cursor/rules/airules-*.mdc`, and explicit `bootstrap --ide cursor` points users to `airules init --ide cursor`.
- Removed the obsolete legacy Cursor renderer while retaining safe cleanup of old airules-owned `.cursor/rules/engineering.mdc` files during upgrade/sync.
- Centralized the project instructions template and onboarding status logic so sync and doctor use one contract.
- Shortened the Russian and English README files and moved detailed usage, configuration, project onboarding, CLI, and agent integration guidance into paired `docs/ru/` and `docs/en/` documentation.

## [0.3.1] — 2026-08-08

- Added an interactive `airules init` wizard with detection-based defaults and selective rule families.
- Added the minimal `custom` profile so interactive setup does not pull unrelated backend, data, infrastructure, or authentication rules.
- Added `airules reconfigure` with a destructive-change preview, required confirmation before reset, a fresh setup wizard, and a final apply confirmation.
- Reconfiguration now removes stale airules-owned adapters while preserving unrelated project files and `.ai-rules/project.md`.
- Added `airules uninstall` with an explicit deletion/modification preview and required `[y/N]` confirmation.
- Added `airules uninstall --purge` for explicitly deleting the user-owned `.ai-rules/project.md` file.
- Added `--yes`, `--dry-run`, and `--interactive/--no-interactive` lifecycle controls while preserving existing `--profile` and `--ide` automation workflows.
- Restored the aggregate `SyncResult.changed` compatibility property used by lifecycle and end-to-end callers.
- Fixed Cursor `.mdc` generation so YAML frontmatter starts at the first byte and the airules ownership marker is written after the closing frontmatter delimiter, restoring Cursor rule discovery while preserving safe managed cleanup.

## [0.3.0] — 2026-08-08

- Changed the project license to MIT for the public repository.
- Added enforced release metadata validation via `scripts/check_release.py`.
- Added tag-driven GitHub Release automation with tests, package build, wheel smoke test, and release artifact upload.
- Added the documented release process in `docs/releasing.md`; `CHANGELOG.md` is the single source for GitHub Release notes.
- Removed internal `docs/superpowers/` artifacts and duplicate `docs/releases/` files from the public tree.
- Added native modular adapters for Cursor, Claude Code, and GitHub Copilot.
- Added `copilot` as a repeatable `--ide` target for project init/sync and global bootstrap.
- Cursor now renders thematic `.cursor/rules/airules-*.mdc` files and migrates the old owned `engineering.mdc` adapter.
- Claude now renders `.claude/rules/airules/*.md` and keeps a short root `CLAUDE.md` project-instruction entrypoint.
- Copilot now renders `.github/copilot-instructions.md` plus `.github/instructions/airules/*.instructions.md`.
- Added safe scoped deletion for stale airules-owned native files; unrelated project rules remain untouched.
- Updated doctor to validate selected native adapter file sets, stale rules, and conflicts.
- Updated bootstrap for Claude native user rules and Copilot CLI user-level instructions.

## 0.2.3 — 2026-08-08

- Fixed `airules doctor` to validate only adapters selected by persisted `manifest.ides`.
- Cursor-only projects no longer report Codex, Claude, or Gemini adapters as outdated.
- Preserved legacy behavior: manifests without `ides` still validate all supported adapters.
- Added regression coverage for selective and legacy doctor behavior.

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
