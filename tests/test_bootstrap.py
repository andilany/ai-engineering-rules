from pathlib import Path

from ai_rules.bootstrap import bootstrap


def test_bootstrap_writes_only_global_core_and_preserves_content(tmp_path: Path) -> None:
    home = tmp_path / "home"
    codex_home = tmp_path / "custom-codex"
    claude = home / ".claude" / "CLAUDE.md"
    claude.parent.mkdir(parents=True)
    claude.write_text("# My Claude rules\n", encoding="utf-8")

    result = bootstrap(home, codex_home=codex_home, dry_run=False)

    assert (codex_home / "AGENTS.md").exists()
    assert (home / ".gemini" / "GEMINI.md").exists()
    assert "# My Claude rules\n" in claude.read_text(encoding="utf-8")
    cursor = home / ".ai-rules" / "cursor-user-rules.txt"
    assert cursor.exists()
    assert "Cursor Settings > Rules > User Rules" in cursor.read_text(encoding="utf-8")
    assert all("fastapi" not in write.content.lower() for write in result.writes)


def test_bootstrap_dry_run_writes_nothing(tmp_path: Path) -> None:
    home = tmp_path / "home"
    result = bootstrap(home, codex_home=None, dry_run=True)
    assert any(write.changed for write in result.writes)
    assert not home.exists()
