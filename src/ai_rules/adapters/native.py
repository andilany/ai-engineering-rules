from __future__ import annotations

from dataclasses import dataclass

from ai_rules.models import EffectiveRules, RuleDocument


@dataclass(frozen=True, slots=True)
class NativeRuleGroup:
    key: str
    title: str
    rules: tuple[RuleDocument, ...]


_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("000-core", "Core", ("core",)),
    ("100-architecture", "Architecture", ("architecture",)),
    ("200-security-quality", "Security & Quality", ("security", "quality")),
    ("300-language-backend", "Language & Backend", ("languages", "backend")),
    ("400-data-messaging", "Data & Messaging", ("data", "messaging")),
    ("500-frontend", "Frontend", ("frontend",)),
    ("600-ml-infrastructure", "ML & Infrastructure", ("ml", "infrastructure")),
)


def group_effective_rules(effective: EffectiveRules) -> tuple[NativeRuleGroup, ...]:
    groups: list[NativeRuleGroup] = []
    for key, title, prefixes in _GROUPS:
        selected = tuple(
            rule for rule in effective.rules if rule.id.split(".", 1)[0] in prefixes
        )
        if selected:
            groups.append(NativeRuleGroup(key=key, title=title, rules=selected))
    return tuple(groups)


def render_group_markdown(group: NativeRuleGroup, effective: EffectiveRules) -> str:
    lines = [f"# {group.title}", ""]
    for rule in group.rules:
        source = effective.sources.get(rule.id, "unknown")
        lines.append(f"<!-- source: {source}; rule: {rule.id} -->")
        lines.append(rule.body.rstrip())
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
