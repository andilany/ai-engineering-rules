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


def test_bootstrap_codex_only_writes_only_codex(tmp_path: Path) -> None:
    home = tmp_path / "home"
    codex_home = tmp_path / "custom-codex"

    result = bootstrap(home, codex_home=codex_home, dry_run=False, ides=("codex",))

    assert (codex_home / "AGENTS.md").exists()
    assert not (home / ".claude" / "CLAUDE.md").exists()
    assert not (home / ".gemini" / "GEMINI.md").exists()
    assert not (home / ".ai-rules" / "cursor-user-rules.txt").exists()
    assert result.cursor_note == ""


def test_bootstrap_cursor_only_writes_helper_and_returns_note(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = bootstrap(home, codex_home=None, dry_run=False, ides=("cursor",))

    cursor = home / ".ai-rules" / "cursor-user-rules.txt"
    assert cursor.exists()
    assert not (home / ".codex" / "AGENTS.md").exists()
    assert not (home / ".claude" / "CLAUDE.md").exists()
    assert not (home / ".gemini" / "GEMINI.md").exists()
    assert "Cursor" in result.cursor_note


def test_bootstrap_multiple_ides_only_writes_selected_targets(tmp_path: Path) -> None:
    home = tmp_path / "home"

    bootstrap(home, codex_home=None, dry_run=False, ides=("claude", "gemini"))

    assert (home / ".claude" / "CLAUDE.md").exists()
    assert (home / ".gemini" / "GEMINI.md").exists()
    assert not (home / ".codex" / "AGENTS.md").exists()
    assert not (home / ".ai-rules" / "cursor-user-rules.txt").exists()
