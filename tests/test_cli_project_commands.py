import shutil
from pathlib import Path

from typer.testing import CliRunner

from ai_rules.cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"
runner = CliRunner()


def test_cli_init_sync_add(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    monkeypatch.chdir(root)

    assert runner.invoke(app, ["init", "--profile", "fastapi-backend"]).exit_code == 0
    assert runner.invoke(app, ["sync"]).exit_code == 0
    assert runner.invoke(app, ["add", "ml-gpu-service"]).exit_code == 0
