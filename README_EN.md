# ai-engineering-rules

[Русский](README.md) | **English**

A versioned engineering rule pack for AI coding agents. `airules` detects the project stack, composes the relevant guidance from one canonical catalog, and generates native instructions only for the selected agents.

Supported agents: **OpenAI Codex, Claude Code, Cursor, GitHub Copilot, and Gemini CLI**.

## Install

Stable version:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@main"
```

Development version:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@dev"
```

Upgrade:

```bash
uv tool upgrade ai-engineering-rules
```

## Quick start

From the project root:

```bash
airules init
```

In an interactive terminal, the wizard proposes detected stack defaults, lets you select only the rule families you need, and then selects AI-agent adapters separately.

After setup, `airules` creates `.ai-rules/project.md` and prints a ready-to-use prompt for your AI coding agent. The agent should inspect the repository, ask you questions, and record only confirmed project-specific facts and decisions.

After completing the file:

```bash
airules sync
airules doctor
```

For CI and scripts:

```bash
airules init --no-interactive --profile fastapi-backend --ide cursor
```

## Main commands

```bash
airules detect       # show detected stack signals
airules init         # attach rules to a project
airules sync         # refresh generated rules and adapters
airules doctor       # validate project state
airules explain      # show effective rules and provenance
airules add NAME     # add a profile or individual rule
airules reconfigure  # rebuild project configuration
airules uninstall    # safely remove airules-managed data
```

`reconfigure` and `uninstall` preview destructive changes and require confirmation. `.ai-rules/project.md` is user-owned and is preserved by normal uninstall; remove it only with `airules uninstall --purge`.

## Global Universal Core

```bash
airules bootstrap
```

Global bootstrap is supported for Codex, Claude Code, GitHub Copilot, and Gemini CLI. Cursor uses project rules under `.cursor/rules/`; configure it with `airules init --ide cursor`.

## Documentation

- [Getting started](docs/en/getting-started.md)
- [Project-specific instructions and AI onboarding](docs/en/project-instructions.md)
- [CLI reference](docs/en/cli.md)
- [Configuration and profiles](docs/en/configuration.md)
- Integrations: [Codex](docs/en/agents/codex.md) · [Claude Code](docs/en/agents/claude.md) · [Cursor](docs/en/agents/cursor.md) · [GitHub Copilot](docs/en/agents/copilot.md) · [Gemini CLI](docs/en/agents/gemini.md)

Canonical rules live under `rules/`, profiles under `profiles/`. `.ai-rules/generated.md` is the generated snapshot, while `.ai-rules/project.md` belongs to the project and is never overwritten by `airules sync`.

## What the CLI does not do

`airules` does not modify application source code, architecture, package managers, dependencies, databases, or infrastructure, and it does not run Git commit/push/merge operations. It manages only AI guidance and its own adapter files.

## License

[MIT License](LICENSE).
