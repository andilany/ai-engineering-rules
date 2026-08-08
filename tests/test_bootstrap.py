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

    assert (home / ".claude" / "rules" / "airules" / "000-core.md").exists()
    assert not (home / ".claude" / "CLAUDE.md").exists()
    assert (home / ".gemini" / "GEMINI.md").exists()
    assert not (home / ".codex" / "AGENTS.md").exists()
    assert not (home / ".ai-rules" / "cursor-user-rules.txt").exists()


def test_bootstrap_claude_uses_native_user_rules_directory(tmp_path: Path) -> None:
    home = tmp_path / "home"

    bootstrap(home, codex_home=None, copilot_home=None, dry_run=False, ides=("claude",))

    native = home / ".claude" / "rules" / "airules" / "000-core.md"
    assert native.exists()
    assert "Universal AI Engineering Core" in native.read_text(encoding="utf-8")
    assert not (home / ".claude" / "CLAUDE.md").exists()


def test_bootstrap_copilot_uses_user_level_instructions_file(tmp_path: Path) -> None:
    home = tmp_path / "home"
    copilot_home = tmp_path / "custom-copilot"

    bootstrap(
        home,
        codex_home=None,
        copilot_home=copilot_home,
        dry_run=False,
        ides=("copilot",),
    )

    target = copilot_home / "copilot-instructions.md"
    assert target.exists()
    assert "Universal AI Engineering Core" in target.read_text(encoding="utf-8")
    assert not (home / ".codex" / "AGENTS.md").exists()
    assert not (home / ".ai-rules" / "cursor-user-rules.txt").exists()
