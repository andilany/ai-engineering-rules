from __future__ import annotations

from pathlib import Path
from typing import Any

import tomlkit
from tomlkit import TOMLDocument

from ai_rules.errors import ConfigurationError
from ai_rules.models import ProjectManifest

SECTIONS = ("language", "backend", "data", "messaging", "security", "frontend", "ml", "infrastructure")
LIST_FIELDS = ("extra_profiles", "include_modules", "exclude_modules")


def _as_bool_dict(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        return {}
    return {str(key): bool(item) for key, item in value.items()}


def _as_frontend_dict(value: Any) -> dict[str, bool | str]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, bool | str] = {}
    for key, item in value.items():
        if isinstance(item, (bool, str)):
            result[str(key)] = item
    return result


def load_manifest(path: Path) -> ProjectManifest:
    try:
        data = tomlkit.parse(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConfigurationError(f"Cannot read manifest {path}: {exc}") from exc

    version = int(data.get("version", 1))
    if version != 1:
        raise ConfigurationError(f"Unsupported manifest version: {version}")

    return ProjectManifest(
        version=version,
        profile=str(data.get("profile", "python-backend")),
        rules_version=str(data.get("rules_version", "")),
        language=_as_bool_dict(data.get("language", {})),
        backend=_as_bool_dict(data.get("backend", {})),
        data=_as_bool_dict(data.get("data", {})),
        messaging=_as_bool_dict(data.get("messaging", {})),
        security=_as_bool_dict(data.get("security", {})),
        frontend=_as_frontend_dict(data.get("frontend", {})),
        ml=_as_bool_dict(data.get("ml", {})),
        infrastructure=_as_bool_dict(data.get("infrastructure", {})),
        extra_profiles=[str(item) for item in data.get("extra_profiles", [])],
        include_modules=[str(item) for item in data.get("include_modules", [])],
        exclude_modules=[str(item) for item in data.get("exclude_modules", [])],
    )


def _document(existing: str | None) -> TOMLDocument:
    if existing is None:
        return tomlkit.document()
    try:
        return tomlkit.parse(existing)
    except ValueError as exc:
        raise ConfigurationError(f"Existing manifest is invalid TOML: {exc}") from exc


def render_manifest(manifest: ProjectManifest, existing: str | None = None) -> str:
    if manifest.version != 1:
        raise ConfigurationError(f"Unsupported manifest version: {manifest.version}")
    document = _document(existing)
    document["version"] = manifest.version
    document["profile"] = manifest.profile
    document["rules_version"] = manifest.rules_version

    for field in LIST_FIELDS:
        values = getattr(manifest, field)
        if values or field in document:
            document[field] = list(values)

    for section in SECTIONS:
        values = getattr(manifest, section)
        if not values and section not in document:
            continue
        table = document.get(section)
        if not isinstance(table, dict):
            table = tomlkit.table()
            document[section] = table
        for key, value in values.items():
            table[key] = value
    return tomlkit.dumps(document)
