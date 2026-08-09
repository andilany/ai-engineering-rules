from __future__ import annotations

from ai_rules.adapters.native import group_effective_rules, render_group_markdown
from ai_rules.models import EffectiveRules

OWNER = "<!-- ai-engineering-rules:owned -->"


def _owned_mdc(description: str, body: str) -> str:
    return (
        "---\n"
        f"description: {description}\n"
        "globs:\n"
        "alwaysApply: true\n"
        "---\n\n"
        f"{OWNER}\n\n"
        f"{body.rstrip()}\n"
    )


def render_cursor_native(effective: EffectiveRules, project_text: str) -> dict[str, str]:
    rendered: dict[str, str] = {}
    for group in group_effective_rules(effective):
        rendered[f"airules-{group.key}.mdc"] = _owned_mdc(
            f"airules {group.title} engineering rules",
            render_group_markdown(group, effective),
        )
    rendered["airules-999-project.mdc"] = _owned_mdc(
        "Project-specific instructions managed through .ai-rules/project.md",
        project_text,
    )
    return rendered


def is_owned_cursor_rule(content: str | None) -> bool:
    return content is not None and OWNER in content
