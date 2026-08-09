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
from ai_rules.errors import AirulesError
from ai_rules.ides import SUPPORTED_IDES, normalize_ides
from ai_rules.manifest import load_manifest
from ai_rules.models import DoctorFinding, EffectiveRules
from ai_rules.precedence import compose_effective_rules, validate_catalog_integrity
from ai_rules.profiles import load_profiles
from ai_rules.project import ProjectPaths
from ai_rules.project_instructions import PROJECT_INSTRUCTIONS_TEMPLATE, is_project_incomplete
from ai_rules.rendering import render_generated_rules
from ai_rules.rules import load_rules


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _check_single_adapter(
    findings: list[DoctorFinding],
    *,
    path: Path,
    expected: str,
    code: str,
) -> None:
    if _read(path) != expected:
        findings.append(DoctorFinding("WARN", code, f"Adapter needs sync: {path}"))


def _check_native_adapter(
    findings: list[DoctorFinding],
    *,
    directory: Path,
    expected: dict[str, str],
    is_owned: Callable[[str | None], bool],
    pattern: str,
    code_prefix: str,
) -> None:
    expected_paths = {directory / name for name in expected}
    for name, content in expected.items():
        path = directory / name
        current = _read(path)
        if current == content:
            continue
        if current is not None and not is_owned(current):
            findings.append(
                DoctorFinding(
                    "ERROR",
                    f"{code_prefix}_adapter_conflict",
                    f"Native rule exists but is not owned by airules: {path}",
                )
            )
        else:
            findings.append(
                DoctorFinding(
                    "WARN",
                    f"{code_prefix}_adapter_outdated",
                    f"Native rule needs sync: {path}",
                )
            )
    if directory.exists():
        for path in directory.glob(pattern):
            if path in expected_paths:
                continue
            if is_owned(_read(path)):
                findings.append(
                    DoctorFinding(
                        "WARN",
                        f"{code_prefix}_adapter_stale",
                        f"Stale airules-owned native rule: {path}",
                    )
                )


def _check_cursor(
    findings: list[DoctorFinding],
    paths: ProjectPaths,
    effective: EffectiveRules,
    project_text: str,
) -> None:
    _check_native_adapter(
        findings,
        directory=paths.cursor_rules_dir,
        expected=render_cursor_native(effective, project_text),
        is_owned=is_owned_cursor_rule,
        pattern="airules-*.mdc",
        code_prefix="cursor",
    )
    legacy = _read(paths.legacy_cursor_rule)
    if is_owned_cursor_rule(legacy):
        findings.append(
            DoctorFinding(
                "WARN",
                "cursor_adapter_stale",
                f"Legacy airules Cursor adapter needs migration: {paths.legacy_cursor_rule}",
            )
        )


def doctor_project(root: Path) -> tuple[DoctorFinding, ...]:
    paths = ProjectPaths(root.resolve())
    findings: list[DoctorFinding] = []
    if not paths.manifest.exists():
        return (DoctorFinding("ERROR", "manifest_missing", "Missing .ai-rules.toml"),)
    try:
        manifest = load_manifest(paths.manifest)
        profiles = load_profiles(validate_modules=False)
        rules = load_rules()
        validate_catalog_integrity(profiles, rules)
        effective = compose_effective_rules(manifest, profiles, rules)
        expected_generated = render_generated_rules(
            effective,
            manifest.rules_version or __version__,
        )
    except AirulesError as exc:
        return (DoctorFinding("ERROR", "invalid_configuration", str(exc)),)

    current_generated = _read(paths.generated)
    if current_generated is None:
        findings.append(
            DoctorFinding(
                "ERROR",
                "stale_or_missing_generated",
                "Missing generated rules snapshot",
            )
        )
    elif current_generated != expected_generated:
        findings.append(
            DoctorFinding(
                "WARN",
                "generated_content_modified",
                "Generated rules differ from manifest/rule-pack",
            )
        )

    project_text = _read(paths.project_rules)
    if project_text is None:
        findings.append(
            DoctorFinding(
                "WARN",
                "project_rules_missing",
                "Missing user-owned .ai-rules/project.md",
            )
        )
        project_text = PROJECT_INSTRUCTIONS_TEMPLATE
    elif is_project_incomplete(project_text):
        findings.append(
            DoctorFinding(
                "WARN",
                "project_rules_incomplete",
                "Project onboarding is incomplete; complete .ai-rules/project.md with your AI "
                "coding agent and remove the incomplete marker.",
            )
        )

    selected_ides = (
        SUPPORTED_IDES
        if manifest.ides is None
        else normalize_ides(manifest.ides, default_all=False)
    )

    if "codex" in selected_ides:
        current = _read(paths.codex)
        _check_single_adapter(
            findings,
            path=paths.codex,
            expected=render_codex(current),
            code="codex_adapter_outdated",
        )

    if "claude" in selected_ides:
        current = _read(paths.claude)
        _check_single_adapter(
            findings,
            path=paths.claude,
            expected=render_claude(current),
            code="claude_adapter_outdated",
        )
        _check_native_adapter(
            findings,
            directory=paths.claude_native_dir,
            expected=render_claude_native(effective),
            is_owned=is_owned_claude_rule,
            pattern="*.md",
            code_prefix="claude",
        )

    if "gemini" in selected_ides:
        current = _read(paths.gemini)
        _check_single_adapter(
            findings,
            path=paths.gemini,
            expected=render_gemini(current),
            code="gemini_adapter_outdated",
        )

    if "cursor" in selected_ides:
        _check_cursor(findings, paths, effective, project_text)

    if "copilot" in selected_ides:
        current = _read(paths.copilot)
        _check_single_adapter(
            findings,
            path=paths.copilot,
            expected=render_copilot(current, project_text),
            code="copilot_adapter_outdated",
        )
        _check_native_adapter(
            findings,
            directory=paths.copilot_native_dir,
            expected=render_copilot_native(effective),
            is_owned=is_owned_copilot_rule,
            pattern="*.instructions.md",
            code_prefix="copilot",
        )

    if not findings:
        findings.append(DoctorFinding("INFO", "healthy", "airules project state is consistent"))
    return tuple(findings)
