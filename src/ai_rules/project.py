from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProjectPaths:
    root: Path

    @property
    def manifest(self) -> Path:
        return self.root / ".ai-rules.toml"

    @property
    def rules_dir(self) -> Path:
        return self.root / ".ai-rules"

    @property
    def generated(self) -> Path:
        return self.rules_dir / "generated.md"

    @property
    def project_rules(self) -> Path:
        return self.rules_dir / "project.md"

    @property
    def codex(self) -> Path:
        return self.root / "AGENTS.md"

    @property
    def claude(self) -> Path:
        return self.root / "CLAUDE.md"

    @property
    def claude_native_dir(self) -> Path:
        return self.root / ".claude" / "rules" / "airules"

    @property
    def gemini(self) -> Path:
        return self.root / "GEMINI.md"

    @property
    def legacy_cursor_rule(self) -> Path:
        return self.root / ".cursor" / "rules" / "engineering.mdc"

    @property
    def cursor_rules_dir(self) -> Path:
        return self.root / ".cursor" / "rules"

    @property
    def copilot(self) -> Path:
        return self.root / ".github" / "copilot-instructions.md"

    @property
    def copilot_native_dir(self) -> Path:
        return self.root / ".github" / "instructions" / "airules"


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current
