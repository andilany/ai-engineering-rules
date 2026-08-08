from pathlib import Path

from ai_rules.sync import init_project, sync_project

FIXTURES = Path(__file__).parent / "fixtures" / "projects"


def copy_fixture(tmp_path: Path, name: str) -> Path:
    source = FIXTURES / name
    root = tmp_path / name
    root.mkdir()
    for item in source.iterdir():
        if item.is_dir():
            continue
        (root / item.name).write_text(item.read_text(encoding="utf-8"), encoding="utf-8")
    return root


def test_init_then_sync_is_idempotent(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path, "fastapi")
    first = init_project(root, profile="fastapi-backend", dry_run=False)
    assert first.changed
    second = sync_project(root, dry_run=False)
    assert not second.changed


def test_dry_run_does_not_write(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path, "fastapi")
    result = init_project(root, profile="fastapi-backend", dry_run=True)
    assert result.changed
    assert not (root / ".ai-rules.toml").exists()
    assert not (root / "AGENTS.md").exists()


def test_project_override_survives_sync(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path, "fastapi")
    init_project(root, profile="fastapi-backend", dry_run=False)
    project_rules = root / ".ai-rules" / "project.md"
    project_rules.write_text(
        project_rules.read_text() + "\nMy project-specific constraint.\n",
        encoding="utf-8",
    )
    sync_project(root, dry_run=False)
    assert "My project-specific constraint." in project_rules.read_text(encoding="utf-8")


def test_generated_file_contains_rules(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path, "fastapi")
    init_project(root, profile="fastapi-backend", dry_run=False)
    generated = (root / ".ai-rules" / "generated.md").read_text(encoding="utf-8")
    assert "AI Engineering Rules" in generated
    assert "FastAPI" in generated


def test_init_respects_single_ide_selection(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path, "fastapi")
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("codex",))

    assert (root / "AGENTS.md").exists()
    assert not (root / "CLAUDE.md").exists()
    assert not (root / "GEMINI.md").exists()
    assert not (root / ".cursor" / "rules" / "engineering.mdc").exists()
    assert not (root / ".cursor" / "rules" / "airules-000-core.mdc").exists()
    assert (root / ".ai-rules" / "generated.md").exists()
    assert (root / ".ai-rules" / "project.md").exists()


def test_invalid_ide_cli_fails_without_writes(tmp_path: Path) -> None:
    # Covered in CLI-focused tests; keep a project-level guard for write behavior.
    root = copy_fixture(tmp_path, "fastapi")
    from ai_rules.errors import ConfigurationError

    try:
        init_project(root, profile="fastapi-backend", dry_run=False, ides=("unknown",))
    except ConfigurationError:
        pass
    else:
        raise AssertionError("unknown IDE should fail")

    assert not (root / ".ai-rules.toml").exists()
