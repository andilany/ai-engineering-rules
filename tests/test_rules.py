import pytest

from ai_rules.errors import ConfigurationError
from ai_rules.models import RuleSeverity
from ai_rules.rules import parse_rule


VALID = '''+++
id = "core.agent-behavior"
title = "Agent Behavior"
severity = "required"
scopes = ["all"]
+++
# Agent Behavior

- Preserve project reality.
'''


def test_parse_rule_reads_toml_frontmatter() -> None:
    rule = parse_rule(VALID, "rules/core/agent-behavior.md")

    assert rule.id == "core.agent-behavior"
    assert rule.severity is RuleSeverity.REQUIRED
    assert rule.scopes == ("all",)
    assert "Preserve project reality" in rule.body


def test_parse_rule_rejects_missing_frontmatter() -> None:
    with pytest.raises(ConfigurationError, match="frontmatter"):
        parse_rule("# plain markdown", "broken.md")
