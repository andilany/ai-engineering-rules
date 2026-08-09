from pathlib import Path

import pytest

from ai_rules.bootstrap import BOOTSTRAP_IDES, bootstrap
from ai_rules.errors import ConfigurationError


def test_bootstrap_writes_only_supported_global_targets(tmp_path: Path) -> None:
    home = tmp_path / "home"
    codex_home = tmp_path / "custom-codex"
    claude = home / ".claude" / "CLAUDE.md"
    claude.parent.mkdir(parents=True)
    claude.write_text("# My Claude rules\n", encoding="utf-8")

    result = bootstrap(home, codex_home=codex_home, dry_run=False)

    assert "cursor" not in BOOTSTRAP_IDES
    assert (codex_home / "AGENTS.md").exists()
    assert (home / ".gemini" / "GEMINI.md").exists()
    assert "# My Claude rules\n" in claude.read_text(encoding="utf-8")
    assert not (home / ".ai-rules" / "cursor-user-rules.txt").exists()
    assert all("fastapi" not in write.content.lower() for write in result.writes)


def test_bootstrap_dry_run_writes_nothing(tmp_path: Path) -> None:
    home = tmp_path / "home"
    result = bootstrap(home, codex_home=None, dry_run=True)
    assert any(write.changed for write in result.writes)
    assert not home.exists()


def test_bootstrap_codex_only_writes_only_codex(tmp_path: Path) -> None:
    home = tmp_path / "home"
    codex_home = tmp_path / "custom-codex"

    bootstrap(home, codex_home=codex_home, dry_run=False, ides=("codex",))

    assert (codex_home / "AGENTS.md").exists()
    assert not (home / ".claude" / "CLAUDE.md").exists()
    assert not (home / ".gemini" / "GEMINI.md").exists()
    assert not (home / ".ai-rules" / "cursor-user-rules.txt").exists()


def test_bootstrap_rejects_cursor_global_target(tmp_path: Path) -> None:
    home = tmp_path / "home"

    with pytest.raises(ConfigurationError, match="airules init --ide cursor"):
        bootstrap(home, codex_home=None, dry_run=False, ides=("cursor",))

    assert not home.exists()


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
