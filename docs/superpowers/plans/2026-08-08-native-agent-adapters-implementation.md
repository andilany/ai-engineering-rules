# Native Agent Adapters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship airules 0.3.0 with native Cursor, Claude Code, and GitHub Copilot adapters, a compact Codex adapter, safe migration/deletion, updated doctor/bootstrap behavior, and installed-package regression coverage.

**Architecture:** Keep `rules/**/*.md` and `EffectiveRules` canonical, then project the same effective graph into adapter-specific native files. Add a shared native-group renderer and explicit safe deletion planning so adapters can manage multiple owned files without touching unrelated project content.

**Tech Stack:** Python 3.13, Typer, tomlkit, pytest, Markdown/MDC/TOML frontmatter, importlib.resources.

## Global Constraints

- `--ide` supports exactly `codex`, `claude`, `cursor`, `copilot`, `gemini`.
- `.ai-rules/generated.md` remains a complete compiled snapshot.
- `.ai-rules/project.md` remains user-owned and is never overwritten or deleted.
- Native adapters are derived from the same `EffectiveRules` graph.
- Empty thematic groups are not emitted.
- No semantic-scope-to-filesystem-glob inference in 0.3.0.
- Delete only files proven to be airules-owned and only inside adapter-owned prefixes.
- Dry-run performs no writes or deletions.
- Do not modify application code, dependencies, architecture, or Git history.

---

### Task 1: Shared native rule grouping

**Files:**
- Create: `src/ai_rules/adapters/native.py`
- Modify: `tests/test_adapters.py`

**Interfaces:**
- Produces `NativeRuleGroup(key: str, title: str, rules: tuple[RuleDocument, ...])`.
- Produces `group_effective_rules(effective: EffectiveRules) -> tuple[NativeRuleGroup, ...]`.
- Produces `render_group_markdown(group: NativeRuleGroup, effective: EffectiveRules) -> str`.

- [ ] Write tests proving exact group membership, stable group order, empty group omission, severity/effective order preservation, and provenance comments.
- [ ] Run `PYTHONPATH=src pytest tests/test_adapters.py -q` and verify RED.
- [ ] Implement the minimal shared grouping/rendering module.
- [ ] Re-run focused tests and verify GREEN.

### Task 2: Safe multi-file adapter filesystem operations

**Files:**
- Modify: `src/ai_rules/models.py`
- Modify: `src/ai_rules/filesystem.py`
- Modify: `tests/test_filesystem.py`

**Interfaces:**
- Add an explicit planned-delete model separate from `PlannedWrite`.
- Add safe delete application honoring `WriteScope`, dry-run, and ownership validation performed by callers.

- [ ] Write RED tests for dry-run deletion, real deletion, missing-file no-op, and out-of-scope rejection.
- [ ] Implement minimal deletion planning/application without changing existing write semantics.
- [ ] Run focused filesystem tests GREEN.

### Task 3: Cursor native adapter and migration

**Files:**
- Replace behavior in: `src/ai_rules/adapters/cursor.py`
- Modify: `src/ai_rules/project.py`
- Modify: `src/ai_rules/sync.py`
- Modify: `tests/test_adapters.py`
- Modify: `tests/test_sync.py`

**Interfaces:**
- Render expected `.cursor/rules/airules-*.mdc` files from `EffectiveRules`.
- Render `airules-999-project.mdc` as the project-rule bridge.
- Detect and safely delete owned legacy `.cursor/rules/engineering.mdc`.
- Detect and safely delete stale owned `airules-*.mdc` files.

- [ ] Write RED tests for native MDC content, no `../../` generated import, empty-group omission, legacy migration, stale cleanup, unowned-file preservation, and dry-run.
- [ ] Implement Cursor native renderer and sync integration.
- [ ] Run Cursor/sync focused tests GREEN.

### Task 4: Claude Code native modular adapter

**Files:**
- Replace behavior in: `src/ai_rules/adapters/claude.py`
- Modify: `src/ai_rules/project.py`
- Modify: `src/ai_rules/sync.py`
- Modify: `tests/test_adapters.py`
- Modify: `tests/test_sync.py`

**Interfaces:**
- Root `CLAUDE.md` managed block imports only `.ai-rules/project.md`.
- Native canonical groups render to `.claude/rules/airules/*.md`.
- Stale owned native files are safely removed.

