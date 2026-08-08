# ai-engineering-rules

**Русский** | [English](README_EN.md)

Версионируемый rule-pack инженерных правил для AI coding agents. Репозиторий хранит единый canonical набор правил и CLI `airules`, который подключает релевантные инструкции к проектам.

Поддерживаемые агенты:

- OpenAI Codex — компактный `AGENTS.md`-entrypoint;
- Claude Code — `CLAUDE.md` + native `.claude/rules/airules/*.md`;
- Cursor — native `.cursor/rules/airules-*.mdc`;
- GitHub Copilot — `.github/copilot-instructions.md` + `.github/instructions/airules/*.instructions.md`;
- Gemini CLI — `GEMINI.md`.

## Зачем это нужно

Правила разделены на универсальные invariants, технологические модули и профили. Они помогают модели соблюдать существующую архитектуру, не выполнять неожиданные Git/infra-действия, честно верифицировать изменения и использовать согласованный стек там, где он действительно применим.

Это **не генератор приложения** и не инструмент миграций. `airules` не переводит Poetry на uv, монолит на микросервисы, Nginx на Caddy, RabbitMQ на Kafka и Docker Compose на Kubernetes.

## Почему не submodule и не копирование

Canonical rules живут в этом репозитории. В конкретном проекте остаются только:

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

`.ai-rules/project.md` полностью принадлежит проекту и никогда не перезаписывается `airules sync`.

## Установка

Стабильная версия после релиза в `main`:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@main"
```

Development-версия из `dev`:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@dev"
```

Обновление установленного CLI:

```bash
uv tool upgrade ai-engineering-rules
```

## Глобальный Universal Core

Один раз на рабочей машине:

```bash
airules bootstrap
```

Можно ограничить bootstrap конкретными агентами/IDE:

```bash
airules bootstrap --ide codex
airules bootstrap --ide claude --ide copilot
```

Без `--ide` сохраняется прежнее поведение — подготавливаются все поддерживаемые targets. Команда добавляет managed block только в:

- `$CODEX_HOME/AGENTS.md` или `~/.codex/AGENTS.md`;
- `~/.claude/rules/airules/000-core.md`;
- `$COPILOT_HOME/copilot-instructions.md` или `~/.copilot/copilot-instructions.md`;
- `~/.gemini/GEMINI.md`;
- `~/.ai-rules/cursor-user-rules.txt`.

Cursor User Rules управляются через настройки Cursor. `airules` не меняет их автоматически — готовый текст нужно вставить из `~/.ai-rules/cursor-user-rules.txt` в **Settings → Rules → User Rules**.

Проверить изменения без записи:

```bash
airules bootstrap --dry-run
```

## Подключение к существующему проекту

```bash
cd my-project
airules detect
airules init
```

`detect` только читает безопасные конфигурационные признаки (`pyproject.toml`, `package.json`, Docker/Compose markers и т. п.). Он не импортирует код проекта, не читает значения `.env` и не запускает приложение.

Если профиль определён неоднозначно, `init` откажется угадывать и попросит указать его явно:

```bash
airules init --profile fastapi-backend
```

Можно сразу выбрать, для каких агентов создавать project adapters:

```bash
airules init --profile fastapi-backend --ide codex
airules init --ide codex --ide cursor
airules init --ide copilot
```

Выбор сохраняется в `.ai-rules.toml`. Последующий `airules sync` обновляет только выбранные adapters. Временный override не меняет manifest:

```bash
airules sync --ide claude
```

Невыбранные существующие adapter-файлы не изменяются. Для выбранного adapter `sync` может удалить только устаревшие файлы с доказанным ownership marker `airules`. Старые manifests без поля `ides` продолжают означать «все поддерживаемые агенты».

Начальные профили:

- `python-backend`
- `fastapi-backend`
- `django-backend`
- `ml-gpu-service`
- `frontend-nextjs`
- `fullstack-python`

### Native adapters

