import hashlib
import shutil
from pathlib import Path

from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.sync import init_project

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"
runner = CliRunner()


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_readonly_commands_do_not_modify_project(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False)
    monkeypatch.chdir(root)
    before = tree_hash(root)

    for command in (["detect"], ["explain"], ["doctor"]):
        result = runner.invoke(app, command)
        assert result.exit_code == 0, result.stdout
        assert tree_hash(root) == before
