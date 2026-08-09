from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_rules.adapters.claude import OWNER as CLAUDE_OWNER
from ai_rules.errors import ConfigurationError
from ai_rules.filesystem import WriteScope, apply_writes, plan_write
from ai_rules.ides import SUPPORTED_IDES, normalize_ides
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

BOOTSTRAP_IDES = tuple(ide for ide in SUPPORTED_IDES if ide != "cursor")

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


def _selected_bootstrap_ides(ides: tuple[str, ...] | None) -> tuple[str, ...]:
    if ides is None:
        return BOOTSTRAP_IDES
    selected = normalize_ides(ides, default_all=False)
    if "cursor" in selected:
        raise ConfigurationError(
            "Cursor has no airules-managed global bootstrap target. "
            "Use project rules with `airules init --ide cursor` instead."
        )
    return selected


def bootstrap(
    home: Path,
    *,
    codex_home: Path | None,
    dry_run: bool,
    copilot_home: Path | None = None,
    ides: tuple[str, ...] | None = None,
) -> BootstrapResult:
    home = home.resolve()
    codex_dir = (codex_home or (home / ".codex")).resolve()
    copilot_dir = (copilot_home or (home / ".copilot")).resolve()
    codex = codex_dir / "AGENTS.md"
    claude = home / ".claude" / "rules" / "airules" / "000-core.md"
    gemini = home / ".gemini" / "GEMINI.md"
    copilot = copilot_dir / "copilot-instructions.md"

    core = _render_core()
    selected_ides = _selected_bootstrap_ides(ides)
    writes: list[PlannedWrite] = []
    if "codex" in selected_ides:
        writes.append(plan_write(codex, upsert_managed_block(_read(codex), core)))
    if "claude" in selected_ides:
        existing_claude = _read(claude)
        if existing_claude and CLAUDE_OWNER not in existing_claude:
            raise ConfigurationError(
                f"Claude user rule exists but is not owned by airules: {claude}"
            )
        writes.append(plan_write(claude, f"{CLAUDE_OWNER}\n{core}"))
    if "gemini" in selected_ides:
        writes.append(plan_write(gemini, upsert_managed_block(_read(gemini), core)))
    if "copilot" in selected_ides:
        writes.append(plan_write(copilot, upsert_managed_block(_read(copilot), core)))
    scope = WriteScope(
        root=home,
        allowed_exact=frozenset({codex, claude, gemini, copilot}),
        allowed_prefixes=(codex_dir, copilot_dir, home / ".claude" / "rules" / "airules"),
    )
    applied = apply_writes(tuple(writes), dry_run=dry_run, scope=scope)
    return BootstrapResult(writes=applied)
