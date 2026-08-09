# ai-engineering-rules

[Русский](README.md) | **English**

A versioned engineering rule pack for AI coding agents. The repository keeps one canonical rule catalog, while the `airules` CLI composes only the rules relevant to a project and delivers them to selected agents in their native formats.

Supported agents:

- OpenAI Codex — compact `AGENTS.md` entrypoint;
- Claude Code — `CLAUDE.md` plus `.claude/rules/airules/*.md`;
- Cursor — `.cursor/rules/airules-*.mdc`;
- GitHub Copilot — `.github/copilot-instructions.md` plus `.github/instructions/airules/*.instructions.md`;
- Gemini CLI — `GEMINI.md`.

## What airules does

`airules` does not generate an application or change project architecture. It installs engineering guidance for AI agents: rules for code changes, testing, security, the selected backend/frontend/ML/data/infrastructure stack, and project-specific constraints.

The core model is: **one canonical rule set → project-specific effective rules → native adapters for selected agents**.

```text
rules/**/*.md
        │
        └── effective rule set
              │
              ├── .ai-rules/generated.md
              ├── .cursor/rules/airules-*.mdc
              ├── .claude/rules/airules/*.md
              ├── .github/instructions/airules/*.instructions.md
              ├── AGENTS.md
              ├── CLAUDE.md
              └── GEMINI.md
```

## Install

Stable channel from `main`:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@main"
```

Development channel from `dev`:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@dev"
```

Upgrade:

```bash
uv tool upgrade ai-engineering-rules
```

Check the installed version:

```bash
airules version
```

## Quick start

Run from the project root:

```bash
cd my-project
airules init
```

In an interactive terminal, the setup wizard:

1. inspects bounded, safe project signals;
2. uses the detected stack as defaults;
3. asks which rule families are needed;
4. asks which AI agents are used;
5. shows the resulting configuration;
6. applies it only after confirmation.

You can select only the rule families the project actually needs, including:

- Backend;
- Frontend;
- ML / AI / GPU;
- Databases / data stores;
- Messaging / task queues;
- Infrastructure / Docker / Kubernetes;
- Authentication / security.

The wizard uses the minimal `custom` profile, so choosing FastAPI does not implicitly enable PostgreSQL, Redis, Docker, or Keycloak. Those rule families are added only when explicitly selected.

For CI and scripts, use the non-interactive flow:

```bash
airules init --no-interactive --profile fastapi-backend --ide cursor
```

Repeat `--ide` to select multiple adapters:

```bash
airules init --profile fastapi-backend --ide cursor --ide claude
```

The selection is persisted in `.ai-rules.toml`.

## Files in an attached project

Depending on the selected agents, `airules` manages files such as:

```text
.ai-rules.toml
.ai-rules/
├── generated.md
└── project.md

AGENTS.md
CLAUDE.md
GEMINI.md

.cursor/
└── rules/
    ├── airules-000-core.mdc
    ├── airules-100-architecture.mdc
    ├── airules-200-security-quality.mdc
    ├── airules-300-language-backend.mdc
    ├── airules-400-data-messaging.mdc
    ├── airules-500-frontend.mdc
    ├── airules-600-ml-infrastructure.mdc
    └── airules-999-project.mdc

.claude/
└── rules/
    └── airules/
        └── *.md

.github/
├── copilot-instructions.md
└── instructions/
    └── airules/
        └── *.instructions.md
```

Empty thematic groups are omitted, so a real project usually receives only a subset of the files shown above.

`.ai-rules/generated.md` is the complete generated snapshot of the effective rule set.

`.ai-rules/project.md` is **user-owned** project-specific guidance. `airules sync` never overwrites it.

## Cursor: current rule layout

For Cursor, `airules` uses **Project Rules** in Cursor's standard project directory:

```text
.cursor/rules/
```

Rules are generated as `.mdc` files, for example:

```text
.cursor/rules/airules-000-core.mdc
.cursor/rules/airules-200-security-quality.mdc
.cursor/rules/airules-300-language-backend.mdc
.cursor/rules/airules-999-project.mdc
...
```

These files are created and refreshed by:

```bash
airules init --ide cursor
airules sync
```

Cursor Project Rules are version-controlled project files. `airules` does not use the legacy `.cursorrules` file as its primary adapter.

Every generated `.mdc` begins with YAML frontmatter. The ownership marker is written **after** the closing `---` so Cursor can parse the rule correctly:

```md
---
description: airules Core engineering rules
globs:
alwaysApply: true
---

<!-- ai-engineering-rules:owned -->

# Rule content
```

`airules sync` recognizes older airules-owned `.mdc` files and regenerates them using the current valid layout.

### Cursor User Rules

Cursor User Rules are separate global Cursor preferences and are not required for `airules` project integration.

