from __future__ import annotations

from ai_rules.adapters.native import group_effective_rules, render_group_markdown
from ai_rules.managed_blocks import upsert_managed_block
from ai_rules.models import EffectiveRules

OWNER = "<!-- ai-engineering-rules:owned -->"
_CONTENT = """# airules project instructions

@.ai-rules/project.md"""


def render_claude(existing: str | None) -> str:
    return upsert_managed_block(existing or "", _CONTENT)


def render_claude_native(effective: EffectiveRules) -> dict[str, str]:
    rendered: dict[str, str] = {}
    for group in group_effective_rules(effective):
        rendered[f"{group.key}.md"] = (
            f"{OWNER}\n" + render_group_markdown(group, effective)
        )
    return rendered


def is_owned_claude_rule(content: str | None) -> bool:
    return content is not None and OWNER in content
