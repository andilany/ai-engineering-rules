# Конфигурация

**Русский** | [English](../en/configuration.md)

## `.ai-rules.toml`

Manifest хранит выбранный профиль, technology flags, extra profiles, явные include/exclude rules и список project adapters. Он описывает effective AI guidance и не является командой изменить технологический стек приложения.

Основные поля:

- `version` — версия схемы manifest;
- `profile` — основной profile;
- `rules_version` — версия rule-pack;
- `ides` — ordered list: `codex`, `claude`, `cursor`, `copilot`, `gemini`;
- `extra_profiles` — дополнительные profiles;
- `include_modules` / `exclude_modules` — явные rule overrides;
- секции `language`, `backend`, `data`, `messaging`, `security`, `frontend`, `ml`, `infrastructure` — technology flags.

Пример:

```toml
version = 1
profile = "custom"
rules_version = "0.3.2"
ides = ["cursor", "claude"]

[language]
python = true

[backend]
fastapi = true

[data]
postgresql = true

[infrastructure]
docker = true
```

## Profiles

`custom` — минимальная база интерактивного wizard. Он не подтягивает PostgreSQL, Redis, Docker или Keycloak только из-за выбора backend framework.

Готовые profiles включают `python-backend`, `fastapi-backend`, `django-backend`, `frontend-nextjs`, `ml-gpu-service` и `fullstack-python`.

## Adapter selection

`airules init --ide cursor --ide claude` сохраняет selection в manifest. Обычный `sync` обновляет только выбранные adapters. `airules sync --ide gemini` является временным override и не меняет manifest.

Старый manifest без `ides` трактуется как legacy-конфигурация со всеми поддерживаемыми project adapters.

## Project files

- `.ai-rules/generated.md` — generated effective snapshot;
- `.ai-rules/project.md` — user-owned project-specific instructions;
- agent adapters — generated/native projections выбранных rules.

Прямой запрос пользователя и project-specific инструкции имеют приоритет над generic preferences.
