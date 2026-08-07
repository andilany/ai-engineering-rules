import shutil
from pathlib import Path

from ai_rules.manifest import load_manifest
from ai_rules.sync import add_selection, init_project, sync_project

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"


def copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    return root


def test_init_detects_fastapi_and_only_creates_airules_files(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    original_pyproject = (root / "pyproject.toml").read_bytes()
    result = init_project(root, profile=None, dry_run=False)

    assert result.selected_profiles[0] == "fastapi-backend"
    assert load_manifest(root / ".ai-rules.toml").profile == "fastapi-backend"
    for path in (
        root / ".ai-rules" / "generated.md",
        root / ".ai-rules" / "project.md",
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / "GEMINI.md",
        root / ".cursor" / "rules" / "engineering.mdc",
    ):
        assert path.exists(), path
    assert (root / "pyproject.toml").read_bytes() == original_pyproject


def test_sync_is_idempotent_and_preserves_project_file(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False)
    project_file = root / ".ai-rules" / "project.md"
    project_file.write_text(project_file.read_text() + "\nCustom constraint.\n", encoding="utf-8")

    first = sync_project(root, dry_run=False)
    second = sync_project(root, dry_run=False)

    assert "Custom constraint." in project_file.read_text(encoding="utf-8")
    assert all(not write.changed for write in second.writes)
    assert first.selected_profiles == second.selected_profiles


def test_add_profile_updates_manifest_and_rules_only(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False)
    original_pyproject = (root / "pyproject.toml").read_bytes()

    add_selection(root, "ml-gpu-service", dry_run=False)
    manifest = load_manifest(root / ".ai-rules.toml")
    generated = (root / ".ai-rules" / "generated.md").read_text(encoding="utf-8")

    assert manifest.extra_profiles == ["ml-gpu-service"]
    assert "# GPU / CUDA" in generated
    assert (root / "pyproject.toml").read_bytes() == original_pyproject
