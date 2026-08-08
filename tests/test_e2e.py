import shutil
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.manifest import load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"
runner = CliRunner()


def test_end_to_end_project_workflow_preserves_user_content_and_never_calls_git(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    (root / "AGENTS.md").write_text("# Existing Codex instructions\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text("# Existing Claude instructions\n", encoding="utf-8")
    (root / "GEMINI.md").write_text("# Existing Gemini instructions\n", encoding="utf-8")
    original_pyproject = (root / "pyproject.toml").read_bytes()

    def fail_subprocess(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("airules must not invoke subprocess/git")

    monkeypatch.setattr(subprocess, "run", fail_subprocess)
    monkeypatch.setattr(subprocess, "Popen", fail_subprocess)
    monkeypatch.chdir(root)

    for command in (
        ["init", "--profile", "fastapi-backend"],
        ["doctor"],
        ["explain"],
        ["sync"],
        ["add", "ml-gpu-service"],
        ["doctor"],
    ):
        result = runner.invoke(app, command)
        assert result.exit_code == 0, f"{command}: {result.stdout}\n{result.exception}"

    project_rules = root / ".ai-rules" / "project.md"
    project_rules.write_text(
        project_rules.read_text() + "\nMy private project constraint.\n",
        encoding="utf-8",
    )
    second_sync = runner.invoke(app, ["sync"])
    assert second_sync.exit_code == 0
    assert "My private project constraint." in project_rules.read_text(encoding="utf-8")

    third_sync = runner.invoke(app, ["sync"])
    assert third_sync.exit_code == 0
    assert "change:" not in third_sync.stdout

    assert "Existing Codex instructions" in (root / "AGENTS.md").read_text(encoding="utf-8")
    assert "Existing Claude instructions" in (root / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Existing Gemini instructions" in (root / "GEMINI.md").read_text(encoding="utf-8")
    assert "# GPU / CUDA" in (root / ".ai-rules" / "generated.md").read_text(encoding="utf-8")
    assert (root / "pyproject.toml").read_bytes() == original_pyproject


def test_cli_init_accepts_repeatable_ide_and_generates_only_selected(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "project-ides"
    shutil.copytree(FIXTURE, root)
    monkeypatch.chdir(root)

    result = runner.invoke(
        app,
        ["init", "--profile", "fastapi-backend", "--ide", "codex", "--ide", "cursor"],
    )

    assert result.exit_code == 0, result.stdout
    assert load_manifest(root / ".ai-rules.toml").ides == ["codex", "cursor"]
    assert (root / "AGENTS.md").exists()
    assert (root / ".cursor" / "rules" / "engineering.mdc").exists()
    assert not (root / "CLAUDE.md").exists()
    assert not (root / "GEMINI.md").exists()


def test_cli_invalid_ide_fails_before_project_writes(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "invalid-ide-project"
    shutil.copytree(FIXTURE, root)
    monkeypatch.chdir(root)

    result = runner.invoke(app, ["init", "--profile", "fastapi-backend", "--ide", "vscode"])

    assert result.exit_code == 1
    assert "Supported values" in (result.stdout + result.stderr)
    assert not (root / ".ai-rules.toml").exists()
    assert not (root / ".ai-rules").exists()
    assert not (root / "AGENTS.md").exists()
    assert not (root / "CLAUDE.md").exists()
    assert not (root / "GEMINI.md").exists()
    assert not (root / ".cursor").exists()


def test_cli_bootstrap_invalid_ide_fails_before_global_writes(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))

    result = runner.invoke(app, ["bootstrap", "--ide", "vscode"])

    assert result.exit_code == 1
    assert "Supported values" in (result.stdout + result.stderr)
    assert not home.exists()
