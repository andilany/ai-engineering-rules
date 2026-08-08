from ai_rules.rules import load_rules


def test_packaged_rules_are_discoverable() -> None:
    rules = load_rules()

    assert "core.agent-behavior" in rules
    assert "core.external-actions" in rules
