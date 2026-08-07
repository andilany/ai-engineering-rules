from ai_rules.models import EffectiveRules, RuleDocument, RuleSeverity
from ai_rules.rendering import render_generated_rules


def test_rendering_groups_rules_and_shows_provenance() -> None:
    required = RuleDocument("core.a", "Core A", RuleSeverity.REQUIRED, ("all",), "x", "Required body\n")
    decision = RuleDocument("architecture.choice", "Choice", RuleSeverity.USER_DECISION, ("all",), "y", "Decision body\n")
    preferred = RuleDocument("backend.fastapi", "FastAPI", RuleSeverity.PREFERRED, ("python",), "z", "Preferred body\n")
    effective = EffectiveRules(
        modules=("core.a", "architecture.choice", "backend.fastapi"),
        rules=(required, decision, preferred),
        sources={
            "core.a": "core:required",
            "architecture.choice": "profile:python-backend",
            "backend.fastapi": "profile:fastapi-backend",
        },
    )

    rendered = render_generated_rules(effective, "0.1.0")

    assert rendered.index("## REQUIRED") < rendered.index("## USER_DECISION") < rendered.index("## PREFERRED")
    assert "<!-- source: profile:fastapi-backend; rule: backend.fastapi -->" in rendered
    assert "/mnt/" not in rendered
    assert "This file is generated" in rendered
