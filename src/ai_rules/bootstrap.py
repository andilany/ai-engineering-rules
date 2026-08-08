from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_rules.filesystem import WriteScope, apply_writes, plan_write
from ai_rules.ides import normalize_ides
from ai_rules.managed_blocks import upsert_managed_block
from ai_rules.models import PlannedWrite, RuleSeverity
from ai_rules.rules import load_rules

GLOBAL_CORE_MODULES = (
    "core.agent-behavior",
    "core.scope-discipline",
    "core.workflow",
    "core.verification",
    "core.external-actions",
    "security.baseline",
    "security.secrets",
    "quality.anti-cheating",
)

_ORDER = (
    RuleSeverity.REQUIRED,
    RuleSeverity.USER_DECISION,
    RuleSeverity.PREFERRED,
    RuleSeverity.CONDITIONAL,
    RuleSeverity.OPTIONAL,
)


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    writes: tuple[PlannedWrite, ...]
    cursor_note: str


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _render_core() -> str:
    rules = load_rules()
    lines = [
        "# Universal AI Engineering Core",
        "",
        "These are cross-project invariants. Project-specific instructions and explicit user "
        "requests take precedence over generic preferences.",
        "",
    ]
    for severity in _ORDER:
        selected = [
            rules[module]
            for module in GLOBAL_CORE_MODULES
            if rules[module].severity is severity
        ]
        if not selected:
            continue
        lines.extend([f"## {severity.name}", ""])
        for rule in selected:
            lines.append(rule.body.rstrip())
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def bootstrap(
    home: Path,
    *,
    codex_home: Path | None,
    dry_run: bool,
    ides: tuple[str, ...] | None = None,
) -> BootstrapResult:
    home = home.resolve()
    codex_dir = (codex_home or (home / ".codex")).resolve()
    codex = codex_dir / "AGENTS.md"
    claude = home / ".claude" / "CLAUDE.md"
    gemini = home / ".gemini" / "GEMINI.md"
    cursor = home / ".ai-rules" / "cursor-user-rules.txt"

    core = _render_core()
    cursor_text = (
        "Paste the content below into Cursor Settings > Rules > User Rules.\n"
        "Cursor User Rules are managed by Cursor settings; airules does not modify them "
        "automatically.\n\n"
        + core
    )
    selected_ides = normalize_ides(ides, default_all=True)
    writes: list[PlannedWrite] = []
    if "codex" in selected_ides:
        writes.append(plan_write(codex, upsert_managed_block(_read(codex), core)))
    if "claude" in selected_ides:
        writes.append(plan_write(claude, upsert_managed_block(_read(claude), core)))
    if "gemini" in selected_ides:
        writes.append(plan_write(gemini, upsert_managed_block(_read(gemini), core)))
    if "cursor" in selected_ides:
        writes.append(plan_write(cursor, cursor_text))
    scope = WriteScope(
        root=home,
        allowed_exact=frozenset({codex, claude, gemini, cursor}),
    )
    applied = apply_writes(tuple(writes), dry_run=dry_run, scope=scope)
    cursor_note = (
        "Cursor: paste ~/.ai-rules/cursor-user-rules.txt into Settings > Rules > User Rules."
        if "cursor" in selected_ides
        else ""
    )
    return BootstrapResult(writes=applied, cursor_note=cursor_note)
