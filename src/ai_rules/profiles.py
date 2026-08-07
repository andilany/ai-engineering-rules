from __future__ import annotations

import tomllib
from collections.abc import Mapping

from ai_rules.errors import ConfigurationError
from ai_rules.models import ProfileDefinition
from ai_rules.resources import resource_path
from ai_rules.rules import load_rules


def load_profiles(*, validate_modules: bool = True) -> dict[str, ProfileDefinition]:
    root = resource_path("profiles")
    profiles: dict[str, ProfileDefinition] = {}
    if not root.is_dir():
        return profiles
    for item in sorted(
        (entry for entry in root.iterdir() if entry.name.endswith(".toml")), key=lambda p: p.name
    ):
        try:
            data = tomllib.loads(item.read_text(encoding="utf-8"))
            profile = ProfileDefinition(
                name=str(data["name"]),
                description=str(data.get("description", "")),
                extends=tuple(str(value) for value in data.get("extends", [])),
                modules=tuple(str(value) for value in data.get("modules", [])),
            )
        except (KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
            raise ConfigurationError(f"Invalid profile {item.name}: {exc}") from exc
        if profile.name in profiles:
            raise ConfigurationError(f"Duplicate profile name: {profile.name}")
        profiles[profile.name] = profile

    for name in profiles:
        resolve_profile(name, profiles)

    if validate_modules:
        rule_ids = set(load_rules())
        for profile in profiles.values():
            missing = [module for module in profile.modules if module not in rule_ids]
            if missing:
                raise ConfigurationError(
                    f"Profile {profile.name} references unknown modules: {', '.join(missing)}"
                )
    return profiles


def resolve_profile(
    name: str,
    profiles: Mapping[str, ProfileDefinition],
    *,
    _visiting: tuple[str, ...] = (),
) -> tuple[str, ...]:
    if name not in profiles:
        raise ConfigurationError(f"Unknown profile: {name}")
    if name in _visiting:
        chain = " -> ".join((*_visiting, name))
        raise ConfigurationError(f"Profile inheritance cycle: {chain}")

    profile = profiles[name]
    resolved: list[str] = []
    for parent in profile.extends:
        for module in resolve_profile(parent, profiles, _visiting=(*_visiting, name)):
            if module not in resolved:
                resolved.append(module)
    for module in profile.modules:
        if module not in resolved:
            resolved.append(module)
    return tuple(resolved)
