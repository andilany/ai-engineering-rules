# Getting started

[Русский](../ru/getting-started.md) | **English**

## Install

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@main"
```

Use `@dev` instead of `@main` for the development branch.

Verify the installation:

```bash
airules version
```

## Attach a project

From the repository root, run:

```bash
airules init
```

In an interactive terminal, the wizard first shows detected stack signals, then asks which rule families and AI agents to enable. Detected values are defaults, not mandatory user decisions.

Rule families include backend, frontend, ML/AI/GPU, data stores, messaging, infrastructure, and authentication/security.

For automation, disable the wizard:

```bash
airules init --no-interactive --profile fastapi-backend --ide cursor
```

`--ide` is repeatable:

```bash
airules init --profile fastapi-backend --ide cursor --ide claude
```

## Required next step: project.md

After a successful `init`, `.ai-rules/project.md` is created with an incomplete status marker. The CLI prints a prompt for your AI coding agent. The agent inspects the repository, separates verifiable facts from decisions, and asks you about anything that cannot be safely inferred from code.

See [Project-specific instructions](project-instructions.md).

After the file is complete and the incomplete marker is removed:

```bash
airules sync
airules doctor
```

## Refresh rules

After upgrading the CLI or changing `.ai-rules/project.md`:

```bash
airules sync
```

Validate state without writing:

```bash
airules doctor
```

## Global rules

```bash
airules bootstrap
```

Bootstrap installs the Universal Core for Codex, Claude Code, GitHub Copilot, and Gemini CLI. Cursor has no airules-managed global target and uses project rules via `airules init --ide cursor`.
