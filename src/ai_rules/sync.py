from __future__ import annotations

from pathlib import Path

from ai_rules import __version__
from ai_rules.adapters.claude import render_claude
from ai_rules.adapters.codex import render_codex
from ai_rules.adapters.cursor import render_cursor
from ai_rules.adapters.gemini import render_gemini
from ai_rules.detection import detect_project, suggest_extra_profiles, suggest_profile
from ai_rules.errors import ConfigurationError
from ai_rules.filesystem import WriteScope, apply_writes, plan_write
from ai_rules.manifest import load_manifest, render_manifest
from ai_rules.models import Detection, DetectionConfidence, ProjectManifest, SyncResult
from ai_rules.precedence import compose_effective_rules
from ai_rules.profiles import load_profiles
from ai_rules.project import ProjectPaths
from ai_rules.rendering import render_generated_rules
from ai_rules.rules import load_rules

_PROJECT_TEMPLATE = """# Project-Specific AI Instructions

Add repository-specific architecture, testing, operational, and business constraints here.
This file is user-owned and is never overwritten by `airules sync`.
"""

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
                paths.cursor,
            }
        ),
        allowed_prefixes=(paths.rules_dir, paths.root / ".cursor" / "rules"),
    )


def _manifest_from_detections(profile: str, detections: tuple[Detection, ...]) -> ProjectManifest:
    manifest = ProjectManifest(profile=profile, rules_version=__version__)
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


def _render_all(
    paths: ProjectPaths,
    manifest: ProjectManifest,
    *,
    create_project_file: bool,
) -> tuple:
    profiles = load_profiles(validate_modules=True)
    rules = load_rules()
    effective = compose_effective_rules(manifest, profiles, rules)
    generated = render_generated_rules(effective, manifest.rules_version or __version__)

    writes = [
        plan_write(paths.manifest, render_manifest(manifest, _read_text(paths.manifest))),
        plan_write(paths.generated, generated),
        plan_write(paths.codex, render_codex(_read_text(paths.codex))),
        plan_write(paths.claude, render_claude(_read_text(paths.claude))),
        plan_write(paths.gemini, render_gemini(_read_text(paths.gemini))),
        plan_write(paths.cursor, render_cursor(_read_text(paths.cursor))),
    ]
    if create_project_file and not paths.project_rules.exists():
        writes.append(plan_write(paths.project_rules, _PROJECT_TEMPLATE))
    return tuple(writes)


def init_project(root: Path, profile: str | None, dry_run: bool) -> SyncResult:
    root = root.resolve()
    paths = ProjectPaths(root)
    detections = detect_project(root)
    selected = profile or suggest_profile(detections)
    if not selected:
        raise ConfigurationError("Could not infer a safe profile; use --profile NAME")
    profiles = load_profiles(validate_modules=True)
    if selected not in profiles:
        raise ConfigurationError(f"Unknown profile: {selected}")
    manifest = _manifest_from_detections(selected, detections)
    # Explicit profile remains primary; ML is an extra only when detected.
    writes = _render_all(paths, manifest, create_project_file=True)
    applied = apply_writes(writes, dry_run=dry_run, scope=_scope(paths))
    return SyncResult(
        writes=applied,
        selected_profiles=(manifest.profile, *manifest.extra_profiles),
        detections=detections,
    )


def sync_project(root: Path, dry_run: bool) -> SyncResult:
    root = root.resolve()
    paths = ProjectPaths(root)
    if not paths.manifest.exists():
        raise ConfigurationError("Project is not initialized; run `airules init`")
    manifest = load_manifest(paths.manifest)
    manifest.rules_version = __version__
    writes = _render_all(paths, manifest, create_project_file=False)
    applied = apply_writes(writes, dry_run=dry_run, scope=_scope(paths))
    return SyncResult(
        writes=applied,
        selected_profiles=(manifest.profile, *manifest.extra_profiles),
    )


def add_selection(root: Path, selection: str, dry_run: bool) -> SyncResult:
    root = root.resolve()
    paths = ProjectPaths(root)
    manifest = load_manifest(paths.manifest)
    profiles = load_profiles(validate_modules=True)
    rules = load_rules()
    if selection in profiles:
        if selection != manifest.profile and selection not in manifest.extra_profiles:
            manifest.extra_profiles.append(selection)
    elif selection in rules:
        if selection not in manifest.include_modules:
            manifest.include_modules.append(selection)
    else:
        raise ConfigurationError(f"Unknown profile or rule: {selection}")
    manifest.rules_version = __version__
    writes = _render_all(paths, manifest, create_project_file=False)
    applied = apply_writes(writes, dry_run=dry_run, scope=_scope(paths))
    return SyncResult(
        writes=applied,
        selected_profiles=(manifest.profile, *manifest.extra_profiles),
    )
