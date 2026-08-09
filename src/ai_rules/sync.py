from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from ai_rules import __version__
from ai_rules.adapters.claude import (
    is_owned_claude_rule,
    render_claude,
    render_claude_native,
)
from ai_rules.adapters.codex import render_codex
from ai_rules.adapters.copilot import (
    is_owned_copilot_rule,
    render_copilot,
    render_copilot_native,
)
from ai_rules.adapters.cursor import is_owned_cursor_rule, render_cursor_native
from ai_rules.adapters.gemini import render_gemini
from ai_rules.detection import detect_project, suggest_extra_profiles, suggest_profile
from ai_rules.errors import ConfigurationError
from ai_rules.filesystem import (
    WriteScope,
    apply_deletes,
    apply_writes,
    plan_delete,
    plan_write,
)
from ai_rules.ides import SUPPORTED_IDES, normalize_ides
from ai_rules.manifest import load_manifest, render_manifest
from ai_rules.models import (
    Detection,
    DetectionConfidence,
    EffectiveRules,
    PlannedDelete,
    PlannedWrite,
    ProjectManifest,
    SyncResult,
)
from ai_rules.precedence import compose_effective_rules, validate_catalog_integrity
from ai_rules.profiles import load_profiles
from ai_rules.project import ProjectPaths
from ai_rules.project_instructions import PROJECT_INSTRUCTIONS_TEMPLATE
from ai_rules.rendering import render_generated_rules
from ai_rules.rules import load_rules

_DETECTION_MANIFEST_MAP: dict[str, tuple[str, str]] = {
    "python": ("language", "python"),
    "fastapi": ("backend", "fastapi"),
    "django": ("backend", "django"),
    "django-modern-rest": ("backend", "django_modern_rest"),
    "pydantic": ("backend", "pydantic"),
    "msgspec": ("backend", "msgspec"),
    "postgresql": ("data", "postgresql"),
    "sqlalchemy": ("data", "sqlalchemy"),
    "alembic": ("data", "alembic"),
    "redis": ("data", "redis"),
    "rabbitmq": ("messaging", "rabbitmq"),
    "aio-pika": ("messaging", "aio_pika"),
    "aiormq": ("messaging", "aiormq"),
    "celery": ("messaging", "celery"),
    "kafka": ("messaging", "kafka"),
    "nextjs": ("frontend", "nextjs"),
    "gpu-cuda": ("ml", "gpu"),
    "docker": ("infrastructure", "docker"),
    "docker-compose": ("infrastructure", "compose"),
    "kubernetes": ("infrastructure", "kubernetes"),
    "helm": ("infrastructure", "helm"),
}


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _scope(paths: ProjectPaths) -> WriteScope:
    return WriteScope(
        root=paths.root,
        allowed_exact=frozenset(
            {
                paths.manifest,
                paths.generated,
                paths.project_rules,
                paths.codex,
                paths.claude,
                paths.gemini,
                paths.legacy_cursor_rule,
                paths.copilot,
            }
        ),
        allowed_prefixes=(
            paths.rules_dir,
            paths.cursor_rules_dir,
            paths.claude_native_dir,
            paths.copilot_native_dir,
        ),
    )


def _manifest_from_detections(
    profile: str,
    detections: tuple[Detection, ...],
    *,
    ides: tuple[str, ...],
) -> ProjectManifest:
    manifest = ProjectManifest(profile=profile, rules_version=__version__, ides=list(ides))
    for detection in detections:
        if detection.confidence is DetectionConfidence.NOT_DETECTED:
            continue
        mapping = _DETECTION_MANIFEST_MAP.get(detection.key)
        if mapping is None:
            continue
        section, key = mapping
        values = getattr(manifest, section)
        values[key] = True
    manifest.extra_profiles = list(suggest_extra_profiles(detections))
    return manifest


