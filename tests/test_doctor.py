import shutil
from pathlib import Path

from ai_rules.doctor import doctor_project
from ai_rules.sync import init_project

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"


def make_project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False)
    return root


def test_doctor_healthy_project_has_no_errors(tmp_path: Path) -> None:
    root = make_project(tmp_path)
    assert not [finding for finding in doctor_project(root) if finding.level == "ERROR"]


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
