# Начало работы

**Русский** | [English](../en/getting-started.md)

## Установка

```bash
uv tool install "git+https://github.com/andilany/ai-engineering-rules.git@main"
```

Для development-ветки замените `@main` на `@dev`.

Проверить установку:

```bash
airules version
```

## Подключение проекта

Перейдите в корень репозитория и запустите:

```bash
airules init
```

В интерактивном терминале wizard сначала показывает обнаруженные признаки стека, затем предлагает выбрать группы правил и AI-агентов. Detected значения являются defaults, а не обязательными решениями пользователя.

Основные группы включают backend, frontend, ML/AI/GPU, data stores, messaging, infrastructure и authentication/security.

Для автоматизации можно отключить wizard:

```bash
airules init --no-interactive --profile fastapi-backend --ide cursor
```

`--ide` можно повторять:

```bash
airules init --profile fastapi-backend --ide cursor --ide claude
```

## Следующий обязательный шаг: project.md

После успешного `init` создаётся `.ai-rules/project.md` со статусом incomplete. CLI печатает prompt, который нужно передать вашему AI coding agent. Агент анализирует репозиторий, отделяет проверяемые факты от решений и задаёт вам вопросы по тому, что нельзя безопасно вывести из кода.

Подробнее: [Project-specific инструкции](project-instructions.md).

Когда файл заполнен и marker incomplete удалён:

```bash
airules sync
airules doctor
```

## Обновление правил

После обновления CLI или изменения `.ai-rules/project.md`:

```bash
airules sync
```

Проверить состояние без записи:

```bash
airules doctor
```

## Глобальные правила

```bash
airules bootstrap
```

Bootstrap создаёт Universal Core для Codex, Claude Code, GitHub Copilot и Gemini CLI. Cursor не имеет airules-managed global target и использует project rules: `airules init --ide cursor`.