def _plan_native_files(
    directory: Path,
    expected: dict[str, str],
    *,
    is_owned: Callable[[str | None], bool],
    pattern: str,
    label: str,
) -> tuple[list[PlannedWrite], list[PlannedDelete]]:
    writes: list[PlannedWrite] = []
    deletes: list[PlannedDelete] = []
    expected_paths = {directory / name for name in expected}
    for name, content in expected.items():
        path = directory / name
        existing = _read_text(path)
        if existing is not None and not is_owned(existing):
            raise ConfigurationError(f"{label} rule exists but is not owned by airules: {path}")
        writes.append(plan_write(path, content))
    if directory.exists():
        for path in directory.glob(pattern):
            if path in expected_paths:
                continue
            if is_owned(_read_text(path)):
                deletes.append(plan_delete(path))
    return writes, deletes


def _render_adapter_files(
    paths: ProjectPaths,
    effective: EffectiveRules,
    project_text: str,
    ides: tuple[str, ...],
) -> tuple[list[PlannedWrite], list[PlannedDelete]]:
    writes: list[PlannedWrite] = []
    deletes: list[PlannedDelete] = []

    if "codex" in ides:
        writes.append(plan_write(paths.codex, render_codex(_read_text(paths.codex))))

    if "claude" in ides:
        writes.append(plan_write(paths.claude, render_claude(_read_text(paths.claude))))
        native_writes, native_deletes = _plan_native_files(
            paths.claude_native_dir,
            render_claude_native(effective),
            is_owned=is_owned_claude_rule,
            pattern="*.md",
            label="Claude",
        )
        writes.extend(native_writes)
        deletes.extend(native_deletes)

    if "gemini" in ides:
        writes.append(plan_write(paths.gemini, render_gemini(_read_text(paths.gemini))))

    if "cursor" in ides:
        native_writes, native_deletes = _plan_native_files(
            paths.cursor_rules_dir,
            render_cursor_native(effective, project_text),
            is_owned=is_owned_cursor_rule,
            pattern="airules-*.mdc",
            label="Cursor",
        )
        writes.extend(native_writes)
        deletes.extend(native_deletes)
        legacy = _read_text(paths.legacy_cursor_rule)
        if is_owned_cursor_rule(legacy):
            deletes.append(plan_delete(paths.legacy_cursor_rule))

    if "copilot" in ides:
        writes.append(
            plan_write(
                paths.copilot,
                render_copilot(_read_text(paths.copilot), project_text),
            )
        )
        native_writes, native_deletes = _plan_native_files(
            paths.copilot_native_dir,
            render_copilot_native(effective),
            is_owned=is_owned_copilot_rule,
            pattern="*.instructions.md",
            label="Copilot",
        )
        writes.extend(native_writes)
        deletes.extend(native_deletes)

    return writes, deletes


def _render_all(
    paths: ProjectPaths,
    manifest: ProjectManifest,
    *,
    create_project_file: bool,
    ides: tuple[str, ...],
) -> tuple[tuple[PlannedWrite, ...], tuple[PlannedDelete, ...]]:
    profiles = load_profiles(validate_modules=False)
    rules = load_rules()
    validate_catalog_integrity(profiles, rules)
    effective = compose_effective_rules(manifest, profiles, rules)
    generated = render_generated_rules(effective, manifest.rules_version or __version__)
    project_text = _read_text(paths.project_rules) or PROJECT_INSTRUCTIONS_TEMPLATE

    writes: list[PlannedWrite] = [
        plan_write(paths.manifest, render_manifest(manifest, _read_text(paths.manifest))),
        plan_write(paths.generated, generated),
    ]
    adapter_writes, deletes = _render_adapter_files(paths, effective, project_text, ides)
    writes.extend(adapter_writes)
    if create_project_file and not paths.project_rules.exists():
        writes.append(plan_write(paths.project_rules, PROJECT_INSTRUCTIONS_TEMPLATE))
    return tuple(writes), tuple(deletes)


