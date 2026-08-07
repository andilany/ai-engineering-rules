from __future__ import annotations

from pathlib import Path

from ai_rules import __version__
from ai_rules.adapters.claude import render_claude
from ai_rules.adapters.codex import render_codex
from ai_rules.adapters.cursor import render_cursor
from ai_rules.adapters.gemini import render_gemini
from ai_rules.errors import AirulesError
from ai_rules.manifest import load_manifest
from ai_rules.models import DoctorFinding
from ai_rules.precedence import compose_effective_rules
from ai_rules.profiles import load_profiles
from ai_rules.project import ProjectPaths
from ai_rules.rendering import render_generated_rules
from ai_rules.rules import load_rules


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def doctor_project(root: Path) -> tuple[DoctorFinding, ...]:
    paths = ProjectPaths(root.resolve())
    findings: list[DoctorFinding] = []
    if not paths.manifest.exists():
        return (DoctorFinding("ERROR", "manifest_missing", "Missing .ai-rules.toml"),)
    try:
        manifest = load_manifest(paths.manifest)
        effective = compose_effective_rules(manifest, load_profiles(validate_modules=True), load_rules())
        expected_generated = render_generated_rules(effective, manifest.rules_version or __version__)
    except AirulesError as exc:
        return (DoctorFinding("ERROR", "invalid_configuration", str(exc)),)

    current_generated = _read(paths.generated)
    if current_generated is None:
        findings.append(DoctorFinding("ERROR", "stale_or_missing_generated", "Missing generated rules snapshot"))
    elif current_generated != expected_generated:
        findings.append(DoctorFinding("WARN", "generated_content_modified", "Generated rules differ from manifest/rule-pack"))

    if not paths.project_rules.exists():
        findings.append(DoctorFinding("WARN", "project_rules_missing", "Missing user-owned .ai-rules/project.md"))

    adapters = (
        (paths.codex, render_codex, "codex_adapter_outdated"),
        (paths.claude, render_claude, "claude_adapter_outdated"),
        (paths.gemini, render_gemini, "gemini_adapter_outdated"),
    )
    for path, renderer, code in adapters:
        current = _read(path)
        try:
            expected = renderer(current)
        except AirulesError as exc:
            findings.append(DoctorFinding("ERROR", code, str(exc)))
            continue
        if current != expected:
            findings.append(DoctorFinding("WARN", code, f"Adapter needs sync: {path.name}"))

    current_cursor = _read(paths.cursor)
    try:
        expected_cursor = render_cursor(current_cursor)
    except AirulesError as exc:
        findings.append(DoctorFinding("ERROR", "cursor_adapter_conflict", str(exc)))
    else:
        if current_cursor != expected_cursor:
            findings.append(DoctorFinding("WARN", "cursor_adapter_outdated", "Cursor adapter needs sync"))

    if not findings:
        findings.append(DoctorFinding("INFO", "healthy", "airules project state is consistent"))
    return tuple(findings)
