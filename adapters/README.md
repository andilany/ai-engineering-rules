# Adapter mapping

Runtime adapters генерируются CLI из canonical rules. В этой директории нет копии rule-pack; она только документирует mapping:

- Codex → `AGENTS.md`
- Claude Code → `CLAUDE.md`
- Gemini CLI → `GEMINI.md`
- Cursor → `.cursor/rules/airules-*.mdc`
- GitHub Copilot → `.github/copilot-instructions.md` + `.github/instructions/airules/*.instructions.md`

Canonical source of truth находится в `rules/` и `profiles/`.
