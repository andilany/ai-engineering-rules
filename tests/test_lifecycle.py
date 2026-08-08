from __future__ import annotations

import shutil
from pathlib import Path

from ai_rules.lifecycle import configure_project, uninstall_project
from ai_rules.manifest import load_manifest
from ai_rules.sync import init_project
from ai_rules.wizard import WizardSelection, build_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "projects" / "fastapi"


def copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    return root


def test_uninstall_preserves_project_rules_and_unrelated_content(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("codex", "cursor"))
    project_rules = root / ".ai-rules" / "project.md"
    project_rules.write_text("User-specific constraint.\n", encoding="utf-8")
    agents = root / "AGENTS.md"
    agents.write_text("User preface.\n" + agents.read_text(encoding="utf-8"), encoding="utf-8")
    foreign_cursor = root / ".cursor" / "rules" / "team.mdc"
    foreign_cursor.write_text("user owned\n", encoding="utf-8")

    preview = uninstall_project(root, purge=False, dry_run=True)
    assert (root / ".ai-rules.toml").exists()
    assert any(item.path == root / ".ai-rules.toml" and item.changed for item in preview.deletes)

    uninstall_project(root, purge=False, dry_run=False)

    assert not (root / ".ai-rules.toml").exists()
    assert not (root / ".ai-rules" / "generated.md").exists()
    assert project_rules.read_text(encoding="utf-8") == "User-specific constraint.\n"
    assert agents.read_text(encoding="utf-8") == "User preface.\n"
    assert foreign_cursor.read_text(encoding="utf-8") == "user owned\n"
    assert not list((root / ".cursor" / "rules").glob("airules-*.mdc"))


def test_uninstall_purge_deletes_project_rules(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("cursor",))

    uninstall_project(root, purge=True, dry_run=False)

    assert not (root / ".ai-rules" / "project.md").exists()


def test_reconfigure_replaces_old_selection_and_preserves_project_rules(tmp_path: Path) -> None:
    root = copy_fixture(tmp_path)
    init_project(root, profile="fastapi-backend", dry_run=False, ides=("codex", "claude"))
    project_rules = root / ".ai-rules" / "project.md"
    project_rules.write_text("Keep this project rule.\n", encoding="utf-8")
    manifest = build_manifest(
        WizardSelection(
            ides=("cursor",),
            frontend=("nextjs", "tailwind"),
        ),
        rules_version="0.3.1",
    )

    configure_project(root, manifest, dry_run=False, replace_existing=True)

    loaded = load_manifest(root / ".ai-rules.toml")
    assert loaded.profile == "custom"
    assert loaded.ides == ["cursor"]
    assert loaded.backend == {}
    assert loaded.frontend == {"nextjs": True}
    assert loaded.include_modules == [
        "frontend.typescript",
        "frontend.react",
        "frontend.tailwind",
    ]
    assert project_rules.read_text(encoding="utf-8") == "Keep this project rule.\n"
    assert not (root / "AGENTS.md").exists()
    assert not (root / "CLAUDE.md").exists()
    assert (root / ".cursor" / "rules" / "airules-000-core.mdc").exists()
