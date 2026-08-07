from __future__ import annotations

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path


def resource_path(kind: str) -> Traversable:
    if kind not in {"rules", "profiles"}:
        raise ValueError(f"Unsupported resource kind: {kind}")

    packaged = files("ai_rules").joinpath("resources", kind)
    if packaged.is_dir():
        return packaged

    source_root = Path(__file__).resolve().parents[2]
    fallback = source_root / kind
    if fallback.is_dir():
        return fallback

    return packaged
