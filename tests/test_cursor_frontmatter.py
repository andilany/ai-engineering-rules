from ai_rules.adapters.cursor import OWNER, render_cursor_native
from ai_rules.models import EffectiveRules, RuleDocument, RuleSeverity


def test_cursor_native_mdc_starts_with_frontmatter_before_owner_marker() -> None:
    rule = RuleDocument(
        id="core.workflow",
        title="Workflow",
        severity=RuleSeverity.REQUIRED,
        scopes=(),
        path="rules/core/workflow.md",
        body="# Workflow\nDo workflow.",
    )
    effective = EffectiveRules(
        modules=(rule.id,),
        rules=(rule,),
        sources={rule.id: "core:required"},
    )

    rendered = render_cursor_native(effective, "# Project\nKeep contract.\n")

    for content in rendered.values():
        lines = content.splitlines()
        assert lines[0] == "---"
        assert lines[2] == "globs:"
        assert lines[3] == "alwaysApply: true"
        assert lines[4] == "---"
        assert lines[5] == ""
        assert lines[6] == OWNER
