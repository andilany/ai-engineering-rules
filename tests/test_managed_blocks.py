import pytest

from ai_rules.errors import ConfigurationError
from ai_rules.managed_blocks import remove_managed_block, upsert_managed_block


def test_empty_file_gets_one_managed_block() -> None:
    result = upsert_managed_block("", "generated")
    assert result.count("<!-- ai-engineering-rules:start -->") == 1
    assert "generated" in result


def test_user_text_is_preserved_around_block() -> None:
    existing = "before\n<!-- ai-engineering-rules:start -->\nold\n<!-- ai-engineering-rules:end -->\nafter\n"
    result = upsert_managed_block(existing, "new")
    assert result.startswith("before\n")
    assert result.endswith("after\n")
    assert "old" not in result
    assert "new" in result


def test_duplicate_markers_are_rejected() -> None:
    existing = "<!-- ai-engineering-rules:start -->\na\n<!-- ai-engineering-rules:start -->\n"
    with pytest.raises(ConfigurationError, match="markers"):
        upsert_managed_block(existing, "new")


def test_upsert_is_idempotent() -> None:
    once = upsert_managed_block("user\n", "generated")
    twice = upsert_managed_block(once, "generated")
    assert once == twice


def test_remove_preserves_user_text() -> None:
    existing = upsert_managed_block("before\nafter\n", "generated")
    result = remove_managed_block(existing)
    assert result == "before\nafter\n"
