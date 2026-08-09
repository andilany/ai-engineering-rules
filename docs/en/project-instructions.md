# Project-specific instructions

[Русский](../ru/project-instructions.md) | **English**

`.ai-rules/project.md` is the user-owned layer for repository-specific guidance. It holds information that generic technology rules cannot safely express: product purpose, architecture boundaries, business constraints, required verification commands, and actions that require explicit approval.

`airules sync` and `airules reconfigure` never overwrite a completed `project.md`.

## Onboarding status

A new file starts with:

```html
<!-- airules:project-status=incomplete -->
```

While the marker remains, `airules doctor` reports `project_rules_incomplete`. The user or their AI agent removes the marker only after onboarding is complete.

## Complete it with your own AI

After `airules init`, the CLI prints a ready-to-use prompt. Give it to Cursor, Claude Code, Codex, Copilot, or Gemini while the repository is open.

The AI should:

1. inspect repository structure, configuration, tests, and documentation;
2. record only facts that can be verified in the repository;
3. ask the user focused questions about project purpose, architectural decisions, business constraints, and operational constraints;
4. never invent requirements or decisions;
5. show the proposed content before writing it;
6. modify only `.ai-rules/project.md` after user confirmation;
7. remove the incomplete marker only after the content is approved.

## Recommended sections

- Project purpose
- Architecture and boundaries
- Development workflow
- Testing and verification
- Business constraints
- Operational constraints
- Changes requiring explicit approval

After editing, run:

```bash
airules sync
airules doctor
```

This refreshes native projections for adapters that embed project-specific instructions.

## Removal

Normal `airules uninstall` preserves `.ai-rules/project.md`. Delete it only explicitly:

```bash
airules uninstall --purge
```
