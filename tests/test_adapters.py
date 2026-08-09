from ai_rules.adapters.claude import render_claude
from ai_rules.adapters.codex import render_codex
from ai_rules.adapters.gemini import render_gemini


def test_text_adapters_preserve_user_content() -> None:
    existing = "# User instructions\nKeep this.\n"
    for render in (render_codex, render_claude, render_gemini):
        result = render(existing)
        assert "# User instructions\nKeep this.\n" in result
        assert result.count("<!-- ai-engineering-rules:start -->") == 1


def _rule(rule_id: str, severity, body: str = "body"):
    from ai_rules.models import RuleDocument

    return RuleDocument(
        id=rule_id,
        title=rule_id,
        severity=severity,
        scopes=(),
        path=f"rules/{rule_id}.md",
        body=body,
    )


def test_native_grouping_is_stable_and_omits_empty_groups() -> None:
    from ai_rules.adapters.native import group_effective_rules
    from ai_rules.models import EffectiveRules, RuleSeverity

    rules = (
        _rule("core.workflow", RuleSeverity.REQUIRED),
        _rule("security.auth", RuleSeverity.REQUIRED),
        _rule("quality.pytest", RuleSeverity.PREFERRED),
        _rule("backend.fastapi", RuleSeverity.PREFERRED),
        _rule("data.postgresql", RuleSeverity.PREFERRED),
        _rule("messaging.rabbitmq", RuleSeverity.PREFERRED),
        _rule("ml.gpu-cuda", RuleSeverity.CONDITIONAL),
        _rule("infrastructure.docker", RuleSeverity.PREFERRED),
    )
    effective = EffectiveRules(
        modules=tuple(rule.id for rule in rules),
        rules=rules,
        sources={rule.id: "profile:test" for rule in rules},
    )

    groups = group_effective_rules(effective)

    assert [group.key for group in groups] == [
        "000-core",
        "200-security-quality",
        "300-language-backend",
        "400-data-messaging",
        "600-ml-infrastructure",
    ]
    assert [rule.id for rule in groups[1].rules] == ["security.auth", "quality.pytest"]
    assert [rule.id for rule in groups[4].rules] == [
        "ml.gpu-cuda",
        "infrastructure.docker",
    ]


def test_native_group_rendering_preserves_provenance_and_rule_order() -> None:
    from ai_rules.adapters.native import group_effective_rules, render_group_markdown
    from ai_rules.models import EffectiveRules, RuleSeverity

    rules = (
        _rule("core.workflow", RuleSeverity.REQUIRED, "# Workflow\nRequired body."),
        _rule("core.documentation", RuleSeverity.PREFERRED, "# Documentation\nPreferred body."),
    )
    effective = EffectiveRules(
        modules=tuple(rule.id for rule in rules),
        rules=rules,
        sources={
            "core.workflow": "core:required",
            "core.documentation": "profile:python-backend",
        },
    )
    group = group_effective_rules(effective)[0]

    rendered = render_group_markdown(group, effective)

    assert rendered.index("core.workflow") < rendered.index("core.documentation")
    assert "source: core:required; rule: core.workflow" in rendered
    assert "source: profile:python-backend; rule: core.documentation" in rendered


def _effective_for_native_adapters():
    from ai_rules.models import EffectiveRules, RuleSeverity

    rules = (
        _rule("core.workflow", RuleSeverity.REQUIRED, "# Workflow\nDo workflow."),
        _rule("security.auth", RuleSeverity.REQUIRED, "# Auth\nDo auth."),
        _rule("backend.fastapi", RuleSeverity.PREFERRED, "# FastAPI\nDo API."),
        _rule("ml.gpu-cuda", RuleSeverity.CONDITIONAL, "# GPU / CUDA\nDo GPU."),
    )
    return EffectiveRules(
        modules=tuple(rule.id for rule in rules),
        rules=rules,
        sources={rule.id: "profile:test" for rule in rules},
    )


def test_cursor_native_rules_embed_canonical_content_without_parent_references() -> None:
    from ai_rules.adapters.cursor import render_cursor_native

    rendered = render_cursor_native(_effective_for_native_adapters(), "# Project\nKeep contract.\n")

    assert set(rendered) == {
        "airules-000-core.mdc",
        "airules-200-security-quality.mdc",
        "airules-300-language-backend.mdc",
        "airules-600-ml-infrastructure.mdc",
        "airules-999-project.mdc",
    }
    assert "alwaysApply: true" in rendered["airules-000-core.mdc"]
    assert "# Workflow" in rendered["airules-000-core.mdc"]
    assert "# Project\nKeep contract." in rendered["airules-999-project.mdc"]
    assert "../../" not in "\n".join(rendered.values())
    assert "@.ai-rules/generated.md" not in "\n".join(rendered.values())
    assert all("ai-engineering-rules:owned" in content for content in rendered.values())


def test_claude_native_rules_and_root_entrypoint_do_not_duplicate_generated_snapshot() -> None:
    from ai_rules.adapters.claude import render_claude, render_claude_native

    native = render_claude_native(_effective_for_native_adapters())
    root = render_claude("# User Claude\n")

    assert set(native) == {
        "000-core.md",
        "200-security-quality.md",
        "300-language-backend.md",
        "600-ml-infrastructure.md",
    }
    assert all("ai-engineering-rules:owned" in content for content in native.values())
    assert "@.ai-rules/project.md" in root
    assert "generated.md" not in root
    assert "# User Claude" in root


def test_copilot_native_rules_use_official_repository_instruction_layout() -> None:
    from ai_rules.adapters.copilot import render_copilot, render_copilot_native

    native = render_copilot_native(_effective_for_native_adapters())
    root = render_copilot("# User Copilot\n", "# Project\nProject rule.\n")

    assert set(native) == {
        "000-core.instructions.md",
        "200-security-quality.instructions.md",
        "300-language-backend.instructions.md",
        "600-ml-infrastructure.instructions.md",
    }
    assert all('applyTo: "**"' in content for content in native.values())
    assert all("ai-engineering-rules:owned" in content for content in native.values())
    assert ".github/instructions/airules" in root
    assert "Project rule." in root
    assert "# User Copilot" in root


def test_supported_ides_include_copilot() -> None:
    from ai_rules.ides import SUPPORTED_IDES, normalize_ides

    assert "copilot" in SUPPORTED_IDES
    assert normalize_ides(("copilot",), default_all=False) == ("copilot",)
