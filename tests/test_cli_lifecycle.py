from __future__ import annotations

import shutil
from pathlib import Path

from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.manifest import load_manifest
from ai_rules.project_instructions import PROJECT_INCOMPLETE_MARKER

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"
runner = CliRunner()


def copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    return root


def test_uninstall_requires_confirmation_and_cancel_keeps_project(
    tmp_path: Path, monkeypatch
) -> None:
    root = copy_fixture(tmp_path)
    monkeypatch.chdir(root)
    init_result = runner.invoke(
        app, ["init", "--profile", "fastapi-backend", "--ide", "cursor"]
    )
    assert init_result.exit_code == 0

    result = runner.invoke(app, ["uninstall"], input="n\n")

    assert result.exit_code == 0
    assert "airules will be removed" in result.stdout
    assert "Cancelled. No changes were made." in result.stdout
    assert (root / ".ai-rules.toml").exists()


def test_uninstall_confirmed_preserves_project_rules(tmp_path: Path, monkeypatch) -> None:
    root = copy_fixture(tmp_path)
    monkeypatch.chdir(root)
    init_result = runner.invoke(
        app, ["init", "--profile", "fastapi-backend", "--ide", "cursor"]
    )
    assert init_result.exit_code == 0
    project_rules = root / ".ai-rules" / "project.md"
    project_rules.write_text("keep\n", encoding="utf-8")

    result = runner.invoke(app, ["uninstall"], input="y\n")

    assert result.exit_code == 0
    assert not (root / ".ai-rules.toml").exists()
    assert project_rules.read_text(encoding="utf-8") == "keep\n"


def test_noninteractive_init_prints_ai_project_onboarding(tmp_path: Path, monkeypatch) -> None:
    root = copy_fixture(tmp_path)
    monkeypatch.chdir(root)

    result = runner.invoke(
        app, ["init", "--profile", "fastapi-backend", "--ide", "cursor"]
    )

    assert result.exit_code == 0, result.stdout
    assert "Project-specific instructions still need your input" in result.stdout
    assert "Suggested prompt" in result.stdout
    assert "Ask me focused questions" in result.stdout
    project_rules = root / ".ai-rules" / "project.md"
    assert PROJECT_INCOMPLETE_MARKER in project_rules.read_text(encoding="utf-8")


def test_interactive_init_builds_selective_custom_manifest(tmp_path: Path, monkeypatch) -> None:
    root = copy_fixture(tmp_path)
    monkeypatch.chdir(root)

    result = runner.invoke(
        app,
        ["init", "--interactive"],
        input="1,6\n1\n1,2\n3\ny\n",
    )

    assert result.exit_code == 0, result.stdout
    manifest = load_manifest(root / ".ai-rules.toml")
    assert manifest.profile == "custom"
    assert manifest.ides == ["cursor"]
    assert manifest.backend == {"fastapi": True}
    assert manifest.infrastructure == {"docker": True, "compose": True}
    assert manifest.data == {}
    assert "Project-specific instructions still need your input" in result.stdout


def test_reconfigure_warns_then_replaces_selection_after_second_confirmation(
    tmp_path: Path, monkeypatch
) -> None:
    root = copy_fixture(tmp_path)
    monkeypatch.chdir(root)
    init_result = runner.invoke(
        app, ["init", "--profile", "fastapi-backend", "--ide", "codex"]
    )
    assert init_result.exit_code == 0
    project_rules = root / ".ai-rules" / "project.md"
    project_rules.write_text("keep me\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["reconfigure"],
        input="y\n2\n1\n3\ny\n",
    )

    assert result.exit_code == 0, result.stdout
    assert "Current airules configuration will be replaced" in result.stdout
    manifest = load_manifest(root / ".ai-rules.toml")
    assert manifest.profile == "custom"
    assert manifest.ides == ["cursor"]
    assert manifest.backend == {}
    assert manifest.frontend == {"nextjs": True}
    assert project_rules.read_text(encoding="utf-8") == "keep me\n"
    assert "Project-specific instructions still need your input" not in result.stdout
    assert not (root / "AGENTS.md").exists()
    assert (root / ".cursor" / "rules" / "airules-000-core.mdc").exists()
