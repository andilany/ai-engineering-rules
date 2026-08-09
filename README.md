# ai-engineering-rules

**Русский** | [English](README_EN.md)

Версионируемый набор инженерных правил для AI coding agents. Репозиторий хранит единый canonical rule catalog, а CLI `airules` собирает из него только релевантные правила и подключает их к выбранным агентам в native-формате.

Поддерживаемые агенты:

- OpenAI Codex — компактный `AGENTS.md` entrypoint;
- Claude Code — `CLAUDE.md` + `.claude/rules/airules/*.md`;
- Cursor — `.cursor/rules/airules-*.mdc`;
- GitHub Copilot — `.github/copilot-instructions.md` + `.github/instructions/airules/*.instructions.md`;
- Gemini CLI — `GEMINI.md`.

## Что делает airules

`airules` не генерирует приложение и не меняет архитектуру проекта. Он добавляет инженерные инструкции для AI-агентов: правила работы с кодом, тестированием, безопасностью, выбранным backend/frontend/ML/data/infrastructure стеком и project-specific ограничениями.

Основной принцип: **один canonical набор правил → effective rules конкретного проекта → native adapters выбранных агентов**.

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

## Установка

Стабильная версия из `main`:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@main"
```

Development-версия из `dev`:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@dev"
```

Обновление:

```bash
uv tool upgrade ai-engineering-rules
```

Проверка версии:

```bash
airules version
```

## Быстрый старт

Перейдите в корень проекта и запустите:

```bash
cd my-project
airules init
```

В интерактивном терминале откроется wizard. Он:

1. анализирует безопасные признаки проекта;
2. предлагает detected stack как defaults;
3. спрашивает, какие группы правил нужны;
4. отдельно спрашивает, какие AI-агенты используются;
5. показывает итоговую конфигурацию;
6. применяет её только после подтверждения.

Можно выбрать только нужные группы, например:

- Backend;
- Frontend;
- ML / AI / GPU;
- Databases / data stores;
- Messaging / task queues;
- Infrastructure / Docker / Kubernetes;
- Authentication / security.

Wizard использует минимальный профиль `custom`, поэтому выбор FastAPI сам по себе не включает PostgreSQL, Redis, Docker или Keycloak. Дополнительные группы подключаются только если пользователь выбрал их явно.

Для CI и скриптов остаётся non-interactive режим:

```bash
airules init --no-interactive --profile fastapi-backend --ide cursor
```

`--ide` можно указывать несколько раз:

```bash
airules init --profile fastapi-backend --ide cursor --ide claude
```

Выбор сохраняется в `.ai-rules.toml`.

## Файлы в подключённом проекте

В зависимости от выбранных агентов `airules` управляет следующими файлами:

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

Пустые тематические группы не создаются, поэтому конкретный проект обычно получает только часть файлов из примера выше.

`.ai-rules/generated.md` — полный generated snapshot effective rules.

`.ai-rules/project.md` — **user-owned файл** для project-specific инструкций. `airules sync` его не перезаписывает.

## Cursor: актуальная схема

Для Cursor `airules` использует **Project Rules**. Они находятся в стандартном каталоге проекта:

```text
.cursor/rules/
```

и хранятся как `.mdc` файлы:

```text
.cursor/rules/airules-000-core.mdc
.cursor/rules/airules-200-security-quality.mdc
.cursor/rules/airules-300-language-backend.mdc
.cursor/rules/airules-999-project.mdc
...
```

Именно эти файлы создают и обновляют:

```bash
airules init --ide cursor
airules sync
```

Cursor Project Rules являются version-controlled частью проекта. `airules` не использует legacy `.cursorrules` как основной adapter.

Каждый generated `.mdc` начинается с YAML frontmatter. Ownership marker размещается **после** закрывающего `---`, чтобы Cursor корректно распознавал правило:

```md
---
description: airules Core engineering rules
globs:
alwaysApply: true
---

<!-- ai-engineering-rules:owned -->

# Rule content
```

`airules sync` распознаёт старые airules-owned `.mdc` и перегенерирует их в актуальном формате.

### Cursor User Rules

Cursor User Rules — отдельные глобальные настройки самого Cursor и не требуются для project integration `airules`.

Рекомендуемый flow для `airules` — **Project Rules в `.cursor/rules/`**, а не ручное копирование project rules в Cursor Settings.

Текущая команда `airules bootstrap` может создавать `~/.ai-rules/cursor-user-rules.txt` как legacy compatibility helper. Этот файл не является Cursor Project Rule и не используется `airules init/sync` для подключения правил к репозиторию.

## Глобальный Universal Core

