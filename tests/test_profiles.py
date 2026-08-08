import pytest

from ai_rules.errors import ConfigurationError
from ai_rules.models import ProfileDefinition
from ai_rules.profiles import resolve_profile


def test_resolve_profile_includes_parent_before_child_modules() -> None:
    profiles = {
        "base": ProfileDefinition("base", "", (), ("core.agent-behavior",)),
        "api": ProfileDefinition("api", "", ("base",), ("backend.fastapi",)),
    }

    assert resolve_profile("api", profiles) == (
        "core.agent-behavior",
        "backend.fastapi",
    )


def test_resolve_profile_rejects_cycles() -> None:
    profiles = {
        "a": ProfileDefinition("a", "", ("b",), ()),
        "b": ProfileDefinition("b", "", ("a",), ()),
    }

    with pytest.raises(ConfigurationError, match="cycle"):
        resolve_profile("a", profiles)
