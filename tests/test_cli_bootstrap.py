from pathlib import Path

from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner()


def test_cli_bootstrap_dry_run_uses_home(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("CODEX_HOME", raising=False)

    result = runner.invoke(app, ["bootstrap", "--dry-run"])

    assert result.exit_code == 0, result.stdout
    assert "Cursor" in result.stdout
    assert not home.exists()


def test_cli_bootstrap_copilot_honors_copilot_home(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    copilot_home = tmp_path / "copilot-home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("COPILOT_HOME", str(copilot_home))

    result = runner.invoke(app, ["bootstrap", "--ide", "copilot"])

    assert result.exit_code == 0, result.stdout
    assert (copilot_home / "copilot-instructions.md").exists()
    assert not (home / ".codex" / "AGENTS.md").exists()
