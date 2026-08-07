from __future__ import annotations

from ai_rules.managed_blocks import upsert_managed_block

_CONTENT = """@.ai-rules/generated.md
@.ai-rules/project.md"""


def render_claude(existing: str | None) -> str:
    return upsert_managed_block(existing or "", _CONTENT)
