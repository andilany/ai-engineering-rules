from __future__ import annotations

from ai_rules.managed_blocks import upsert_managed_block

_CONTENT = """# Shared AI Engineering Rules

Read and follow `.ai-rules/generated.md` and `.ai-rules/project.md` before making changes in this repository.
Project-specific instructions and explicit user requests take precedence over generic preferences."""


def render_codex(existing: str | None) -> str:
    return upsert_managed_block(existing or "", _CONTENT)
