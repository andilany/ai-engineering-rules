import pytest

from ai_rules.errors import ConfigurationError
from ai_rules.models import ProfileDefinition, ProjectManifest, RuleDocument, RuleSeverity
from ai_rules.precedence import compose_effective_rules


def rule(rule_id: str, severity: RuleSeverity) -> RuleDocument:
    return RuleDocument(rule_id, rule_id, severity, ("all",), f"rules/{rule_id}.md", rule_id)


def test_composition_orders_by_severity_and_preserves_user_decision() -> None:
    rules = {
        "core.agent-behavior": rule("core.agent-behavior", RuleSeverity.REQUIRED),
        "core.external-actions": rule("core.external-actions", RuleSeverity.REQUIRED),
        "architecture.choice": rule("architecture.choice", RuleSeverity.USER_DECISION),
        "backend.fastapi": rule("backend.fastapi", RuleSeverity.PREFERRED),
        "data.redis": rule("data.redis", RuleSeverity.CONDITIONAL),
    }
    profiles = {
        "base": ProfileDefinition(
            "base", "", (), ("backend.fastapi", "architecture.choice", "data.redis")
        )
    }

    effective = compose_effective_rules(ProjectManifest(profile="base"), profiles, rules)

    assert [item.severity for item in effective.rules] == [
        RuleSeverity.REQUIRED,
        RuleSeverity.REQUIRED,
        RuleSeverity.USER_DECISION,
        RuleSeverity.PREFERRED,
        RuleSeverity.CONDITIONAL,
    ]


def test_required_core_modules_cannot_be_excluded() -> None:
    rules = {
        "core.agent-behavior": rule("core.agent-behavior", RuleSeverity.REQUIRED),
        "core.external-actions": rule("core.external-actions", RuleSeverity.REQUIRED),
    }
    profiles = {"base": ProfileDefinition("base", "", (), ())}
    manifest = ProjectManifest(profile="base", exclude_modules=["core.agent-behavior"])

    with pytest.raises(ConfigurationError, match="required core"):
        compose_effective_rules(manifest, profiles, rules)
