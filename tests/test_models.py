from ai_rules.models import DetectionConfidence, RuleSeverity


def test_rule_severity_order_is_explicit() -> None:
    assert RuleSeverity.REQUIRED.rank > RuleSeverity.PREFERRED.rank
    assert RuleSeverity.PREFERRED.rank > RuleSeverity.CONDITIONAL.rank
    assert RuleSeverity.CONDITIONAL.rank > RuleSeverity.OPTIONAL.rank
    assert RuleSeverity.USER_DECISION.rank == RuleSeverity.PREFERRED.rank


def test_detection_confidence_values_are_stable() -> None:
    assert [item.value for item in DetectionConfidence] == [
        "detected",
        "probable",
        "not_detected",
    ]