Для агентов, поддерживающих filesystem-based user/global instructions, можно один раз выполнить:

```bash
airules bootstrap
```

Или ограничить targets:

```bash
airules bootstrap --ide codex
airules bootstrap --ide claude --ide copilot
```

Основные global targets:

- Codex: `$CODEX_HOME/AGENTS.md` или `~/.codex/AGENTS.md`;
- Claude Code: `~/.claude/rules/airules/000-core.md`;
- GitHub Copilot: `$COPILOT_HOME/copilot-instructions.md` или `~/.copilot/copilot-instructions.md`;
- Gemini CLI: `~/.gemini/GEMINI.md`.

Для Cursor project-specific rules используйте `airules init` / `airules sync` и `.cursor/rules/`.

Проверка bootstrap без записи:

```bash
airules bootstrap --dry-run
```

## Native adapters

| Agent | Project adapter | Поведение |
|---|---|---|
| Codex | `AGENTS.md` | Короткий entrypoint к generated/project instructions |
| Claude Code | `CLAUDE.md` + `.claude/rules/airules/*.md` | Native тематические правила |
| Cursor | `.cursor/rules/airules-*.mdc` | Native MDC Project Rules |
| GitHub Copilot | `.github/copilot-instructions.md` + `.github/instructions/airules/*.instructions.md` | Repository + modular instructions |
| Gemini CLI | `GEMINI.md` | Project adapter |

Cursor, Claude и Copilot получают тематические проекции effective rule set: core, architecture, security/quality, language/backend, data/messaging, frontend, ML/infrastructure. Пустые группы пропускаются.

## Профили

Доступные базовые профили:

- `custom` — минимальная база для интерактивного wizard;
- `python-backend`;
- `fastapi-backend`;
- `django-backend`;
- `ml-gpu-service`;
- `frontend-nextjs`;
- `fullstack-python`.

Профиль не устанавливает технологии в проект. Он только выбирает AI guidance.

## Повседневные команды

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

Показывает обнаруженные признаки стека. Не импортирует код приложения, не читает значения `.env` и не запускает проект.

### `airules sync`

Перечитывает `.ai-rules.toml` и обновляет только `airules`-managed generated content и выбранные adapters.

Временный IDE override не меняет manifest:

```bash
airules sync --ide cursor
```

Невыбранные adapter-файлы не изменяются. Stale generated files удаляются только при наличии ownership marker.

### `airules reconfigure`

Показывает текущие managed-файлы и предупреждает о замене конфигурации. После обязательного подтверждения запускается новый wizard. До финального `Apply?` файловая система не изменяется.

`.ai-rules/project.md` сохраняется.

### `airules uninstall`

Перед удалением показывает точный список `DELETE` / `MODIFY` и требует подтверждение `[y/N]`.

По умолчанию `.ai-rules/project.md` сохраняется. Полное удаление выполняется только явно:

```bash
airules uninstall --purge
```

Для automation доступны `--yes` и `--dry-run`.

## Модель приоритетов

Уровни правил:

1. `REQUIRED` — инженерные invariants;
2. `USER_DECISION` — модель анализирует и рекомендует, решение принимает пользователь;
3. `PREFERRED` — greenfield/default preference;
4. `CONDITIONAL` — применяется только когда технология или ситуация релевантна;
5. `OPTIONAL` — возможный вариант.

Прямой запрос пользователя и project-specific инструкции имеют приоритет над generic preferences.

## Что airules не делает

CLI не должен:

- выполнять `git add`, commit, push, merge или rebase;
- создавать PR или GitHub-репозитории;
- создавать или переключать Git-ветки;
- устанавливать зависимости приложения;
- менять package manager приложения;
- изменять исходный код приложения;
- менять архитектуру проекта;
- выполнять миграции БД;
- деплоить или изменять инфраструктуру.

## Документация

- [Rule authoring](docs/rules-authoring.md)
- [Manifest](docs/manifest.md)
- [Agent adapters](docs/agent-adapters.md)
- [Release process](docs/releasing.md)

## Релизы

История изменений и текст GitHub Release ведутся в [`CHANGELOG.md`](CHANGELOG.md).

Для каждого релиза обязательны:

1. версия `X.Y.Z` в `pyproject.toml`;
2. заполненная секция `[X.Y.Z]` в `CHANGELOG.md`;
3. тег `vX.Y.Z` из проверенного `main`;
4. GitHub Release для этого тега.

`.github/workflows/release.yml` проверяет metadata, запускает тесты и сборку, создаёт или обновляет GitHub Release и прикладывает wheel/sdist.

## Лицензия

Проект распространяется по [MIT License](LICENSE).
