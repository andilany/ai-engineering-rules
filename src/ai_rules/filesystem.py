from __future__ import annotations

import os
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from ai_rules.errors import SafetyError
from ai_rules.models import PlannedDelete, PlannedWrite


@dataclass(frozen=True, slots=True)
class WriteScope:
    root: Path
    allowed_exact: frozenset[Path] = frozenset()
    allowed_prefixes: tuple[Path, ...] = ()


def plan_write(path: Path, content: str) -> PlannedWrite:
    try:
        existing = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing = None
    return PlannedWrite(path=path, content=content, changed=existing != content)


def _is_allowed(path: Path, scope: WriteScope) -> bool:
    resolved = path.resolve(strict=False)
    root = scope.root.resolve(strict=False)
    if resolved in {item.resolve(strict=False) for item in scope.allowed_exact}:
        return True
    for prefix in scope.allowed_prefixes:
        resolved_prefix = prefix.resolve(strict=False)
        if resolved == resolved_prefix or resolved_prefix in resolved.parents:
            return root == resolved or root in resolved.parents
    return False


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".airules-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def apply_writes(
    writes: Sequence[PlannedWrite],
    *,
    dry_run: bool,
    scope: WriteScope,
) -> tuple[PlannedWrite, ...]:
    for write in writes:
        if not _is_allowed(write.path, scope):
            raise SafetyError(f"Refusing to write outside allowed airules paths: {write.path}")
        if write.changed and not dry_run:
            _atomic_write(write.path, write.content)
    return tuple(writes)


def plan_delete(path: Path) -> PlannedDelete:
    return PlannedDelete(path=path, changed=path.exists())


def apply_deletes(
    deletes: Sequence[PlannedDelete],
    *,
    dry_run: bool,
    scope: WriteScope,
) -> tuple[PlannedDelete, ...]:
    for delete in deletes:
        if not _is_allowed(delete.path, scope):
            raise SafetyError(f"Refusing to delete outside allowed airules paths: {delete.path}")
        if delete.changed and not dry_run:
            try:
                delete.path.unlink()
            except FileNotFoundError:
                pass
    return tuple(deletes)
