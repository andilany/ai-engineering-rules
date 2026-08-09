# CLI reference

**Русский** | [English](../en/cli.md)

## Project commands

| Команда | Назначение |
| --- | --- |
| `airules version` | показать версию CLI |
| `airules detect` | показать обнаруженные stack signals и suggested profiles |
| `airules init` | подключить airules; в TTY открывает wizard |
| `airules sync` | обновить generated snapshot и выбранные adapters |
| `airules doctor` | проверить manifest, project onboarding и adapters без записи |
| `airules explain` | показать effective modules/rules и provenance |
| `airules add NAME` | добавить profile или canonical rule |
| `airules reconfigure` | заново выбрать конфигурацию с preview и подтверждениями |
| `airules uninstall` | удалить airules-managed project state после preview |

### init

```bash
airules init
airules init --profile fastapi-backend --ide cursor
airules init --no-interactive --profile fastapi-backend --ide cursor
airules init --dry-run
```

`--ide` repeatable. Явные `--profile`/`--ide` по умолчанию переводят `init` в non-interactive режим; `--interactive` можно использовать принудительно.

### sync

```bash
airules sync
airules sync --ide claude
airules sync --dry-run
```

`sync --ide` является временным adapter override и не меняет persisted `ides` в `.ai-rules.toml`.

### reconfigure

Команда показывает managed data, которые будут заменены, требует подтверждение, запускает новый wizard и перед применением запрашивает второе подтверждение. `.ai-rules/project.md` сохраняется.

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

Обычный uninstall сохраняет user-owned `project.md`; `--purge` удаляет его явно.

## Global bootstrap

```bash
airules bootstrap
airules bootstrap --ide codex --ide claude
airules bootstrap --dry-run
```

Поддерживаются Codex, Claude Code, GitHub Copilot и Gemini CLI. Явный `airules bootstrap --ide cursor` завершается ошибкой с подсказкой использовать `airules init --ide cursor`, потому что Cursor integration является project-level.