- [ ] Write RED tests for short root entrypoint, native grouped rules, no generated snapshot duplication, stale cleanup, user-rule preservation, and dry-run.
- [ ] Implement Claude native renderer and sync integration.
- [ ] Run focused tests GREEN.

### Task 5: GitHub Copilot support

**Files:**
- Create: `src/ai_rules/adapters/copilot.py`
- Modify: `src/ai_rules/ides.py`
- Modify: `src/ai_rules/project.py`
- Modify: `src/ai_rules/sync.py`
- Modify: `src/ai_rules/cli.py` only if help text enumerates IDEs explicitly
- Modify: `tests/test_adapters.py`
- Modify: `tests/test_manifest.py`
- Modify: `tests/test_sync.py`
- Modify: `tests/test_cli_project_commands.py`

**Interfaces:**
- Add `copilot` to `SUPPORTED_IDES`.
- Root `.github/copilot-instructions.md` is a managed entrypoint preserving user text.
- Native groups render to `.github/instructions/airules/*.instructions.md` with `applyTo: "**"`.

- [ ] Write RED tests for IDE normalization/persistence, root Copilot instructions, modular files, ownership, stale cleanup, and `init --ide copilot`.
- [ ] Implement Copilot renderer and project integration.
- [ ] Run focused tests GREEN.

### Task 6: Codex and Gemini adapter audit

**Files:**
- Modify: `src/ai_rules/adapters/codex.py`
- Keep or minimally modify: `src/ai_rules/adapters/gemini.py`
- Modify: `tests/test_adapters.py`

**Interfaces:**
- Codex root `AGENTS.md` remains compact and points to generated + project files.
- Gemini retains its existing imports unless tests reveal a correctness problem.

- [ ] Write/adjust tests enforcing compact Codex entrypoint and Gemini backward compatibility.
- [ ] Make the minimal adapter changes.
- [ ] Run focused tests GREEN.

### Task 7: Doctor for native adapters

**Files:**
- Modify: `src/ai_rules/doctor.py`
- Modify: `tests/test_doctor.py`

**Interfaces:**
- Doctor resolves selected IDEs exactly like sync.
- Doctor compares expected native files, reports missing/outdated/stale/conflicting owned state, and ignores unselected agents.

- [ ] Write RED tests for Cursor, Claude, Copilot, Codex, legacy manifest, stale owned files, and unselected-agent ignore behavior.
- [ ] Implement native adapter doctor checks using shared expected-file renderers.
- [ ] Run doctor tests GREEN.

### Task 8: Bootstrap native updates

**Files:**
- Modify: `src/ai_rules/bootstrap.py`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_cli_bootstrap.py`

**Interfaces:**
- Codex global behavior remains `$CODEX_HOME/AGENTS.md` or `~/.codex/AGENTS.md`.
- Claude universal core renders under `~/.claude/rules/airules/`.
- Cursor helper file behavior remains settings/manual-paste based.
- Copilot universal core renders to `$COPILOT_HOME/copilot-instructions.md` or `~/.copilot/copilot-instructions.md`.
- Gemini behavior remains compatible.

- [ ] Write RED tests for filtered bootstrap across all five supported IDE values.
- [ ] Implement bootstrap paths/rendering safely.
- [ ] Run focused bootstrap tests GREEN.

### Task 9: Release docs, version, and installed-package smoke

**Files:**
- Modify: `README.md`
- Modify: `docs/agent-adapters.md`
- Modify: `docs/manifest.md`
- Modify: `CHANGELOG.md`
- Modify: `pyproject.toml`
- Modify: `src/ai_rules/__init__.py`
- Add/modify tests as needed for installed-resource smoke.

**Interfaces:**
- Version becomes `0.3.0`.
- Documentation explains native adapter outputs and safe migration.

- [ ] Update docs/version only after feature tests are GREEN.
- [ ] Run `PYTHONPATH=src python -m pytest -q` and require zero failures.
- [ ] Run `python -m compileall -q src`.
- [ ] Run CLI help/version smoke.
- [ ] Build/install an isolated package layout and run `airules init`, `sync`, and `doctor` for `cursor`, `claude`, `codex`, and `copilot` from outside the source tree.
- [ ] Verify generated native files and that no unrelated adapters appear.
- [ ] Do not commit, push, merge, or create a PR without separate explicit user authorization.
