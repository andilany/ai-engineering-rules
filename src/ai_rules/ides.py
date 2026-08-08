from __future__ import annotations

from collections.abc import Iterable

from ai_rules.errors import ConfigurationError

SUPPORTED_IDES: tuple[str, ...] = ("codex", "claude", "cursor", "gemini")


def normalize_ides(values: Iterable[str] | None, *, default_all: bool) -> tuple[str, ...]:
    if values is None:
        return SUPPORTED_IDES if default_all else ()

    normalized: list[str] = []
    for raw in values:
        value = str(raw).strip().lower()
        if value not in SUPPORTED_IDES:
            supported = ", ".join(SUPPORTED_IDES)
            raise ConfigurationError(f"Unknown IDE: {raw}. Supported values: {supported}")
        if value not in normalized:
            normalized.append(value)

    if not normalized:
        raise ConfigurationError("`ides` selection cannot be empty")
    return tuple(normalized)
