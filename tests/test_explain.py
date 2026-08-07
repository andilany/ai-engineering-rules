import shutil
from pathlib import Path

from ai_rules.explain import explain_project
from ai_rules.sync import init_project

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"


def test_explain_shows_severity_and_provenance(tmp_path: Path) -> None:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    init_project(root, profile="fastapi-backend", dry_run=False)

    output = explain_project(root)

    assert "REQUIRED" in output
    assert "core.agent-behavior" in output
    assert "core:required" in output
    assert "PREFERRED" in output
    assert "backend.fastapi" in output
