from pathlib import Path

from ai_rules.project import ProjectPaths, find_project_root


def test_find_project_root_uses_nearest_git_ancestor(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (repo / ".git").mkdir()
    assert find_project_root(nested) == repo.resolve()


def test_project_paths_are_fixed(tmp_path: Path) -> None:
    paths = ProjectPaths(tmp_path)
    assert paths.manifest == tmp_path / ".ai-rules.toml"
    assert paths.generated == tmp_path / ".ai-rules" / "generated.md"
    assert paths.cursor_rules_dir == tmp_path / ".cursor" / "rules"
    assert paths.legacy_cursor_rule == tmp_path / ".cursor" / "rules" / "engineering.mdc"
