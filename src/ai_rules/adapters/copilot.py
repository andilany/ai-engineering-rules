from __future__ import annotations

from ai_rules.adapters.native import group_effective_rules, render_group_markdown
from ai_rules.managed_blocks import upsert_managed_block
from ai_rules.models import EffectiveRules

OWNER = "<!-- ai-engineering-rules:owned -->"


def render_copilot(existing: str | None, project_text: str) -> str:
    body = """# airules repository instructions

Canonical engineering instructions are provided by `.github/instructions/airules/`.
The project-specific instructions below are sourced from `.ai-rules/project.md`.

## Project-specific instructions

""" + project_text.rstrip()
    return upsert_managed_block(existing or "", body)


def render_copilot_native(effective: EffectiveRules) -> dict[str, str]:
    rendered: dict[str, str] = {}
    for group in group_effective_rules(effective):
        rendered[f"{group.key}.instructions.md"] = (
            f"{OWNER}\n"
            "---\n"
            'applyTo: "**"\n'
            "---\n\n"
            + render_group_markdown(group, effective)
        )
    return rendered


def is_owned_copilot_rule(content: str | None) -> bool:
    return content is not None and OWNER in content
