# ai-engineering-rules

[Русский](README.md) | **English**

A versioned engineering rule pack for AI coding agents. The repository keeps one canonical rule set and provides the `airules` CLI to attach only the relevant guidance to a project.

Supported agents:

- OpenAI Codex — compact `AGENTS.md` entrypoint;
- Claude Code — `CLAUDE.md` plus native `.claude/rules/airules/*.md`;
- Cursor — native `.cursor/rules/airules-*.mdc`;
- GitHub Copilot — `.github/copilot-instructions.md` plus `.github/instructions/airules/*.instructions.md`;
- Gemini CLI — `GEMINI.md`.

## Why this exists

The rule pack separates universal invariants, technology-specific modules, and project profiles. It helps coding agents preserve existing architecture, avoid unexpected Git or infrastructure actions, verify changes honestly, and use the preferred stack only when it is relevant to the repository.

`airules` is not an application generator or a migration tool. It does not silently migrate Poetry to uv, a monolith to microservices, Nginx to Caddy, RabbitMQ to Kafka, or Docker Compose to Kubernetes.

## Project model

Canonical rules live under `rules/**/*.md`. A project receives only the effective configuration and adapters:

```text
.ai-rules.toml
.ai-rules/generated.md
.ai-rules/project.md
AGENTS.md
CLAUDE.md
GEMINI.md
.cursor/rules/airules-*.mdc
.claude/rules/airules/*.md
.github/copilot-instructions.md
.github/instructions/airules/*.instructions.md
```

`.ai-rules/generated.md` is the complete generated snapshot of the effective rule set. `.ai-rules/project.md` belongs to the project and is never overwritten by `airules sync`.

## Install

Stable channel after a release is merged to `main`:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@main"
```

Development channel:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@dev"
```

Upgrade the currently installed tool:

```bash
uv tool upgrade ai-engineering-rules
```

## Global Universal Core

Run once per workstation:

```bash
airules bootstrap
```

Limit bootstrap to selected agents when needed:

```bash
airules bootstrap --ide codex
airules bootstrap --ide claude --ide copilot
```

Without `--ide`, all supported targets are prepared. Cursor User Rules remain a manual Settings operation; `airules` writes the prepared text to `~/.ai-rules/cursor-user-rules.txt` instead of modifying Cursor settings automatically.

Use `--dry-run` to preview writes:

```bash
airules bootstrap --dry-run
```

## Attach to a project

```bash
cd my-project
airules detect
airules init
```

Detection reads bounded configuration signals such as `pyproject.toml`, `package.json`, and Docker/Compose markers. It does not import application code, read `.env` values, or run the application.

If the profile cannot be selected safely, choose it explicitly:

```bash
airules init --profile fastapi-backend
```

Select one or more adapters:

```bash
airules init --profile fastapi-backend --ide codex
airules init --ide cursor --ide claude
airules init --ide copilot
```

The selection is persisted in `.ai-rules.toml`. Normal `airules sync` updates only the persisted adapters. A command-level override is temporary:

```bash
airules sync --ide claude
```

Unselected adapter files are not modified. For a selected adapter, stale files are removed only when they carry an `airules` ownership marker.

Initial profiles:

- `python-backend`
- `fastapi-backend`
- `django-backend`
- `ml-gpu-service`
- `frontend-nextjs`
- `fullstack-python`

## Native adapters

Cursor, Claude Code, and GitHub Copilot receive thematic native rule files rather than one large imported file. Codex keeps a short `AGENTS.md` index that points to the generated snapshot and project-specific instructions. Gemini currently uses its `GEMINI.md` adapter.

This keeps `rules/**/*.md` as the single canonical source while allowing each agent to consume the effective rules in its native format.

## Everyday commands

```bash
airules detect
airules explain
airules doctor
airules sync
airules add ml-gpu-service
```

- `detect` reports stack signals and suggested profiles;
- `explain` reports active rules and provenance;
- `doctor` validates generated state without writing;
- `sync` refreshes only `airules`-managed content;
- `add` adds AI guidance, not application dependencies or infrastructure.

## Precedence and severity

Rule severity levels:

1. `REQUIRED` — engineering invariants;
2. `USER_DECISION` — the agent may analyze and recommend, but the user decides;
3. `PREFERRED` — greenfield/default preference;
4. `CONDITIONAL` — relevant only when the technology or situation already applies;
5. `OPTIONAL` — an available alternative.

Explicit user requests and project-specific instructions override generic preferences.

## Safety boundaries

The `airules` CLI itself must not:

- run `git add`, commit, push, merge, rebase, or create pull requests;
- create or switch branches;
- create GitHub repositories;
- install application dependencies;
- change the application's package manager;
- edit application source code;
- change project architecture;
- execute database migrations;
- deploy or mutate infrastructure.

## Releases

Release history is tracked in [CHANGELOG.md](CHANGELOG.md). Detailed release notes are stored under [`docs/releases/`](docs/releases/), and the full procedure is documented in [`docs/releasing.md`](docs/releasing.md).

Every release requires:

1. a matching version in `pyproject.toml`;
2. a `CHANGELOG.md` entry;
3. `docs/releases/vX.Y.Z.md`;
4. a `vX.Y.Z` tag from the verified `main` commit;
5. a GitHub Release for that tag.

After a tag is pushed, `.github/workflows/release.yml` validates release metadata, runs tests and the package build, then creates or updates the GitHub Release and uploads the wheel/sdist artifacts.

Current release target: [v0.3.0](docs/releases/v0.3.0.md).

## License

This project is released under the [MIT License](LICENSE). You may use, modify, distribute, and include it in commercial products as long as the copyright notice and license text are preserved.

## Documentation

- [Rule authoring](docs/rules-authoring.md)
- [Manifest](docs/manifest.md)
- [Agent adapters](docs/agent-adapters.md)
