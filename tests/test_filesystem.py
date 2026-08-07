from pathlib import Path

import pytest

from ai_rules.errors import SafetyError
from ai_rules.filesystem import WriteScope, apply_writes, plan_write


def test_dry_run_reports_change_without_writing(tmp_path: Path) -> None:
    path = tmp_path / ".ai-rules" / "generated.md"
    write = plan_write(path, "content\n")
    scope = WriteScope(root=tmp_path, allowed_prefixes=(tmp_path / ".ai-rules",))

    applied = apply_writes((write,), dry_run=True, scope=scope)

    assert applied[0].changed is True
    assert not path.exists()


def test_real_write_is_atomic_and_unchanged_content_is_noop(tmp_path: Path) -> None:
    path = tmp_path / "AGENTS.md"
    scope = WriteScope(root=tmp_path, allowed_exact=frozenset({path}))
    first = apply_writes((plan_write(path, "hello\n"),), dry_run=False, scope=scope)
    second = apply_writes((plan_write(path, "hello\n"),), dry_run=False, scope=scope)

    assert first[0].changed is True
    assert second[0].changed is False
    assert path.read_text(encoding="utf-8") == "hello\n"
    assert not list(tmp_path.glob(".airules-*.tmp"))


def test_write_outside_scope_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "application.py"
    scope = WriteScope(root=tmp_path, allowed_exact=frozenset({tmp_path / "AGENTS.md"}))
    with pytest.raises(SafetyError):
        apply_writes((plan_write(outside, "bad"),), dry_run=False, scope=scope)
