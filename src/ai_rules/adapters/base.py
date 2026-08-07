from __future__ import annotations

from typing import Protocol


class AdapterRenderer(Protocol):
    def __call__(self, existing: str | None) -> str: ...