`rules/**/*.md` остаются canonical source. `.ai-rules/generated.md` — полный compiled snapshot effective rules, а native adapters проецируют тот же набор в формат конкретного агента. Cursor, Claude и Copilot получают тематические файлы (`core`, `security/quality`, `backend`, `data/messaging`, `frontend`, `ml/infrastructure`) без копирования всех 82 canonical files по одному.

`.ai-rules/project.md` остаётся user-owned source project-specific инструкций. Cursor и Copilot обновляют свои generated projections при `airules sync`; Claude подключает project file через корневой `CLAUDE.md`.

## Повседневные команды

```bash
airules detect
airules explain
airules doctor
airules sync
airules add ml-gpu-service
```

`airules explain` показывает активные правила и их provenance. `doctor` сравнивает manifest, generated snapshot и adapters без записи. `sync` перечитывает `.ai-rules.toml` и обновляет только airules-managed контент.

`airules add <profile-or-rule>` **добавляет AI guidance**, а не технологию в приложение. Например, добавление Kubernetes-rule не устанавливает Kubernetes, Helm, manifests или инфраструктуру.

## Модель приоритетов

Используются уровни:

1. `REQUIRED` — инженерные invariants;
2. `USER_DECISION` — модель может анализировать и рекомендовать, но решение принимает пользователь;
3. `PREFERRED` — greenfield/default preference;
4. `CONDITIONAL` — применяется только когда технология/ситуация уже актуальна;
5. `OPTIONAL` — возможный вариант.

Более конкретные project-specific инструкции и прямой запрос пользователя имеют приоритет над generic preferences.

## Python defaults

Для greenfield Python-проектов предпочтителен latest stable Python, совместимый со stable-зависимостями, и `uv`. В существующем проекте package manager сохраняется. Модель может предложить миграцию на `uv` с аргументацией, но не имеет права выполнить её без согласования.

Основные backend defaults при соответствующем выборе пользователя: FastAPI/Pydantic или Django + `django-modern-rest` + `msgspec`, PostgreSQL, SQLAlchemy/Alembic или Django ORM/migrations, Redis, RabbitMQ/aio-pika/aiormq, Keycloak/OAuth2/OIDC/JWT/RBAC, pytest, Ruff, typing и Bandit.

`django-modern-rest` является явным исключением из общего stable-only правила, пока его актуальный релиз имеет Alpha/pre-1.0 статус.

## Что `airules` никогда не делает

Сам CLI не должен:

- выполнять `git add`, commit, push, merge, rebase или создавать PR;
- создавать или переключать ветки;
- создавать GitHub-репозитории;
- устанавливать зависимости приложения;
- менять package manager приложения;
- изменять исходный код приложения;
- менять архитектуру проекта;
- выполнять миграции БД;
- деплоить или изменять инфраструктуру.

Git-коммиты остаются ответственностью пользователя.

## Авторство правил

Формат canonical rules и severity описан в [`docs/rules-authoring.md`](docs/rules-authoring.md), manifest — в [`docs/manifest.md`](docs/manifest.md), особенности агентов — в [`docs/agent-adapters.md`](docs/agent-adapters.md).

## Релизы

История изменений и текст GitHub Release ведутся в [`CHANGELOG.md`](CHANGELOG.md). Полная процедура описана в [`docs/releasing.md`](docs/releasing.md).

Для **каждого** релиза обязательны:

1. версия в `pyproject.toml`;
2. заполненная секция `[X.Y.Z]` в `CHANGELOG.md`;
3. тег `vX.Y.Z` из проверенного `main`;
4. GitHub Release для этого тега.

После push тега workflow `.github/workflows/release.yml` повторно проверяет metadata, извлекает секцию версии из `CHANGELOG.md`, запускает тесты и сборку, затем создаёт GitHub Release или обновляет уже существующий Release и прикладывает wheel/sdist.

## Лицензия

Проект распространяется по [MIT License](LICENSE). Разрешено использовать, изменять, распространять и включать проект в коммерческие продукты при сохранении copyright notice и текста лицензии.
