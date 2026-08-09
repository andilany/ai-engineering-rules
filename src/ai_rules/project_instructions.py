from __future__ import annotations

PROJECT_INCOMPLETE_MARKER = "<!-- airules:project-status=incomplete -->"

PROJECT_INSTRUCTIONS_TEMPLATE = f"""{PROJECT_INCOMPLETE_MARKER}

# Project-Specific AI Instructions

This file is user-owned. Complete it together with your AI coding agent and keep only
repository-specific facts, constraints, and decisions that you have verified or confirmed.

## Project purpose

<!-- What does this repository build or operate? -->

## Architecture and boundaries

<!-- Important components, ownership boundaries, allowed dependencies,
and architectural decisions. -->

## Development workflow

<!-- Local run, build, formatting, linting, migration, and other project-specific commands. -->

## Testing and verification

<!-- Required test suites, checks, environments, and acceptance criteria. -->

## Business constraints

<!-- Domain rules and product constraints that cannot be inferred safely from code alone. -->

## Operational constraints

<!-- Deployment, infrastructure, observability, data-handling, and runtime constraints. -->

## Changes requiring explicit approval

<!-- Actions the AI must not perform or decisions it must not make without user approval. -->
"""

PROJECT_ONBOARDING_PROMPT = (
    "Analyze this repository before editing application code and help me complete\n"
    "`.ai-rules/project.md` together with you.\n\n"
    "1. Inspect the repository structure, configuration, tests, and documentation.\n"
    "2. Separate facts you can verify from decisions or constraints that require my input.\n"
    "3. Ask me focused questions about anything that cannot be inferred safely, especially:\n"
    "   - project purpose;\n"
    "   - architecture and module boundaries;\n"
    "   - development and verification workflow;\n"
    "   - business constraints;\n"
    "   - operational constraints;\n"
    "   - changes that require explicit approval.\n"
    "4. Do not invent business requirements or architectural decisions.\n"
    "5. Show me the proposed project-specific instructions before writing them.\n"
    "6. Update only `.ai-rules/project.md` after I confirm the content.\n"
    "7. Remove `<!-- airules:project-status=incomplete -->` when onboarding is complete.\n"
    "8. After updating the file, ask me to run `airules sync` and `airules doctor`.\n"
)


def is_project_incomplete(content: str | None) -> bool:
    return content is None or PROJECT_INCOMPLETE_MARKER in content
