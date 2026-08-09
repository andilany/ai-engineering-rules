# CLI reference

[Русский](../ru/cli.md) | **English**

## Project commands

| Command | Purpose |
| --- | --- |
| `airules version` | print the CLI version |
| `airules detect` | show detected stack signals and suggested profiles |
| `airules init` | attach airules; opens the wizard in a TTY |
| `airules sync` | refresh the generated snapshot and selected adapters |
| `airules doctor` | validate manifest, project onboarding, and adapters without writing |
| `airules explain` | show effective modules/rules and provenance |
| `airules add NAME` | add a profile or canonical rule |
| `airules reconfigure` | rebuild configuration with previews and confirmations |
| `airules uninstall` | remove airules-managed project state after a preview |

### init

```bash
airules init
airules init --profile fastapi-backend --ide cursor
airules init --no-interactive --profile fastapi-backend --ide cursor
airules init --dry-run
```

`--ide` is repeatable. Explicit `--profile`/`--ide` options make `init` non-interactive by default; use `--interactive` to force the wizard.

### sync

```bash
airules sync
airules sync --ide claude
airules sync --dry-run
```

`sync --ide` is a temporary adapter override and does not modify persisted `ides` in `.ai-rules.toml`.

### reconfigure

The command previews managed data that will be replaced, requires confirmation, runs a fresh wizard, and asks for a second confirmation before applying. `.ai-rules/project.md` is preserved.

```bash
airules reconfigure
airules reconfigure --dry-run
airules reconfigure --yes
```

### uninstall

```bash
airules uninstall
airules uninstall --dry-run
airules uninstall --yes
airules uninstall --purge
```

Normal uninstall preserves the user-owned `project.md`; `--purge` explicitly deletes it.

## Global bootstrap

```bash
airules bootstrap
airules bootstrap --ide codex --ide claude
airules bootstrap --dry-run
```

Codex, Claude Code, GitHub Copilot, and Gemini CLI are supported. Explicit `airules bootstrap --ide cursor` fails with guidance to use `airules init --ide cursor`, because Cursor integration is project-level.
