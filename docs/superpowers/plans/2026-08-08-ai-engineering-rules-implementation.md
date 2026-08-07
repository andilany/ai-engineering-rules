# AI Engineering Rules v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a private, installable `airules` CLI that keeps canonical AI engineering rules in one repository, detects project stacks conservatively, composes profiles, and safely generates/synchronizes native instructions for Codex, Claude Code, Cursor, and Gemini CLI without modifying application code or performing Git writes.

**Architecture:** Canonical Markdown rules and TOML profiles live at repository root and are packaged into the CLI wheel as read-only resources. A typed domain layer parses rule metadata, profiles, project manifests, and detection results; pure composition/rendering services create deterministic snapshots and agent adapters; a thin Typer CLI performs filesystem orchestration through explicit safe write helpers and managed blocks. Project-specific guidance remains user-owned in `.ai-rules/project.md`, while generated content is idempotent and versioned.

**Tech Stack:** Python 3.14 for development, `requires-python >=3.13`, `uv`, Hatchling, Typer, tomlkit, Ruff, mypy, Bandit, pytest; stdlib `tomllib`, `dataclasses`, `enum`, `pathlib`, `hashlib`, `json`, and `importlib.resources` for core logic.

## Global Constraints

- Canonical rules are English; repository-facing README/documentation is Russian where practical.
- Existing project reality overrides generic preferences.
- Architecture decisions are never silently made by `airules` or generated rules.
- `airules` must never install application dependencies, migrate package managers, modify application code, create/switch branches, commit, push, create PRs, deploy, or mutate infrastructure.
- All Git writes belong to the user. Implementation work in this repository must not run `git add`, `git commit`, `git push`, branch creation/switch, merge, rebase, reset, clean, tag, or release commands without explicit user approval.
- Existing Poetry/pip/pip-tools/uv projects are preserved; generated rules may recommend `uv` migration but require explicit user approval before a migration.
- New Python projects prefer latest stable Python supported by selected dependencies and `uv`; prerelease dependencies are avoided except the explicit `django-modern-rest` exception.
- Generated adapters must preserve unrelated user-authored content.
- `airules sync` must be idempotent.
- `airules doctor`, `airules explain`, and `airules detect` are read-only.
- Cursor global User Rules are not mutated automatically; `bootstrap` emits a ready-to-paste Cursor universal-core file/instruction because official Cursor global User Rules are managed through Settings.
- Codex global instructions use `$CODEX_HOME/AGENTS.md` when `CODEX_HOME` is set, otherwise `~/.codex/AGENTS.md`.
- Claude Code global instructions use `~/.claude/CLAUDE.md`; project instructions use `./CLAUDE.md` and may import files with `@path` syntax.
- Gemini CLI global instructions use `~/.gemini/GEMINI.md`; project instructions use `./GEMINI.md` and may import files with `@path` syntax.
- Cursor project rules live in `.cursor/rules/*.mdc`; generated project rules use supported MDC frontmatter and referenced files.

---

## Planned File Map

### Packaging and CLI

- `pyproject.toml` — package metadata, dependencies, `airules` console script, Ruff/mypy/pytest/Bandit configuration, Hatchling resource inclusion.
- `src/ai_rules/__init__.py` — package version export.
- `src/ai_rules/__main__.py` — `python -m ai_rules` entry point.
- `src/ai_rules/cli.py` — Typer commands only; delegates to services.
- `src/ai_rules/errors.py` — typed user-facing exceptions and exit-code mapping.

### Domain and resource loading

- `src/ai_rules/models.py` — enums/dataclasses for severities, rules, profiles, detection, manifest, render result, doctor findings.
- `src/ai_rules/resources.py` — resolve packaged `rules/` and `profiles/` through `importlib.resources`.
- `src/ai_rules/rules.py` — parse canonical rule Markdown with TOML frontmatter.
- `src/ai_rules/profiles.py` — parse profile TOML, resolve inheritance, compose module sets, detect cycles/conflicts.
- `src/ai_rules/manifest.py` — parse/write `.ai-rules.toml` with tomlkit and preserve comments/order where possible.
- `src/ai_rules/precedence.py` — deterministic ordering and effective-rule composition.

### Project detection

- `src/ai_rules/detection.py` — conservative stack detection from config/structure only.
- `tests/fixtures/projects/*` — small synthetic projects representing FastAPI, Django, fullstack, ML, and ambiguous cases.

### Safe filesystem generation

- `src/ai_rules/managed_blocks.py` — insert/update/remove only marked sections while preserving surrounding content.
- `src/ai_rules/filesystem.py` — atomic UTF-8 writes, dry-run plans, path safety, no application-code writes.
- `src/ai_rules/rendering.py` — render `.ai-rules/generated.md` from effective canonical rules.
- `src/ai_rules/adapters/base.py` — adapter protocol/common structures.
- `src/ai_rules/adapters/codex.py` — `AGENTS.md` managed block.
- `src/ai_rules/adapters/claude.py` — `CLAUDE.md` imports.
- `src/ai_rules/adapters/gemini.py` — `GEMINI.md` imports.
- `src/ai_rules/adapters/cursor.py` — `.cursor/rules/engineering.mdc`.

### Application services

- `src/ai_rules/project.py` — repository-root resolution and project layout paths.
- `src/ai_rules/sync.py` — init/add/sync orchestration using pure components.
- `src/ai_rules/bootstrap.py` — safe global universal-core installation/reporting.
- `src/ai_rules/doctor.py` — read-only diagnostics.
- `src/ai_rules/explain.py` — read-only active-rule provenance output.

### Canonical content

- `rules/**.md` — canonical rules with TOML frontmatter.
- `profiles/*.toml` — initial profile definitions.
- `adapters/README.md` — documentation of native agent mapping, not runtime duplicated rules.

### Documentation

- `README.md` — installation, quick start, commands, safety model, agent support.
- `CHANGELOG.md` — initial v0.1.0 entry.
- `PRIVATE.md` — private-repository/distribution note and no-upstream-copy statement.
- `docs/manifest.md` — `.ai-rules.toml` schema and manual editing.
- `docs/rules-authoring.md` — canonical rule frontmatter and severity guidance.
- `docs/agent-adapters.md` — Codex/Claude/Gemini/Cursor specifics and limitations.

---

### Task 1: Package Skeleton, Quality Gates, and Typed Domain Models

**Files:**
- Create: `pyproject.toml`
- Create: `src/ai_rules/__init__.py`
- Create: `src/ai_rules/__main__.py`
- Create: `src/ai_rules/cli.py`
- Create: `src/ai_rules/errors.py`
- Create: `src/ai_rules/models.py`
- Create: `tests/test_cli_smoke.py`
- Create: `tests/test_models.py`

**Interfaces:**
- Produces `RuleSeverity`, `DetectionConfidence`, `RuleDocument`, `ProfileDefinition`, `Detection`, `ProjectManifest`, `EffectiveRules`, `PlannedWrite`, and `DoctorFinding` dataclasses/enums.
- Produces Typer app `ai_rules.cli:app` and console command `airules`.
- Later tasks import all domain types from `ai_rules.models` rather than redefining them.

