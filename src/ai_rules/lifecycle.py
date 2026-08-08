from __future__ import annotations

from pathlib import Path

from ai_rules.filesystem import (
    WriteScope,
    apply_deletes,
    apply_writes,
    plan_delete,
    plan_write,
)
from ai_rules.managed_blocks import remove_managed_block
from ai_rules.models import PlannedDelete, PlannedWrite, ProjectManifest, SyncResult
from ai_rules.project import ProjectPaths

_OWNER = "<!-- ai-engineering-rules:owned -->"


def _read(path: Path) -> str | None:
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


def _plan_managed_root(path: Path) -> tuple[PlannedWrite | None, PlannedDelete | None]:
    existing = _read(path)
    if existing is None:
        return None, None
    cleaned = remove_managed_block(existing)
    if cleaned == existing:
        return None, None
    if not cleaned.strip():
        return None, plan_delete(path)
    return plan_write(path, cleaned), None


def _owned(content: str | None) -> bool:
    return content is not None and _OWNER in content


def plan_project_cleanup(
    paths: ProjectPaths,
    *,
    purge: bool,
) -> tuple[tuple[PlannedWrite, ...], tuple[PlannedDelete, ...], tuple[str, ...]]:
    writes: list[PlannedWrite] = []
    deletes: list[PlannedDelete] = []
    warnings: list[str] = []

    for path in (paths.codex, paths.claude, paths.gemini, paths.copilot):
        write, delete = _plan_managed_root(path)
        if write is not None:
            writes.append(write)
        if delete is not None:
            deletes.append(delete)

    native_specs = (
        (paths.cursor_rules_dir, "airules-*.mdc"),
        (paths.claude_native_dir, "*.md"),
        (paths.copilot_native_dir, "*.instructions.md"),
    )
    for directory, pattern in native_specs:
        if not directory.exists():
            continue
        for path in sorted(directory.glob(pattern)):
            if _owned(_read(path)):
                deletes.append(plan_delete(path))
            elif path.name.startswith("airules-"):
                warnings.append(f"Skipped non-owned airules-looking file: {path}")

    if _owned(_read(paths.cursor)):
        deletes.append(plan_delete(paths.cursor))

    deletes.append(plan_delete(paths.manifest))
    deletes.append(plan_delete(paths.generated))
    if purge:
        deletes.append(plan_delete(paths.project_rules))

    return tuple(writes), tuple(deletes), tuple(warnings)


def merge_reconfigure_plans(
    cleanup_writes: tuple[PlannedWrite, ...],
    cleanup_deletes: tuple[PlannedDelete, ...],
    new_writes: tuple[PlannedWrite, ...],
    new_deletes: tuple[PlannedDelete, ...],
) -> tuple[tuple[PlannedWrite, ...], tuple[PlannedDelete, ...]]:
    write_by_path = {item.path: item for item in cleanup_writes}
    for item in new_writes:
        write_by_path[item.path] = item

    delete_by_path = {item.path: item for item in cleanup_deletes}
    for item in new_deletes:
        delete_by_path[item.path] = item
    for path in write_by_path:
        delete_by_path.pop(path, None)

    writes = tuple(write_by_path[path] for path in sorted(write_by_path, key=str))
    deletes = tuple(delete_by_path[path] for path in sorted(delete_by_path, key=str))
    return writes, deletes


def uninstall_project(root: Path, *, purge: bool, dry_run: bool) -> SyncResult:
    paths = ProjectPaths(root.resolve())
    writes, deletes, warnings = plan_project_cleanup(paths, purge=purge)
    scope = _scope(paths)
    applied_writes = apply_writes(writes, dry_run=dry_run, scope=scope)
    applied_deletes = apply_deletes(deletes, dry_run=dry_run, scope=scope)
    return SyncResult(
        writes=applied_writes,
        deletes=applied_deletes,
        selected_profiles=(),
        warnings=warnings,
    )


def detected_manifest(
    root: Path,
    *,
    profile: str | None,
    ides: tuple[str, ...] | None,
) -> ProjectManifest:
    import ai_rules.sync as sync_module
    from ai_rules.detection import detect_project, suggest_profile
    from ai_rules.errors import ConfigurationError
    from ai_rules.ides import normalize_ides

    detections = detect_project(root.resolve())
    selected = profile or suggest_profile(detections)
    if not selected:
        raise ConfigurationError("Could not infer a safe profile; use --profile NAME")
    selected_ides = normalize_ides(ides, default_all=True)
    return sync_module._manifest_from_detections(
        selected,
        detections,
        ides=selected_ides,
    )


def configure_project(
    root: Path,
    manifest: ProjectManifest,
    *,
    dry_run: bool,
    replace_existing: bool,
) -> SyncResult:
    # Imported lazily to avoid a module import cycle: sync owns the canonical render pipeline.
    import ai_rules.sync as sync_module
    from ai_rules.ides import SUPPORTED_IDES, normalize_ides
    from ai_rules.manifest import render_manifest

    paths = ProjectPaths(root.resolve())
    manifest.rules_version = sync_module.__version__
    selected_ides = (
        SUPPORTED_IDES
        if manifest.ides is None
        else normalize_ides(manifest.ides, default_all=False)
    )
    new_writes, new_deletes = sync_module._render_all(
        paths,
        manifest,
        create_project_file=True,
        ides=selected_ides,
    )

    # Reconfiguration must not inherit stale keys from the previous TOML document.
    fresh_manifest = plan_write(paths.manifest, render_manifest(manifest, None))
    new_writes = tuple(
        fresh_manifest if item.path == paths.manifest else item for item in new_writes
    )

    warnings: tuple[str, ...] = ()
    if replace_existing:
        cleanup_writes, cleanup_deletes, warnings = plan_project_cleanup(paths, purge=False)
        new_writes, new_deletes = merge_reconfigure_plans(
            cleanup_writes,
            cleanup_deletes,
            new_writes,
            new_deletes,
        )

    applied_writes, applied_deletes = sync_module._apply_rendered(
        paths,
        new_writes,
        new_deletes,
        dry_run=dry_run,
    )
    return SyncResult(
        writes=applied_writes,
        deletes=applied_deletes,
        selected_profiles=(manifest.profile, *manifest.extra_profiles),
        warnings=warnings,
    )
