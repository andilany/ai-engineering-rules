from __future__ import annotations

from pathlib import Path

from ai_rules.manifest import load_manifest
from ai_rules.models import RuleSeverity
from ai_rules.precedence import compose_effective_rules
from ai_rules.profiles import load_profiles
from ai_rules.project import ProjectPaths
from ai_rules.rules import load_rules

_ORDER = (
    RuleSeverity.REQUIRED,
    RuleSeverity.USER_DECISION,
    RuleSeverity.PREFERRED,
    RuleSeverity.CONDITIONAL,
    RuleSeverity.OPTIONAL,
)


def explain_project(root: Path) -> str:
    paths = ProjectPaths(root.resolve())
    manifest = load_manifest(paths.manifest)
    effective = compose_effective_rules(manifest, load_profiles(validate_modules=True), load_rules())
    lines: list[str] = []
    for severity in _ORDER:
        group = [rule for rule in effective.rules if rule.severity is severity]
        if not group:
            continue
        lines.append(severity.name)
        for rule in group:
            lines.append(f"  {rule.id}   {effective.sources.get(rule.id, 'unknown')}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