- [ ] **Step 1: Add a failing CLI smoke test**

Create `tests/test_cli_smoke.py`:

```python
from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner()


def test_cli_exposes_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "airules" in result.stdout
```

- [ ] **Step 2: Add failing model tests**

Create `tests/test_models.py`:

```python
from ai_rules.models import DetectionConfidence, RuleSeverity


def test_rule_severity_order_is_explicit() -> None:
    assert RuleSeverity.REQUIRED.rank > RuleSeverity.PREFERRED.rank
    assert RuleSeverity.PREFERRED.rank > RuleSeverity.CONDITIONAL.rank
    assert RuleSeverity.CONDITIONAL.rank > RuleSeverity.OPTIONAL.rank
    assert RuleSeverity.USER_DECISION.rank == RuleSeverity.PREFERRED.rank


def test_detection_confidence_values_are_stable() -> None:
    assert [item.value for item in DetectionConfidence] == [
        "detected",
        "probable",
        "not_detected",
    ]
```

- [ ] **Step 3: Run tests and verify collection/import failure**

Run:

```bash
uv run pytest tests/test_cli_smoke.py tests/test_models.py -q
```

Expected: FAIL because package/modules do not exist.

- [ ] **Step 4: Create package metadata and quality configuration**

Create `pyproject.toml` with this functional shape:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ai-engineering-rules"
version = "0.1.0"
description = "Private reusable engineering rules for AI coding agents"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
  "tomlkit",
  "typer",
]

[project.scripts]
airules = "ai_rules.cli:app"

[dependency-groups]
dev = [
  "bandit",
  "mypy",
  "pytest",
  "ruff",
]

[tool.hatch.build.targets.wheel]
packages = ["src/ai_rules"]

[tool.hatch.build.targets.wheel.force-include]
"rules" = "ai_rules/resources/rules"
"profiles" = "ai_rules/resources/profiles"

[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "ASYNC", "S", "RUF"]
ignore = ["S101"]

