import shutil
from pathlib import Path

from ai_rules.doctor import doctor_project
from ai_rules.project_instructions import PROJECT_INCOMPLETE_MARKER
from ai_rules.sync import init_project, sync_project

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"


def make_project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False)
    return root


def complete_project_rules(root: Path) -> None:
    (root / ".ai-rules" / "project.md").write_text(
        "# Project-Specific AI Instructions\n\nConfirmed project constraints.\n",
        encoding="utf-8",
    )


def test_doctor_healthy_project_has_no_errors(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    complete_project_rules(root)
    sync_project(root, dry_run=False)
    findings = doctor_project(root)
    assert not [finding for finding in findings if finding.level == "ERROR"]
    assert any(finding.code == "healthy" for finding in findings)


def test_doctor_warns_while_project_onboarding_is_incomplete(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    project_rules = root / ".ai-rules" / "project.md"

    assert PROJECT_INCOMPLETE_MARKER in project_rules.read_text(encoding="utf-8")
    assert any(
        finding.code == "project_rules_incomplete" and finding.level == "WARN"
        for finding in doctor_project(root)
    )

    complete_project_rules(root)
    assert not any(
        finding.code == "project_rules_incomplete" for finding in doctor_project(root)
    )


def test_doctor_reports_missing_or_modified_generated(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    generated = root / ".ai-rules" / "generated.md"
    generated.unlink()
    assert any(
        f.code == "stale_or_missing_generated" and f.level == "ERROR"
        for f in doctor_project(root)
    )

    init_project(root, profile="fastapi-backend", dry_run=False)
    generated.write_text(generated.read_text() + "manual edit\n", encoding="utf-8")
    assert any(f.code == "generated_content_modified" for f in doctor_project(root))


def test_doctor_warns_when_project_rules_missing(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    (root / ".ai-rules" / "project.md").unlink()
    assert any(
        f.code == "project_rules_missing" and f.level == "WARN"
        for f in doctor_project(root)
    )


def test_doctor_checks_only_persisted_cursor_adapter(tmp_path: Path) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("cursor",))
    complete_project_rules(root)
    sync_project(root, dry_run=False)

    findings = doctor_project(root)
    adapter_codes = {finding.code for finding in findings if "adapter" in finding.code}

    assert "codex_adapter_outdated" not in adapter_codes
    assert "claude_adapter_outdated" not in adapter_codes
    assert "gemini_adapter_outdated" not in adapter_codes
    assert "cursor_adapter_outdated" not in adapter_codes
    assert any(finding.code == "healthy" for finding in findings)


def test_doctor_legacy_manifest_without_ides_checks_all_adapters(tmp_path: Path) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("cursor",))
    manifest_path = root / ".ai-rules.toml"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(
        "\n".join(line for line in manifest_text.splitlines() if not line.startswith("ides ="))
        + "\n",
        encoding="utf-8",
    )

    adapter_codes = {
        finding.code for finding in doctor_project(root) if "adapter" in finding.code
    }

    assert "codex_adapter_outdated" in adapter_codes
    assert "claude_adapter_outdated" in adapter_codes
    assert "gemini_adapter_outdated" in adapter_codes
    assert "cursor_adapter_outdated" not in adapter_codes


def test_doctor_reports_missing_cursor_native_rule(tmp_path: Path) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("cursor",))
    missing = root / ".cursor" / "rules" / "airules-000-core.mdc"
    missing.unlink()

    findings = doctor_project(root)

    assert any(f.code == "cursor_adapter_outdated" and f.level == "WARN" for f in findings)


def test_doctor_reports_stale_owned_cursor_rule(tmp_path: Path) -> None:
    from ai_rules.adapters.cursor import OWNER

    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("cursor",))
    stale = root / ".cursor" / "rules" / "airules-stale.mdc"
    stale.write_text(f"{OWNER}\nstale\n", encoding="utf-8")

    findings = doctor_project(root)

    assert any(f.code == "cursor_adapter_stale" for f in findings)


def test_doctor_reports_owned_legacy_cursor_rule_for_migration(tmp_path: Path) -> None:
    from ai_rules.adapters.cursor import OWNER

    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("cursor",))
    legacy = root / ".cursor" / "rules" / "engineering.mdc"
    legacy.write_text(f"{OWNER}\nlegacy\n", encoding="utf-8")

    findings = doctor_project(root)

    assert any(
        f.code == "cursor_adapter_stale" and "Legacy airules Cursor adapter" in f.message
        for f in findings
    )


def test_doctor_validates_claude_native_rules(tmp_path: Path) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("claude",))
    target = root / ".claude" / "rules" / "airules" / "000-core.md"
    target.write_text(target.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")

    findings = doctor_project(root)

    assert any(f.code == "claude_adapter_outdated" for f in findings)
    assert not any(f.code.startswith("cursor_adapter") for f in findings)


def test_doctor_validates_copilot_native_rules(tmp_path: Path) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("copilot",))
    target = root / ".github" / "instructions" / "airules" / "000-core.instructions.md"
    target.unlink()

    findings = doctor_project(root)

    assert any(f.code == "copilot_adapter_outdated" for f in findings)
    assert not any(f.code.startswith("claude_adapter") for f in findings)
