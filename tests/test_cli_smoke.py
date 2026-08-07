from typer.testing import CliRunner

from ai_rules.cli import app

runner = CliRunner()


def test_cli_exposes_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "airules" in result.stdout