def _apply_rendered(
    paths: ProjectPaths,
    writes: tuple[PlannedWrite, ...],
    deletes: tuple[PlannedDelete, ...],
    *,
    dry_run: bool,
) -> tuple[tuple[PlannedWrite, ...], tuple[PlannedDelete, ...]]:
    scope = _scope(paths)
    applied_writes = apply_writes(writes, dry_run=dry_run, scope=scope)
    applied_deletes = apply_deletes(deletes, dry_run=dry_run, scope=scope)
    return applied_writes, applied_deletes


def init_project(
    root: Path,
    profile: str | None,
    dry_run: bool,
    ides: tuple[str, ...] | None = None,
) -> SyncResult:
    root = root.resolve()
    paths = ProjectPaths(root)
    detections = detect_project(root)
    selected = profile or suggest_profile(detections)
    if not selected:
        raise ConfigurationError("Could not infer a safe profile; use --profile NAME")
    profiles = load_profiles(validate_modules=False)
    rules = load_rules()
    validate_catalog_integrity(profiles, rules)
    if selected not in profiles:
        raise ConfigurationError(f"Unknown profile: {selected}")
    selected_ides = normalize_ides(ides, default_all=True)
    manifest = _manifest_from_detections(selected, detections, ides=selected_ides)
    writes, deletes = _render_all(
        paths,
        manifest,
        create_project_file=True,
        ides=selected_ides,
    )
    applied, removed = _apply_rendered(paths, writes, deletes, dry_run=dry_run)
    return SyncResult(
        writes=applied,
        deletes=removed,
        selected_profiles=(manifest.profile, *manifest.extra_profiles),
        detections=detections,
    )


def sync_project(
    root: Path,
    dry_run: bool,
    ides: tuple[str, ...] | None = None,
) -> SyncResult:
    root = root.resolve()
    paths = ProjectPaths(root)
    if not paths.manifest.exists():
        raise ConfigurationError("Project is not initialized; run `airules init`")
    manifest = load_manifest(paths.manifest)
    manifest.rules_version = __version__
    if ides is not None:
        selected_ides = normalize_ides(ides, default_all=False)
    elif manifest.ides is None:
        selected_ides = SUPPORTED_IDES
    else:
        selected_ides = normalize_ides(manifest.ides, default_all=False)
    writes, deletes = _render_all(
        paths,
        manifest,
        create_project_file=False,
        ides=selected_ides,
    )
    applied, removed = _apply_rendered(paths, writes, deletes, dry_run=dry_run)
    return SyncResult(
        writes=applied,
        deletes=removed,
        selected_profiles=(manifest.profile, *manifest.extra_profiles),
    )


def add_selection(root: Path, selection: str, dry_run: bool) -> SyncResult:
    root = root.resolve()
    paths = ProjectPaths(root)
    manifest = load_manifest(paths.manifest)
    profiles = load_profiles(validate_modules=False)
    rules = load_rules()
    validate_catalog_integrity(profiles, rules)
    if selection in profiles:
        if selection != manifest.profile and selection not in manifest.extra_profiles:
            manifest.extra_profiles.append(selection)
    elif selection in rules:
        if selection not in manifest.include_modules:
            manifest.include_modules.append(selection)
    else:
        raise ConfigurationError(f"Unknown profile or rule: {selection}")
    manifest.rules_version = __version__
    selected_ides = (
        SUPPORTED_IDES
        if manifest.ides is None
        else normalize_ides(manifest.ides, default_all=False)
    )
    writes, deletes = _render_all(
        paths,
        manifest,
        create_project_file=False,
        ides=selected_ides,
    )
    applied, removed = _apply_rendered(paths, writes, deletes, dry_run=dry_run)
    return SyncResult(
        writes=applied,
        deletes=removed,
        selected_profiles=(manifest.profile, *manifest.extra_profiles),
    )
