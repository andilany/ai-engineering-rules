# IDE Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add persistent and per-command IDE selection so airules generates only the requested Codex, Claude, Cursor, and Gemini adapters without deleting unselected adapter files.

**Architecture:** Keep IDE selection as a small domain concept shared by manifest, sync, bootstrap, and CLI. New project manifests persist an explicit ordered list of IDEs; old manifests without the field resolve to all supported IDEs. Project sync accepts an optional temporary override while bootstrap accepts a selected list directly.

**Tech Stack:** Python 3.11+, dataclasses, Typer, tomlkit, pytest.

## Global Constraints

- Supported IDE values are exactly `codex`, `claude`, `cursor`, `gemini`.
- Repeated `--ide` preserves first-seen order and de-duplicates values.
- Unknown IDE values fail before any writes.
- New manifests persist the selected IDE list; manifests without `ides` remain backward-compatible and mean all IDEs.
- Explicit `ides = []` is invalid.
- `sync --ide ...` is temporary and never changes persisted `manifest.ides`.
- Unselected existing adapter files are never deleted, truncated, or rewritten.
- Shared `.ai-rules/generated.md` and `.ai-rules/project.md` are independent of IDE selection.
- Cursor bootstrap never modifies Cursor Settings automatically.
- Do not modify project architecture, dependencies, or Git state as part of this feature.

---

### Task 1: IDE domain and manifest persistence

**Files:**
- Modify: `src/ai_rules/models.py`
- Modify: `src/ai_rules/manifest.py`
- Create: `src/ai_rules/ides.py`
- Modify: `tests/test_manifest.py`

**Interfaces:**
- Produces: `SUPPORTED_IDES: tuple[str, ...]`, `normalize_ides(values: Iterable[str] | None, *, default_all: bool) -> tuple[str, ...]`.
- Produces: `ProjectManifest.ides: list[str] | None`, where `None` represents a legacy manifest with no `ides` field.

- [ ] **Step 1: Write failing manifest/domain tests**

Add tests proving: explicit IDE order round-trips, absent `ides` loads as `None`, explicit empty list raises `ConfigurationError`, duplicates normalize, and invalid names raise before use.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `PYTHONPATH=src pytest tests/test_manifest.py -q`
Expected: FAIL because `ProjectManifest.ides` and IDE normalization do not exist.

- [ ] **Step 3: Implement IDE normalization and manifest field**

Implement `src/ai_rules/ides.py` with the supported tuple and ordered de-duplication. Add `ides` to `ProjectManifest`; load it only when the TOML key exists and render it only when the field is not `None`.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `PYTHONPATH=src pytest tests/test_manifest.py -q`
Expected: PASS.

### Task 2: Project init/sync adapter filtering

**Files:**
- Modify: `src/ai_rules/sync.py`
- Modify: `src/ai_rules/cli.py`
- Modify: `tests/test_sync.py`
- Modify: `tests/test_e2e.py`

**Interfaces:**
- Modify: `init_project(root: Path, profile: str | None, dry_run: bool, ides: tuple[str, ...] | None = None) -> SyncResult`.
- Modify: `sync_project(root: Path, dry_run: bool, ides: tuple[str, ...] | None = None) -> SyncResult`.
- Internal rendering accepts resolved IDEs and plans writes only for selected adapters.

- [ ] **Step 1: Write failing sync tests**

Add tests proving Codex-only init creates shared files plus `AGENTS.md` only; multi-IDE init persists order; normal sync obeys persisted IDEs; temporary Claude override writes Claude without changing manifest; and reduced selection leaves pre-existing unselected files byte-for-byte unchanged.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `PYTHONPATH=src pytest tests/test_sync.py tests/test_e2e.py -q`
Expected: FAIL because init/sync always render all adapters and CLI has no `--ide`.

- [ ] **Step 3: Implement adapter filtering and CLI options**

Resolve init IDEs with `normalize_ides(..., default_all=True)` and persist them. Resolve normal sync from override first, otherwise manifest selection, otherwise all IDEs for legacy manifests. Make Typer `--ide` repeatable for `init` and `sync`, validating through the shared domain function before writes.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `PYTHONPATH=src pytest tests/test_sync.py tests/test_e2e.py -q`
Expected: PASS.

### Task 3: Bootstrap filtering, docs, and regression verification

**Files:**
- Modify: `src/ai_rules/bootstrap.py`
- Modify: `src/ai_rules/cli.py`
- Modify: `tests/test_bootstrap.py`
- Modify: `README.md`
- Modify: `docs/manifest.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Modify: `bootstrap(home: Path, *, codex_home: Path | None, dry_run: bool, ides: tuple[str, ...] | None = None) -> BootstrapResult`.
- `BootstrapResult.cursor_note` is empty when Cursor is not selected.

- [ ] **Step 1: Write failing bootstrap/CLI tests**

Add tests proving Codex-only bootstrap writes only Codex, Cursor-only bootstrap writes only the helper file and returns the Cursor note, multiple selections work, and invalid CLI IDE produces no writes.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `PYTHONPATH=src pytest tests/test_bootstrap.py tests/test_e2e.py -q`
Expected: FAIL because bootstrap always writes all targets.

- [ ] **Step 3: Implement bootstrap filtering and documentation**

Filter planned bootstrap writes by normalized IDE selection. Print the Cursor note only when non-empty. Document persistent `ides`, examples, temporary sync override, backward compatibility, and non-deletion behavior; add v0.2 changelog entry.

- [ ] **Step 4: Run full regression suite**

Run: `PYTHONPATH=src pytest -q`
Expected: all tests PASS with zero failures.

- [ ] **Step 5: Run syntax and CLI smoke checks**

Run: `python -m compileall -q src`
Run: `PYTHONPATH=src python -m ai_rules --help`
Run: `PYTHONPATH=src python -m ai_rules init --help`
Run: `PYTHONPATH=src python -m ai_rules sync --help`
Run: `PYTHONPATH=src python -m ai_rules bootstrap --help`
Expected: exit 0 and each relevant help page contains `--ide`.

- [ ] **Step 6: Publish authorized changes to GitHub dev**

After fresh verification, create one commit on `andilany/ai-engineering-rules:dev` containing the implementation, tests, docs, spec, and plan; move only the `dev` ref and verify key files from GitHub.
