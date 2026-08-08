from __future__ import annotations

import tomllib

from ai_rules.errors import ConfigurationError
from ai_rules.models import RuleDocument, RuleSeverity
from ai_rules.resources import resource_path


def parse_rule(text: str, path: str) -> RuleDocument:
    if not text.startswith("+++\n"):
        raise ConfigurationError(f"Rule {path} is missing TOML frontmatter")
    try:
        raw_frontmatter, body = text[4:].split("\n+++\n", 1)
    except ValueError as exc:
        raise ConfigurationError(f"Rule {path} has invalid frontmatter delimiters") from exc

    try:
        metadata = tomllib.loads(raw_frontmatter)
        rule_id = str(metadata["id"])
        title = str(metadata["title"])
        severity = RuleSeverity(str(metadata["severity"]))
        scopes = tuple(str(item) for item in metadata.get("scopes", ["all"]))
    except (KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"Rule {path} has invalid metadata: {exc}") from exc

    if not body.strip():
        raise ConfigurationError(f"Rule {path} has an empty body")

    return RuleDocument(
        id=rule_id,
        title=title,
        severity=severity,
        scopes=scopes,
        path=path,
        body=body.strip() + "\n",
    )


def load_rules() -> dict[str, RuleDocument]:
    root = resource_path("rules")
    loaded: dict[str, RuleDocument] = {}
    for category in sorted((item for item in root.iterdir() if item.is_dir()), key=lambda p: p.name):
        for item in sorted(
            (entry for entry in category.iterdir() if entry.name.endswith(".md")),
            key=lambda p: p.name,
        ):
            path = f"rules/{category.name}/{item.name}"
            rule = parse_rule(item.read_text(encoding="utf-8"), path)
            if rule.id in loaded:
                raise ConfigurationError(f"Duplicate rule id: {rule.id}")
            loaded[rule.id] = rule
    return loaded
