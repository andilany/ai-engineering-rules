# ai-engineering-rules

**Русский** | [English](README_EN.md)

Версионируемый набор инженерных правил для AI coding agents. `airules` определяет стек проекта, собирает релевантные правила из canonical catalog и генерирует native-инструкции только для выбранных агентов.

Поддерживаются **OpenAI Codex, Claude Code, Cursor, GitHub Copilot и Gemini CLI**.

## Установка

Стабильная версия:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@main"
```

Development-версия:

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@dev"
```

Обновление:

```bash
uv tool upgrade ai-engineering-rules
```

## Быстрый старт

В корне проекта:

```bash
airules init
```

В интерактивном терминале wizard предложит detected stack, позволит выбрать только нужные группы правил и отдельно выбрать AI-агентов.

После установки `airules` создаёт `.ai-rules/project.md` и предлагает готовый prompt для вашего AI coding agent. Агент должен проанализировать репозиторий, задать вам вопросы и заполнить project-specific инструкции только подтверждёнными фактами и решениями.

После заполнения:

```bash
airules sync
airules doctor
```

Для CI и скриптов:

```bash
airules init --no-interactive --profile fastapi-backend --ide cursor
```

## Основные команды

```bash
airules detect       # показать обнаруженный стек
airules init         # подключить правила к проекту
airules sync         # обновить generated rules и adapters
airules doctor       # проверить состояние конфигурации
airules explain      # показать effective rules и provenance
airules add NAME     # добавить profile или отдельный rule
airules reconfigure  # заново пройти настройку
airules uninstall    # безопасно удалить airules-managed данные
```

`reconfigure` и `uninstall` сначала показывают план изменений и требуют подтверждение. `.ai-rules/project.md` считается user-owned и сохраняется при обычном uninstall; удалить его можно только через `airules uninstall --purge`.

## Глобальный Universal Core

```bash
airules bootstrap
```

Global bootstrap поддерживается для Codex, Claude Code, GitHub Copilot и Gemini CLI. Cursor использует project rules в `.cursor/rules/`; для него применяется `airules init --ide cursor`.

## Документация

- [Начало работы](docs/ru/getting-started.md)
- [Project-specific инструкции и AI-onboarding](docs/ru/project-instructions.md)
- [CLI reference](docs/ru/cli.md)
- [Конфигурация и profiles](docs/ru/configuration.md)
- Интеграции: [Codex](docs/ru/agents/codex.md) · [Claude Code](docs/ru/agents/claude.md) · [Cursor](docs/ru/agents/cursor.md) · [GitHub Copilot](docs/ru/agents/copilot.md) · [Gemini CLI](docs/ru/agents/gemini.md)

Canonical rules находятся в `rules/`, profiles — в `profiles/`. `.ai-rules/generated.md` является generated snapshot, а `.ai-rules/project.md` принадлежит проекту и не перезаписывается `airules sync`.

## Что CLI не делает

`airules` не меняет исходный код приложения, архитектуру, package manager, зависимости, БД или инфраструктуру и не выполняет Git commit/push/merge. Он управляет только AI guidance и своими adapter-файлами.

## Лицензия

[MIT License](LICENSE).