[tool.mypy]
python_version = "3.13"
strict = true
packages = ["ai_rules"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"

[tool.bandit]
exclude_dirs = ["tests"]
```

Then run:

```bash
uv sync
```

Expected: `.venv` and `uv.lock` are created; only dependency metadata changes.

- [ ] **Step 5: Implement minimal package and typed models**

Create `src/ai_rules/__init__.py`:

```python
__version__ = "0.1.0"
```

Create `src/ai_rules/__main__.py`:

```python
from ai_rules.cli import app

if __name__ == "__main__":
    app()
```

Create `src/ai_rules/models.py` with the exact public API:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class RuleSeverity(StrEnum):
    REQUIRED = "required"
    USER_DECISION = "user_decision"
    PREFERRED = "preferred"
    CONDITIONAL = "conditional"
    OPTIONAL = "optional"

    @property
    def rank(self) -> int:
        return {
            self.REQUIRED: 50,
            self.USER_DECISION: 40,
            self.PREFERRED: 40,
            self.CONDITIONAL: 30,
            self.OPTIONAL: 20,
        }[self]


class DetectionConfidence(StrEnum):
    DETECTED = "detected"
    PROBABLE = "probable"
    NOT_DETECTED = "not_detected"


@dataclass(frozen=True, slots=True)
class RuleDocument:
    id: str
    title: str
    severity: RuleSeverity
    scopes: tuple[str, ...]
    body: str
    source: Path


@dataclass(frozen=True, slots=True)
class ProfileDefinition:
    name: str
    description: str
    modules: tuple[str, ...]
    extends: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Detection:
    key: str
    confidence: DetectionConfidence
    evidence: tuple[str, ...] = ()


@dataclass(slots=True)
class ProjectManifest:
    version: int = 1
    profile: str = ""
    rules_version: str = "0.1.0"
    extra_profiles: list[str] = field(default_factory=list)
    include_modules: list[str] = field(default_factory=list)
    exclude_modules: list[str] = field(default_factory=list)
    flags: dict[str, dict[str, bool]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EffectiveRules:
    rules: tuple[RuleDocument, ...]
    provenance: dict[str, tuple[str, ...]]


@dataclass(frozen=True, slots=True)
class PlannedWrite:
    path: Path
    content: str
    changed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class DoctorFinding:
    level: str
    code: str
    message: str
    path: Path | None = None
```

Create `src/ai_rules/cli.py` with a Typer app exposing `version`; later tasks add commands.

- [ ] **Step 6: Re-run smoke/model tests**

Run:

```bash
uv run pytest tests/test_cli_smoke.py tests/test_models.py -q
```

Expected: PASS.

- [ ] **Step 7: Run initial quality gates**

Run:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv run bandit -c pyproject.toml -r src
```

Expected: PASS.

---

### Task 2: Canonical Rule Parser and Packaged Resource Loading

**Files:**
- Create: `src/ai_rules/resources.py`
- Create: `src/ai_rules/rules.py`
- Create: `tests/test_resources.py`
- Create: `tests/test_rules.py`
- Create: `rules/core/agent-behavior.md`

**Interfaces:**
- `resource_root(kind: Literal["rules", "profiles"]) -> Traversable`
- `parse_rule_text(text: str, *, source: Path) -> RuleDocument`
- `load_rules(root: Traversable | Path | None = None) -> dict[str, RuleDocument]`

- [ ] **Step 1: Write failing resource/parser tests**

Create a rule fixture in the test body:

```python
RULE_TEXT = """+++
id = "core.agent-behavior"
title = "Agent Behavior"
severity = "required"
scopes = ["core"]
+++
# Agent Behavior

- Preserve project intent.
"""
```

Tests:

```python
def test_parse_rule_text_reads_toml_frontmatter(tmp_path: Path) -> None:
    rule = parse_rule_text(RULE_TEXT, source=tmp_path / "rule.md")

    assert rule.id == "core.agent-behavior"
    assert rule.severity is RuleSeverity.REQUIRED
    assert rule.scopes == ("core",)
    assert "Preserve project intent" in rule.body


def test_parse_rule_rejects_missing_frontmatter(tmp_path: Path) -> None:
    with pytest.raises(RuleFormatError):
        parse_rule_text("# no metadata", source=tmp_path / "bad.md")


def test_load_rules_rejects_duplicate_ids(tmp_path: Path) -> None:
    # create two files with the same id
    ...
```

`tests/test_resources.py` asserts root-level source checkout can load `rules/` and installed-package resource fallback can be monkeypatched.

- [ ] **Step 2: Run parser tests and verify failure**

Run:

```bash
uv run pytest tests/test_rules.py tests/test_resources.py -q
```

Expected: FAIL because loader/parser are missing.

- [ ] **Step 3: Implement typed rule errors**

Add to `src/ai_rules/errors.py`:

```python
class AirulesError(Exception):
    exit_code = 2


class RuleFormatError(AirulesError):
    pass


class DuplicateRuleError(AirulesError):
    pass
```

- [ ] **Step 4: Implement parser**

`parse_rule_text()` must:

1. require opening `+++` on line 1;
2. find the next `+++` delimiter;
3. parse only the enclosed TOML using `tomllib.loads`;
4. require exactly these metadata keys in v1: `id`, `title`, `severity`, `scopes`;
5. reject unknown severity values through `RuleSeverity`;
6. require non-empty body;
7. normalize body to exactly one trailing newline;
8. never execute/import rule content.

- [ ] **Step 5: Implement resource loader**

`resource_root()` first checks the repository checkout relative to package path:

```python
Path(__file__).resolve().parents[2] / kind
```

If it does not exist, use:

```python
files("ai_rules").joinpath("resources", kind)
```

`load_rules()` recursively loads only `*.md`, sorts by path before parsing, rejects duplicate IDs, and returns a dict keyed by rule ID.

- [ ] **Step 6: Add initial canonical core rule**

Create `rules/core/agent-behavior.md`:

```markdown
+++
id = "core.agent-behavior"
title = "Agent Behavior"
severity = "required"
scopes = ["core"]
+++
# Agent Behavior

- Understand the relevant existing code, configuration, tests, and project documentation before changing behavior.
- Prefer the smallest change that fully solves the user request.
- Existing project architecture, conventions, and explicit user decisions override generic engineering preferences.
```

- [ ] **Step 7: Run parser/resource tests**

Run:

```bash
uv run pytest tests/test_rules.py tests/test_resources.py -q
```

Expected: PASS.

---

### Task 3: Profile Loading, Inheritance, and Composition

**Files:**
- Create: `src/ai_rules/profiles.py`
- Create: `tests/test_profiles.py`
- Create: `profiles/python-backend.toml`
- Create: `profiles/fastapi-backend.toml`
- Create: `profiles/django-backend.toml`
- Create: `profiles/ml-gpu-service.toml`
- Create: `profiles/frontend-nextjs.toml`
- Create: `profiles/fullstack-python.toml`

**Interfaces:**
- `load_profiles(root: Traversable | Path | None = None) -> dict[str, ProfileDefinition]`
- `resolve_profile_modules(name: str, profiles: Mapping[str, ProfileDefinition]) -> tuple[str, ...]`
- `compose_profile_names(primary: str, extras: Sequence[str], profiles: Mapping[str, ProfileDefinition]) -> tuple[str, ...]`

- [ ] **Step 1: Write failing profile tests**

Create profile fixtures and assert:

```python
def test_profile_inheritance_is_deterministic() -> None:
    profiles = {
        "base": ProfileDefinition("base", "", ("core.agent-behavior",)),
        "child": ProfileDefinition("child", "", ("backend.fastapi",), ("base",)),
    }

    assert resolve_profile_modules("child", profiles) == (
        "core.agent-behavior",
        "backend.fastapi",
    )


def test_profile_cycle_is_rejected() -> None:
    ...


def test_unknown_parent_is_rejected() -> None:
    ...
```

Also assert every shipped profile file loads and has a unique `name`.

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
uv run pytest tests/test_profiles.py -q
```

Expected: FAIL because profile loader/resolver do not exist.

- [ ] **Step 3: Add profile exceptions**

Create `ProfileError`, `UnknownProfileError`, `ProfileCycleError`, `UnknownRuleReferenceError` in `errors.py`.

- [ ] **Step 4: Implement `load_profiles()`**

Each file uses this exact schema:

```toml
name = "fastapi-backend"
description = "Python backend with FastAPI defaults."
extends = ["python-backend"]
modules = [
  "backend.fastapi",
  "backend.pydantic",
  "backend.uvicorn-asgi",
]
```

Reject unknown keys, empty names, duplicate names, and non-string module entries.

- [ ] **Step 5: Implement inheritance resolution**

Use DFS with `visiting` and `resolved` sets. Parents are resolved left-to-right, then local modules. Deduplicate by first occurrence to preserve stable order.

- [ ] **Step 6: Add initial profile files**

At this task, only reference modules already available or create minimal placeholder *rule files with real final semantics* for profile references required by tests. Do not create empty placeholder modules. Full rule content is expanded in Tasks 10–11.

Initial intended composition:

```text
python-backend
  core.*
  languages.python
  backend.async-python
  quality.*
  security.*

fastapi-backend extends python-backend
  backend.fastapi
  backend.pydantic
  backend.uvicorn-asgi
  data.sqlalchemy
  data.alembic

django-backend extends python-backend
  backend.django
  backend.django-modern-rest
  backend.msgspec
  data.django-orm
  data.django-migrations

ml-gpu-service extends fastapi-backend
  ml.gpu-cuda
  ml.vram
  ml.batching
  ml.pipelines

frontend-nextjs
  frontend.typescript/react/nextjs/etc.

fullstack-python extends fastapi-backend + frontend-nextjs
```

- [ ] **Step 7: Run profile tests**

Run:

```bash
uv run pytest tests/test_profiles.py -q
```

Expected: PASS.

---

### Task 4: Project Manifest Schema and Stable Round-Trip

**Files:**
- Create: `src/ai_rules/manifest.py`
- Create: `tests/test_manifest.py`

**Interfaces:**
- `load_manifest(path: Path) -> ProjectManifest`
- `dump_manifest(manifest: ProjectManifest) -> str`
- `save_manifest(path: Path, manifest: ProjectManifest) -> None` (temporary direct write; Task 6 replaces orchestration with safe filesystem planning)
- `new_manifest(profile: str, flags: Mapping[str, Mapping[str, bool]] | None = None) -> ProjectManifest`

- [ ] **Step 1: Write failing manifest tests**

Test exact supported top-level keys and nested boolean tables:

```python
def test_manifest_round_trip_preserves_values(tmp_path: Path) -> None:
    manifest = ProjectManifest(
        profile="fastapi-backend",
        rules_version="0.1.0",
        extra_profiles=["ml-gpu-service"],
        flags={
            "language": {"python": True},
            "backend": {"fastapi": True, "django": False},
        },
    )
    text = dump_manifest(manifest)
    path = tmp_path / ".ai-rules.toml"
    path.write_text(text, encoding="utf-8")

    assert load_manifest(path) == manifest
```

Additional tests:
- schema version other than `1` is rejected;
- unknown top-level scalar is rejected;
- nested values must be bool;
- `include_modules` and `exclude_modules` may not contain duplicates;
- same rule in both include/exclude is rejected;
- invalid/empty primary profile is rejected.

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
uv run pytest tests/test_manifest.py -q
```

Expected: FAIL.

- [ ] **Step 3: Implement schema validation**

Supported scalars/arrays:

```text
version
profile
rules_version
extra_profiles
include_modules
exclude_modules
```

All other TOML tables are interpreted as technology flag groups and must contain only boolean leaves in v1.

- [ ] **Step 4: Implement deterministic writer**

Use `tomlkit.document()` and emit keys in the exact order above, then flag groups alphabetically. Within each group sort flags alphabetically. This ensures generated manifests are stable even if input order varies.

- [ ] **Step 5: Run manifest tests**

Run:

```bash
uv run pytest tests/test_manifest.py -q
```

Expected: PASS.

---

### Task 5: Conservative Stack Detection

**Files:**
- Create: `src/ai_rules/detection.py`
- Create fixtures under `tests/fixtures/projects/`
- Create: `tests/test_detection.py`

**Interfaces:**
- `detect_stack(project_root: Path) -> tuple[Detection, ...]`
- `suggest_profiles(detections: Sequence[Detection]) -> tuple[str, ...]`
- Detection never executes project code, imports application modules, reads `.env` values, or shells out.

- [ ] **Step 1: Create synthetic fixture projects**

Create minimal files only:

```text
tests/fixtures/projects/fastapi/pyproject.toml
tests/fixtures/projects/fastapi/alembic.ini
tests/fixtures/projects/django/pyproject.toml
tests/fixtures/projects/django/manage.py
tests/fixtures/projects/fullstack/package.json
tests/fixtures/projects/ml/pyproject.toml
tests/fixtures/projects/ml/Dockerfile
tests/fixtures/projects/ambiguous/docker-compose.yml
```

FastAPI fixture dependencies include `fastapi`, `sqlalchemy`, `alembic`, `aio-pika`, `redis`. Django fixture includes `django`, `django-modern-rest`, `msgspec`. Fullstack fixture uses `next`, `react`, `typescript`. ML fixture includes a CUDA image marker and Python ML dependency.

- [ ] **Step 2: Write failing detector tests**

Tests:

```python
def test_fastapi_fixture_detects_stack() -> None:
    detections = {item.key: item for item in detect_stack(FIXTURES / "fastapi")}

    assert detections["python"].confidence is DetectionConfidence.DETECTED
    assert detections["fastapi"].confidence is DetectionConfidence.DETECTED
    assert detections["postgresql"].confidence is DetectionConfidence.PROBABLE
    assert detections["rabbitmq"].confidence is DetectionConfidence.DETECTED
    assert "fastapi-backend" in suggest_profiles(tuple(detections.values()))
```

Additional tests:
- Django suggests `django-backend`;
- Next.js suggests `frontend-nextjs`;
- ML/CUDA can suggest `ml-gpu-service` only with strong evidence;
- ambiguous Docker/Compose alone does not silently select a backend profile;
- detector ignores `.env` even if it contains stack-looking strings;
- monkeypatch `subprocess.run` and `__import__` sentinels if useful to prove no execution path occurs.

- [ ] **Step 3: Run detector tests and verify failure**

Run:

```bash
uv run pytest tests/test_detection.py -q
```

Expected: FAIL.

- [ ] **Step 4: Implement safe file readers**

Use `tomllib` for `pyproject.toml`, `json` for `package.json`, `Path.exists()` for markers, and bounded UTF-8 reads for config text. Never follow symlinks outside project root during detection.

Dependencies are normalized from:
- `[project].dependencies`;
- standard optional/dependency-group TOML tables if present;
- Poetry dependency tables when present;
- package.json `dependencies` and `devDependencies`.

- [ ] **Step 5: Implement confidence/evidence rules**

Examples:

```text
python DETECTED    -> pyproject Python dependency metadata or Python package layout
fastapi DETECTED   -> FastAPI dependency
django DETECTED    -> Django dependency +/or manage.py
postgresql PROBABLE -> SQLAlchemy/Django + postgres driver/compose marker
rabbitmq DETECTED  -> aio-pika/aiormq or rabbitmq compose image
redis DETECTED     -> redis dependency or redis compose image
nextjs DETECTED    -> next dependency
cuda DETECTED      -> CUDA base image or CUDA dependency marker
ml PROBABLE/DETECTED -> known ML dependency markers
```

Every positive/probable detection includes evidence strings naming file and marker, never secret values.

- [ ] **Step 6: Implement profile suggestion**

Rules:
- FastAPI detected → `fastapi-backend`;
- Django detected → `django-backend`;
- Next.js detected → `frontend-nextjs`;
- strong ML + CUDA → `ml-gpu-service`;
- Python only → `python-backend`;
- FastAPI + Next.js → prefer `fullstack-python` as a suggestion but report component evidence;
- multiple incompatible backend detections → return multiple suggestions and require user choice in `init`.

- [ ] **Step 7: Run detector tests**

Run:

```bash
uv run pytest tests/test_detection.py -q
```

Expected: PASS.

---

### Task 6: Managed Blocks and Safe Atomic Filesystem Writes

**Files:**
- Create: `src/ai_rules/managed_blocks.py`
- Create: `src/ai_rules/filesystem.py`
- Create: `tests/test_managed_blocks.py`
- Create: `tests/test_filesystem.py`

**Interfaces:**
- `render_managed_block(body: str) -> str`
- `replace_managed_block(existing: str, body: str) -> str`
- `plan_write(path: Path, content: str, *, allowed_root: Path, dry_run: bool) -> PlannedWrite`
- `apply_write(plan: PlannedWrite) -> None`
- `ensure_allowed_path(path: Path, allowed_root: Path) -> None`

- [ ] **Step 1: Write failing managed-block tests**

Constants:

```python
START = "<!-- ai-engineering-rules:start -->"
END = "<!-- ai-engineering-rules:end -->"
```

Tests assert:
- no existing block → one block appended after existing content;
- existing block → only block contents replaced;
- text before/after block remains byte-for-byte except normalized final newline;
- duplicate/malformed start/end markers are rejected rather than guessed;
- second replacement with the same body produces identical text.

- [ ] **Step 2: Write failing safe-filesystem tests**

Tests assert:
- paths under `allowed_root` may be planned;
- `../escape` is rejected;
- a symlink inside project pointing outside is rejected;
- unchanged content results in `changed=False`;
- `dry_run=True` never creates/modifies files;
- actual writes use same-directory temp + `os.replace` and result in complete UTF-8 text.

- [ ] **Step 3: Run tests and verify failure**

Run:

```bash
uv run pytest tests/test_managed_blocks.py tests/test_filesystem.py -q
```

Expected: FAIL.

- [ ] **Step 4: Implement managed blocks**

`replace_managed_block()` must fail if:
- more than one START/END exists;
- only one boundary exists;
- END precedes START.

When adding a block to a non-empty file, preserve all existing content and add exactly two newlines before START.

- [ ] **Step 5: Implement path safety and atomic writes**

Resolve `allowed_root` and target parent. Reject targets whose resolved parent escapes root. Refuse to overwrite symlinks for airules-owned/generated files.

Atomic write algorithm:

```python
fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
# write UTF-8 + fsync
os.replace(temp_name, path)
```

Cleanup the temp file in `finally` when replace does not occur.

- [ ] **Step 6: Run managed/filesystem tests**

Run:

```bash
uv run pytest tests/test_managed_blocks.py tests/test_filesystem.py -q
```

Expected: PASS.

---

### Task 7: Effective Rule Precedence and Canonical Snapshot Rendering

**Files:**
- Create: `src/ai_rules/precedence.py`
- Create: `src/ai_rules/rendering.py`
- Create: `tests/test_precedence.py`
- Create: `tests/test_rendering.py`

**Interfaces:**
- `compose_effective_rules(manifest: ProjectManifest, rules: Mapping[str, RuleDocument], profiles: Mapping[str, ProfileDefinition]) -> EffectiveRules`
- `render_generated_markdown(effective: EffectiveRules, *, rules_version: str) -> str`

- [ ] **Step 1: Write failing precedence tests**

Tests assert:
- primary profile modules load;
- extra profiles append stable modules;
- `include_modules` append explicit modules;
- `exclude_modules` remove only non-REQUIRED rules;
- trying to exclude a REQUIRED core/security rule raises `RequiredRuleExclusionError`;
- false technology flag does **not** silently remove a profile module (manifest profile is an explicit choice; flags primarily document/detect stack);
- unknown included/excluded module raises `UnknownRuleReferenceError`;
- duplicate modules are deduplicated by ID;
- provenance records profile/include origins.

- [ ] **Step 2: Run precedence tests and verify failure**

Run:

```bash
uv run pytest tests/test_precedence.py -q
```

Expected: FAIL.

- [ ] **Step 3: Implement composition**

Composition order:

```text
resolved primary profile
resolved extra profiles in manifest order
explicit include_modules in manifest order
```

Then apply explicit excludes except REQUIRED. Sort final rendered sections by:
1. severity rank descending;
2. first composition order;
3. rule ID for deterministic tiebreak.

Do not infer new architecture modules during composition.

- [ ] **Step 4: Write failing render test**

Expected generated file header includes:

```markdown
<!-- generated by ai-engineering-rules; do not edit -->
# Active AI Engineering Rules

Rules version: `0.1.0`
```

Sections:

```markdown
## REQUIRED
### Rule Title (`rule.id`)
...

## USER_DECISION
...
```

Provenance is included in a compact HTML comment beneath each rule:

```markdown
<!-- source: profile:fastapi-backend -->
```

- [ ] **Step 5: Implement snapshot rendering**

Do not inject project-specific text into the generated file. Normalize to one trailing newline. Rendering the same `EffectiveRules` twice must be byte-identical.

- [ ] **Step 6: Run precedence/render tests**

Run:

```bash
uv run pytest tests/test_precedence.py tests/test_rendering.py -q
```

Expected: PASS.

---

### Task 8: Native Agent Adapters

**Files:**
- Create: `src/ai_rules/adapters/__init__.py`
- Create: `src/ai_rules/adapters/base.py`
- Create: `src/ai_rules/adapters/codex.py`
- Create: `src/ai_rules/adapters/claude.py`
- Create: `src/ai_rules/adapters/gemini.py`
- Create: `src/ai_rules/adapters/cursor.py`
- Create: `tests/test_adapters.py`

**Interfaces:**

```python
class AgentAdapter(Protocol):
    name: str
    project_path: Path

    def render_project_content(self) -> str: ...
```

Concrete helpers:
- `codex_managed_body() -> str`
- `claude_managed_body() -> str`
- `gemini_managed_body() -> str`
- `cursor_rule_content() -> str`

- [ ] **Step 1: Write failing adapter tests**

Codex managed body must tell the agent to read:

```text
.ai-rules/generated.md
.ai-rules/project.md
```

and state project-specific instructions override generic preferences.

Claude body must contain:

```text
@.ai-rules/generated.md
@.ai-rules/project.md
```

Gemini body must contain relative imports:

```text
@./.ai-rules/generated.md
@./.ai-rules/project.md
```

Cursor file uses:

```yaml
---
description: Shared engineering rules for this project
alwaysApply: true
---
```

and instructs the agent to read both project files. It also includes an ownership marker:

```text
<!-- ai-engineering-rules:owned -->
```

- [ ] **Step 2: Run adapter tests and verify failure**

Run:

```bash
uv run pytest tests/test_adapters.py -q
```

Expected: FAIL.

- [ ] **Step 3: Implement base adapter contract**

Use a frozen dataclass for `RenderedAdapter`:

```python
@dataclass(frozen=True, slots=True)
class RenderedAdapter:
    agent: str
    relative_path: Path
    content: str
    managed_block: bool
```

- [ ] **Step 4: Implement Codex/Claude/Gemini project bodies**

`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are mixed-ownership files. Adapter helpers return **managed body only**, and sync uses `replace_managed_block(existing, body)`.

Do not duplicate the entire generated snapshot into these files.

- [ ] **Step 5: Implement Cursor owned file**

The Cursor file is fully generated because `.cursor/rules/engineering.mdc` is a dedicated airules path. If it exists without the ownership marker, sync must refuse to overwrite it and emit a conflict.

- [ ] **Step 6: Run adapter tests**

Run:

```bash
uv run pytest tests/test_adapters.py -q
```

Expected: PASS.

---

### Task 9: Project Init, Sync, Add, Explain, and Doctor Services + CLI

**Files:**
- Create: `src/ai_rules/project.py`
- Create: `src/ai_rules/sync.py`
- Create: `src/ai_rules/explain.py`
- Create: `src/ai_rules/doctor.py`
- Modify: `src/ai_rules/cli.py`
- Create: `tests/test_project.py`
- Create: `tests/test_sync.py`
- Create: `tests/test_explain.py`
- Create: `tests/test_doctor.py`
- Create: `tests/test_cli_project_commands.py`

**Interfaces:**
- `ProjectLayout.from_root(root: Path) -> ProjectLayout`
- `initialize_project(root: Path, *, profile: str | None, dry_run: bool = False) -> SyncReport`
- `sync_project(root: Path, *, dry_run: bool = False) -> SyncReport`
- `add_selection(root: Path, selection: str, *, dry_run: bool = False) -> SyncReport`
- `explain_project(root: Path) -> str`
- `doctor_project(root: Path) -> tuple[DoctorFinding, ...]`

- [ ] **Step 1: Write failing project-layout tests**

`ProjectLayout` paths are exactly:

```text
manifest        .ai-rules.toml
generated       .ai-rules/generated.md
project         .ai-rules/project.md
codex           AGENTS.md
claude          CLAUDE.md
gemini          GEMINI.md
cursor          .cursor/rules/engineering.mdc
```

Root must be existing directory. Layout does not depend on Git being initialized.

- [ ] **Step 2: Write failing `initialize_project` tests**

Given a pre-existing project with:

```text
AGENTS.md = "# Existing Codex instructions\n"
CLAUDE.md = "# Existing Claude instructions\n"
GEMINI.md = "# Existing Gemini instructions\n"
```

After initialize:
- existing text remains;
- each mixed file has exactly one managed block;
- `.ai-rules/project.md` is created only if absent with a short editable template;
- `.ai-rules/generated.md` is generated;
- `.ai-rules.toml` exists;
- Cursor owned file exists;
- running initialize/sync twice is idempotent.

If no profile argument:
- exactly one high-confidence suggestion → use it;
- zero → fail with explicit `--profile` guidance;
- multiple incompatible backend suggestions → fail with choices; do not guess.

- [ ] **Step 3: Write failing sync/add tests**

`sync_project()`:
- requires manifest;
- recomposes and updates generated/adapters;
- never overwrites `.ai-rules/project.md`;
- preserves external user text in mixed adapter files;
- reports changed/unchanged paths.

`add_selection()`:
- if selection is a profile, append to `extra_profiles` unless it is the primary/already present;
- if selection is an exact rule ID, append to `include_modules` unless already represented;
- unknown selection fails with nearest exact available names listed, not fuzzy auto-selection;
- after manifest update, runs sync;
- adding architecture/Kubernetes rule changes guidance only.

- [ ] **Step 4: Run project/sync tests and verify failure**

Run:

```bash
uv run pytest tests/test_project.py tests/test_sync.py -q
```

Expected: FAIL.

- [ ] **Step 5: Implement project layout and reports**

Add `SyncReport` to `models.py`:

```python
@dataclass(frozen=True, slots=True)
class SyncReport:
    writes: tuple[PlannedWrite, ...]
    profile: str
    effective_rule_count: int

    @property
    def changed_count(self) -> int:
        return sum(write.changed for write in self.writes)
```

`ProjectLayout` owns all paths and is the only place orchestration derives target paths.

- [ ] **Step 6: Implement init/sync/add orchestration**

Use loader → manifest → composition → render → adapter render → safe write planning.

For initialization template:

```markdown
# Project-Specific AI Rules

Add project architecture, domain constraints, exceptions, and local conventions here.
This file is user-owned and is never overwritten by `airules sync`.
```

Before mutating any file, compute **all** plans and conflicts. If any conflict/path-safety error occurs, apply no writes. Then apply plans in deterministic path order.

- [ ] **Step 7: Write failing explain tests**

`explain_project()` output includes:

```text
Profile: fastapi-backend
Rules version: 0.1.0

REQUIRED
  core.agent-behavior <- profile:python-backend
...
USER_DECISION
...
```

A rule with multiple provenance entries lists all of them.

- [ ] **Step 8: Implement explain service**

Read-only: load manifest/resources and compose. Never call write helpers.

- [ ] **Step 9: Write failing doctor tests**

Doctor findings cover:
- missing manifest → ERROR;
- invalid manifest → ERROR;
- missing generated snapshot → ERROR;
- generated snapshot differs → STALE;
- missing project.md → WARN;
- mixed adapter missing managed block → STALE;
- Cursor file missing/foreign → STALE/CONFLICT;
- everything current → one OK summary or empty non-error findings according to chosen output contract.

- [ ] **Step 10: Implement doctor service**

Compute expected content in memory, compare only; no writes or `touch()` calls.

- [ ] **Step 11: Write failing CLI tests**

Use `CliRunner` and `monkeypatch.chdir(tmp_path)`.

Commands and required flags:

```text
airules init [--profile NAME] [--dry-run]
airules sync [--dry-run]
airules add SELECTION [--dry-run]
airules detect
airules explain
airules doctor
```

`--dry-run` prints `would create/update` and leaves filesystem unchanged.

- [ ] **Step 12: Implement CLI commands**

Typer commands catch only `AirulesError`, print concise remediation, and exit with the exception exit code. Unexpected errors retain traceback behavior for development rather than being mislabeled as user errors.

- [ ] **Step 13: Run project command tests**

Run:

```bash
uv run pytest \
  tests/test_project.py \
  tests/test_sync.py \
  tests/test_explain.py \
  tests/test_doctor.py \
  tests/test_cli_project_commands.py -q
```

Expected: PASS.

---

### Task 10: Global Universal-Core Bootstrap and Git/External-Action Safety Tests

**Files:**
- Create: `src/ai_rules/bootstrap.py`
- Modify: `src/ai_rules/cli.py`
- Create: `tests/test_bootstrap.py`
- Create: `tests/test_cli_bootstrap.py`
- Create: `tests/test_cli_readonly.py`

**Interfaces:**
- `bootstrap_global(home: Path | None = None, *, codex_home: Path | None = None, dry_run: bool = False) -> tuple[PlannedWrite, ...]`
- Bootstrap installs **only** Universal Core, never Python/FastAPI/etc. technology preferences.

- [ ] **Step 1: Write failing bootstrap tests**

Given temporary `home`:

Expected targets:

```text
<codex_home-or-home/.codex>/AGENTS.md
<home>/.claude/CLAUDE.md
<home>/.gemini/GEMINI.md
<home>/.ai-rules/cursor-user-rules.txt
```

Assertions:
- pre-existing global content is preserved in mixed files;
- managed block is idempotent;
- generated global text includes only rules whose scopes contain `core` and specifically mandatory universal security/external-action invariants selected by a constant list;
- it does **not** include `backend.fastapi`, `data.postgresql`, `messaging.rabbitmq`, `frontend.nextjs`, or `ml.gpu-cuda`;
- dry-run makes no files;
- Cursor helper file clearly says to paste content into Cursor User Rules manually.

- [ ] **Step 2: Write failing Git-safety source test**

`tests/test_cli_readonly.py` reads all Python under `src/ai_rules` and rejects command-building strings matching:

```regex
git\s+(add|commit|push|checkout|switch|merge|rebase|reset|clean|tag)
```

Also monkeypatch `subprocess.run`, `subprocess.Popen`, and `os.system` in E2E CLI tests so they raise if accidentally invoked.

The source test allows read-only future helpers only through a reviewed allow-list (`git status`, `git rev-parse`, etc.), but v1 implementation should require no Git subprocess at all.

- [ ] **Step 3: Run bootstrap/safety tests and verify failure**

Run:

```bash
uv run pytest tests/test_bootstrap.py tests/test_cli_readonly.py -q
```

Expected: FAIL because bootstrap is absent.

- [ ] **Step 4: Define exact universal-core allow-list**

In `bootstrap.py`:

```python
UNIVERSAL_RULE_IDS = (
    "core.agent-behavior",
    "core.scope-discipline",
    "core.workflow",
    "core.verification",
    "core.external-actions",
    "core.documentation",
    "security.baseline",
    "security.secrets",
    "quality.anti-cheating",
)
```

These rule files must exist by Task 10; if any is missing, bootstrap fails loudly rather than silently omitting it.

- [ ] **Step 5: Implement global rendered body**

Body begins:

```markdown
# Universal AI Engineering Rules

These are cross-project invariants. Project-specific instructions and direct user requests take precedence over generic preferences except where doing so would violate safety or explicit invariants.
```

Append canonical bodies in allow-list order, not severity sorting, to keep global context predictable.

- [ ] **Step 6: Implement global path planning**

Codex:

```python
resolved_codex_home = codex_home or Path(os.environ["CODEX_HOME"]) if set else home / ".codex"
```

Claude/Gemini use fixed home-relative paths. Cursor helper is fully airules-owned and must refuse to overwrite a foreign non-owned file unless the exact expected ownership header is present.

- [ ] **Step 7: Add CLI bootstrap command**

```text
airules bootstrap [--dry-run]
```

Print per-target create/update/unchanged status and the final Cursor manual-settings instruction.

- [ ] **Step 8: Run bootstrap and safety tests**

Run:

```bash
uv run pytest tests/test_bootstrap.py tests/test_cli_bootstrap.py tests/test_cli_readonly.py -q
```

Expected: PASS.

---

### Task 11: Canonical Python Backend, Architecture, Messaging, Security, and Quality Rules

**Files:**
- Create rules under `rules/core`, `rules/languages`, `rules/backend`, `rules/data`, `rules/architecture`, `rules/messaging`, `rules/security`, `rules/quality`
- Extend: `tests/test_canonical_rules.py`

**Interfaces:**
- Every canonical document conforms to Task 2 parser schema.
- Profile references from Task 3 all resolve.

- [ ] **Step 1: Write failing canonical-policy tests**

Create `tests/test_canonical_rules.py` assertions by rule ID, not filename.

Required assertions:

```python
def test_microservices_is_user_decision(rules):
    assert rules["architecture.microservices"].severity is RuleSeverity.USER_DECISION


def test_kafka_requires_user_decision(rules):
    assert rules["messaging.kafka"].severity is RuleSeverity.USER_DECISION
    assert "RabbitMQ" in rules["messaging.kafka"].body


def test_uv_migration_requires_approval(rules):
    body = rules["languages.python"].body.lower()
    assert "uv" in body
    assert "explicit" in body
    assert "existing" in body


def test_refresh_tokens_are_not_localstorage_default(rules):
    body = rules["security.auth"].body.lower()
    assert "localstorage" in body
    assert "long-lived" in body
```

Also assert all expected IDs exist and every profile resolves without unknown modules.

- [ ] **Step 2: Run canonical tests and verify failure**

Run:

```bash
uv run pytest tests/test_canonical_rules.py -q
```

Expected: FAIL until full modules exist.

- [ ] **Step 3: Create Universal Core modules**

Exact IDs/severity:

```text
core.agent-behavior required
core.scope-discipline required
core.workflow required
core.verification required
core.external-actions required
core.documentation conditional
```

Key required semantics:
- inspect before change;
- smallest sufficient change;
- no unrelated refactor/dependency upgrades;
- preserve architecture/project conventions;
- no external write/commit/push/deploy without explicit user intent;
- run relevant verification before claiming success;
- never fake or hide verification failures.

- [ ] **Step 4: Create Python/backend modules**

Create:

```text
languages.python (preferred)
backend.async-python (preferred)
backend.api-design (conditional)
backend.fastapi (preferred)
backend.pydantic (preferred)
backend.uvicorn-asgi (preferred)
backend.django (preferred)
backend.django-modern-rest (preferred)
backend.msgspec (preferred)
```

Required Python semantics:
- latest stable compatible Python for greenfield;
- prefer `uv` for greenfield;
- preserve current dependency manager in existing project;
- recommend `uv` migration only with explicit benefits/costs and wait for explicit approval;
- no prerelease dependencies by default;
- `django-modern-rest` is an explicit prerelease/Alpha exception when Django profile is selected.

Async rule:
- async I/O by default where stack supports it;
- no blocking I/O on event loop;
- thread/process offload only for justified blocking/CPU work;
- bounded concurrency and cancellation/timeout handling.

- [ ] **Step 5: Create data modules**

Create:

```text
data.postgresql (preferred)
data.mongodb (conditional)
data.redis (conditional)
data.sqlalchemy (preferred)
data.django-orm (preferred)
data.alembic (preferred)
data.django-migrations (preferred)
```

Required semantics include schema/data integrity, transaction boundaries, indexes based on actual queries, async DB access when supported, migration for schema changes, no direct production schema mutation, ORM default but raw SQL allowed when justified and parameterized.

- [ ] **Step 6: Create architecture modules**

Create:

```text
architecture.architecture-decisions (user_decision)
architecture.microservices (user_decision)
architecture.event-driven (user_decision)
architecture.saga (conditional)
architecture.orchestration (user_decision)
architecture.api-gateway (user_decision)
architecture.idempotency (required)
architecture.retry-backoff (conditional)
architecture.deduplication (conditional)
architecture.sla-timers (conditional)
```

Microservices, event-driven, orchestration/choreography, API Gateway are recommendation-capable but never migration mandates. Idempotency is REQUIRED for externally repeatable/at-least-once operations where duplicates cause incorrect state.

- [ ] **Step 7: Create messaging modules**

Create:

```text
messaging.rabbitmq (preferred)
messaging.aio-pika (conditional)
messaging.aiormq (conditional)
messaging.celery (conditional)
messaging.kafka (user_decision)
```

Required content includes ack/nack, durable topology where needed, publisher confirms where needed, idempotent consumers, bounded retry/backoff, DLQ/poison messages, correlation IDs, graceful shutdown. Kafka requires explicit justification/approval for introduction.

- [ ] **Step 8: Create security modules**

Create:

```text
security.baseline (required)
security.auth (required)
security.keycloak (preferred)
security.oauth2-oidc (conditional)
security.jwt (conditional)
security.rbac (conditional)
security.secrets (required)
security.dependencies (required)
```

Required auth properties include maintained libraries, issuer/audience/signature/expiry/token-purpose validation, PKCE/state/nonce according to flow, no invented crypto, safer handling of long-lived browser credentials, least privilege, deny-by-default authorization checks, no secret logging.

- [ ] **Step 9: Create quality modules**

Create:

```text
quality.testing (required)
quality.pytest (preferred)
quality.typing (required)
quality.ruff (required)
quality.bandit (required)
quality.anti-cheating (required)
```

Required content: pytest/pytest-asyncio/mocks, unit + integration where meaningful, regression tests, risk-based testing, no coverage gaming, no deleting/skipping/weaking tests, no broad ignores to silence tools, no claiming checks passed unless run.

- [ ] **Step 10: Remove temporary incomplete-profile validation escape hatch**

`load_profiles()` must now always validate referenced canonical module IDs during normal CLI operation. Tests may still pass explicit in-memory profiles without packaged module validation where unit isolation requires it.

- [ ] **Step 11: Run canonical/profile/full parser tests**

Run:

```bash
uv run pytest tests/test_canonical_rules.py tests/test_profiles.py tests/test_resources.py -q
```

Expected: PASS.

---

### Task 11: Frontend, ML/GPU, and Infrastructure Canonical Rules

**Files:**
- Create rules under `rules/frontend`, `rules/ml`, `rules/infrastructure`
- Extend: `tests/test_canonical_rules.py`

**Interfaces:**
- Completes `frontend-nextjs`, `ml-gpu-service`, `fullstack-python` profiles without introducing architecture migrations.

- [ ] **Step 1: Extend canonical tests with frontend/ML/infra assertions**

Assert:
- frontend stack rules are PREFERRED/CONDITIONAL, not migration mandates;
- Kubernetes/Helm/GitOps introduction is USER_DECISION;
- Caddy is preferred for new simple deployments while existing Nginx is preserved;
- ML rules require CPU/unit/contract validation before expensive GPU runs when possible;
- VRAM lifecycle/failure cleanup/bounded batching are present;
- Docker → Compose → Kubernetes → Helm → GitOps is documented as increasing complexity, not an automatic migration path.

- [ ] **Step 2: Create frontend modules**

Create:

```text
frontend.typescript
frontend.react
frontend.nextjs
frontend.tailwind
frontend.shadcn-radix
frontend.tanstack-query
frontend.zustand
frontend.forms-zod
frontend.api-client
```

Use PREFERRED for greenfield defaults and CONDITIONAL for library-specific behavior. Preserve existing frontend stack. REST/WebSocket use is driven by product/API needs, not mandated universally.

- [ ] **Step 3: Create ML modules**

Create:

```text
ml.service-boundaries
ml.gpu-cuda
ml.vram
ml.batching
ml.parallel-processing
ml.pipelines
ml.llm-integrations
```

Rules cover FastAPI service boundaries where selected, GPU/CUDA isolation, VRAM lifecycle, bounded batches, backpressure, cancellation, parallel I/O vs CPU/GPU work, task queues, orchestration/gateway/IO-DB separation only when project already has/chooses it, deterministic structured LLM contracts where practical, and expensive compute testing strategy.

- [ ] **Step 4: Create infrastructure modules**

Create:

```text
infrastructure.docker
infrastructure.docker-compose
infrastructure.kubernetes
infrastructure.helm
infrastructure.gitops
infrastructure.caddy
infrastructure.nginx
infrastructure.linux
infrastructure.windows
infrastructure.ansible
infrastructure.ci-cd
infrastructure.observability
infrastructure.prometheus-grafana
infrastructure.opentelemetry
infrastructure.healthchecks
```

`kubernetes`, `helm`, and `gitops` must be USER_DECISION for introduction. Health/readiness/liveness rules become CONDITIONAL when deployment/runtime supports them.

- [ ] **Step 5: Run canonical/profile tests**

Run:

```bash
uv run pytest tests/test_canonical_rules.py tests/test_profiles.py -q
```

Expected: PASS with every profile resolvable.

---

### Task 12: README, Authoring Docs, Changelog, End-to-End Tests, and Release-Quality Verification

**Files:**
- Modify: `README.md`
- Create: `CHANGELOG.md`
- Create: `PRIVATE.md`
- Create: `docs/manifest.md`
- Create: `docs/rules-authoring.md`
- Create: `docs/agent-adapters.md`
- Create: `adapters/README.md`
- Create: `tests/test_e2e.py`

**Interfaces:**
- Documents install/use/safety without exposing private repository secrets.
- End-to-end test exercises packaged CLI behavior in a temporary project.

- [ ] **Step 1: Write end-to-end test**

Use `CliRunner` with isolated filesystem to execute:

```text
airules init --profile fastapi-backend
airules doctor
airules explain
airules sync
airules add ml-gpu-service
airules doctor
```

Assertions:
- every command exits 0;
- second sync reports no changes;
- project-specific file survives manual edit;
- pre-existing AGENTS/CLAUDE/GEMINI content survives;
- no application source/config file changes other than explicit airules-owned files;
- generated snapshot contains fastapi + ML rules after add;
- Git is never invoked by the CLI (monkeypatch `subprocess.run/Popen` to fail if called, unless a future read-only Git helper is intentionally added and tested separately).

- [ ] **Step 2: Run E2E and verify any documentation-dependent failure**

Run:

```bash
uv run pytest tests/test_e2e.py -q
```

Expected: PASS after command implementation; if it fails, fix behavior before documentation.

- [ ] **Step 3: Write Russian README quick start**

README must include:

```text
Что это
Почему не submodule/copy
Установка через uv tool install git+ssh://...
airules bootstrap
airules init
airules init --profile fastapi-backend
airules detect / explain / doctor / sync / add
Что airules никогда не делает
Как обновить CLI через uv tool upgrade
Как устроены canonical rules / profiles / project.md
Cursor global User Rules manual step
```

Explicitly state that `airules add kubernetes` would only add AI guidance if a Kubernetes rule selection is supported; it never installs Kubernetes.

- [ ] **Step 4: Write manifest/authoring/adapter docs**

`docs/manifest.md` documents all manifest fields and precedence.

`docs/rules-authoring.md` documents exact frontmatter:

```toml
+++
id = "category.name"
title = "Human Title"
severity = "preferred"
scopes = ["python", "backend"]
+++
```

and defines REQUIRED/PREFERRED/CONDITIONAL/OPTIONAL/USER_DECISION with examples.

`docs/agent-adapters.md` records current native behavior:
- Codex global `$CODEX_HOME/AGENTS.md` + hierarchical project `AGENTS.md`;
- Claude global `~/.claude/CLAUDE.md`, project `CLAUDE.md`, `@path` imports;
- Gemini global `~/.gemini/GEMINI.md`, hierarchical context and `@path` imports;
- Cursor project `.cursor/rules/*.mdc`; global User Rules live in Settings and require manual paste from generated helper file.

- [ ] **Step 5: Add changelog/private note**

`CHANGELOG.md` starts with `0.1.0` and summarizes CLI/rules/profiles/adapters.

`PRIVATE.md` states the repository is private, rules were independently authored from ideas rather than copied from the unlicensed upstream repository, and distribution should remain private unless the user chooses a license later.

- [ ] **Step 6: Run the complete verification suite**

Run:

```bash
uv run pytest -q
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
uv run bandit -c pyproject.toml -r src
uv build
```

Expected: every command exits 0.

- [ ] **Step 7: Verify installed-wheel smoke behavior in an isolated uv tool environment**

Run without touching user-global agent files:

```bash
uv tool run --from dist/*.whl airules version
```

If shell glob expansion is not accepted by `uv tool run`, resolve the exact wheel path first and pass it explicitly.

Expected output begins with:

```text
airules 0.1.0
```

- [ ] **Step 8: Final safety inspection**

Run:

```bash
grep -RInE 'git (add|commit|push|checkout|switch|merge|rebase|reset|clean|tag)|subprocess\.(run|Popen).*git' src || true
git status --short
git diff --stat
git diff
```

Review that:
- CLI contains no hidden Git-write behavior;
- only `ai-engineering-rules` repository files changed;
- no secrets/tokens/private remote credentials are embedded in source/docs;
- no generated files overwrite user-owned project content outside managed blocks.

Do not stage or commit. Present the final diff/status to the user; the user decides and performs any commit/push.

---

## Implementation Order and Review Gates

Execute Tasks 1–12 in order. Each task has a testable boundary and must pass its task-specific tests before moving on. After Tasks 6, 9, and 12, perform an additional manual review of generated files because those tasks define agent-facing safety behavior.

The first usable vertical slice exists after Task 7 (`init/sync/add` with minimal canonical rules). Do not call v1 complete until Tasks 10–12 populate/validate the full rule-pack and the release-quality checks pass.
