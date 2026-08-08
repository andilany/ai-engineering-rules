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


def test_init_with_codex_only_creates_shared_files_and_codex_adapter(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)

    init_project(root, profile="fastapi-backend", dry_run=False, ides=("codex",))

    manifest = load_manifest(root / ".ai-rules.toml")
    assert manifest.ides == ["codex"]
    assert (root / ".ai-rules" / "generated.md").exists()
    assert (root / ".ai-rules" / "project.md").exists()
    assert (root / "AGENTS.md").exists()
    assert not (root / "CLAUDE.md").exists()
    assert not (root / "GEMINI.md").exists()
    assert not (root / ".cursor" / "rules" / "engineering.mdc").exists()


def test_init_with_multiple_ides_persists_order_and_only_selected_adapters(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)

    init_project(
        root,
        profile="fastapi-backend",
        dry_run=False,
        ides=("cursor", "codex", "cursor"),
    )

    manifest = load_manifest(root / ".ai-rules.toml")
    assert manifest.ides == ["cursor", "codex"]
    assert (root / "AGENTS.md").exists()
    assert (root / ".cursor" / "rules" / "engineering.mdc").exists()
    assert not (root / "CLAUDE.md").exists()
    assert not (root / "GEMINI.md").exists()


def test_sync_respects_persisted_ides(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("codex",))

    sync_project(root, dry_run=False)

    assert (root / "AGENTS.md").exists()
    assert not (root / "CLAUDE.md").exists()
    assert not (root / "GEMINI.md").exists()
    assert not (root / ".cursor" / "rules" / "engineering.mdc").exists()


def test_sync_ide_override_is_temporary_and_does_not_modify_manifest(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("codex",))
    manifest_before = (root / ".ai-rules.toml").read_text(encoding="utf-8")

    sync_project(root, dry_run=False, ides=("claude",))

    assert (root / "CLAUDE.md").exists()
    assert load_manifest(root / ".ai-rules.toml").ides == ["codex"]
    assert (root / ".ai-rules.toml").read_text(encoding="utf-8") == manifest_before


def test_sync_reduced_selection_does_not_touch_unselected_adapter(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("codex", "claude"))
    claude = root / "CLAUDE.md"
    claude.write_text(
        claude.read_text(encoding="utf-8") + "\nUser Claude content.\n",
        encoding="utf-8",
    )
    before = claude.read_bytes()

    sync_project(root, dry_run=False, ides=("codex",))

    assert claude.read_bytes() == before


def test_legacy_manifest_without_ides_syncs_all_adapters(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("codex",))
    manifest_path = root / ".ai-rules.toml"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(
        "\n".join(
            line for line in manifest_text.splitlines() if not line.startswith("ides =")
        )
        + "\n",
        encoding="utf-8",
    )
    for path in (
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / "GEMINI.md",
        root / ".cursor" / "rules" / "engineering.mdc",
    ):
        if path.exists():
            path.unlink()

    sync_project(root, dry_run=False)

    assert (root / "AGENTS.md").exists()
    assert (root / "CLAUDE.md").exists()
    assert (root / "GEMINI.md").exists()
    assert (root / ".cursor" / "rules" / "engineering.mdc").exists()