The recommended `airules` flow is **Project Rules in `.cursor/rules/`**, not manually copying project rules into Cursor Settings.

The current `airules bootstrap` command may still create `~/.ai-rules/cursor-user-rules.txt` as a legacy compatibility helper. That file is not a Cursor Project Rule and is not used by `airules init/sync` to attach rules to a repository.

## Global Universal Core

For agents that support filesystem-based global/user instructions, run once per workstation:

```bash
airules bootstrap
```

Or limit bootstrap to selected targets:

```bash
airules bootstrap --ide codex
airules bootstrap --ide claude --ide copilot
```

Primary global targets:

- Codex: `$CODEX_HOME/AGENTS.md` or `~/.codex/AGENTS.md`;
- Claude Code: `~/.claude/rules/airules/000-core.md`;
- GitHub Copilot: `$COPILOT_HOME/copilot-instructions.md` or `~/.copilot/copilot-instructions.md`;
- Gemini CLI: `~/.gemini/GEMINI.md`.

For Cursor project-specific guidance, use `airules init` / `airules sync` and `.cursor/rules/`.

Preview bootstrap without writing:

```bash
airules bootstrap --dry-run
```

## Native adapters

| Agent | Project adapter | Behavior |
|---|---|---|
| Codex | `AGENTS.md` | Compact entrypoint to generated/project guidance |
| Claude Code | `CLAUDE.md` + `.claude/rules/airules/*.md` | Native thematic rules |
| Cursor | `.cursor/rules/airules-*.mdc` | Native MDC Project Rules |
| GitHub Copilot | `.github/copilot-instructions.md` + `.github/instructions/airules/*.instructions.md` | Repository + modular instructions |
| Gemini CLI | `GEMINI.md` | Project adapter |

Cursor, Claude, and Copilot receive thematic projections of the effective rule set: core, architecture, security/quality, language/backend, data/messaging, frontend, and ML/infrastructure. Empty groups are omitted.

## Profiles

Available base profiles:

- `custom` — minimal base for the interactive wizard;
- `python-backend`;
- `fastapi-backend`;
- `django-backend`;
- `ml-gpu-service`;
- `frontend-nextjs`;
- `fullstack-python`.

Profiles select AI guidance; they do not install technologies into the application.

## Everyday commands

```bash
airules version
airules bootstrap
airules init
airules detect
airules explain
airules doctor
airules sync
airules add ml-gpu-service
airules reconfigure
airules uninstall
```

### `airules detect`

Reports detected stack signals. It does not import application code, read `.env` values, or run the project.

### `airules sync`

Reloads `.ai-rules.toml` and refreshes only `airules`-managed generated content and selected adapters.

A temporary IDE override does not modify the manifest:

```bash
airules sync --ide cursor
```

Unselected adapter files are left untouched. Stale generated files are removed only when they carry an ownership marker.

### `airules reconfigure`

Shows the current managed files and warns that the configuration will be replaced. After the required confirmation, it opens a fresh wizard. The filesystem is not changed until the final `Apply?` confirmation.

`.ai-rules/project.md` is preserved.

### `airules uninstall`

Shows the exact `DELETE` / `MODIFY` plan and requires `[y/N]` confirmation.

`.ai-rules/project.md` is preserved by default. Full removal is explicit:

```bash
airules uninstall --purge
```

Automation can use `--yes` and `--dry-run`.

## Precedence and severity

Rule levels:

1. `REQUIRED` — engineering invariants;
2. `USER_DECISION` — the agent may analyze and recommend, but the user decides;
3. `PREFERRED` — greenfield/default preference;
4. `CONDITIONAL` — applies only when the technology or situation is relevant;
5. `OPTIONAL` — an available alternative.

Explicit user requests and project-specific guidance override generic preferences.

## What airules does not do

The CLI must not:

- run `git add`, commit, push, merge, or rebase;
- create pull requests or GitHub repositories;
- create or switch Git branches;
- install application dependencies;
- change the application's package manager;
- edit application source code;
- change project architecture;
- execute database migrations;
- deploy or mutate infrastructure.

## Documentation

- [Rule authoring](docs/rules-authoring.md)
- [Manifest](docs/manifest.md)
- [Agent adapters](docs/agent-adapters.md)
- [Release process](docs/releasing.md)

## Releases

Release history and GitHub Release notes are tracked in [`CHANGELOG.md`](CHANGELOG.md).

Every release requires:

1. version `X.Y.Z` in `pyproject.toml`;
2. a populated `[X.Y.Z]` section in `CHANGELOG.md`;
3. a `vX.Y.Z` tag from the verified `main` commit;
4. a GitHub Release for that tag.

`.github/workflows/release.yml` validates metadata, runs tests and the package build, creates or updates the GitHub Release, and uploads wheel/sdist artifacts.

## License

This project is released under the [MIT License](LICENSE).
