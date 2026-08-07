# `.ai-rules.toml`

Manifest хранит активный профиль и явные technology flags конкретного проекта. Он описывает существующий/выбранный стек и **не является инструкцией мигрировать проект**.

```toml
version = 1
profile = "fastapi-backend"
rules_version = "0.1.0"
extra_profiles = ["ml-gpu-service"]
include_modules = []
exclude_modules = []

[language]
python = true

[backend]
fastapi = true
pydantic = true

[data]
postgresql = true
sqlalchemy = true
alembic = true
redis = true

[messaging]
rabbitmq = true
aio_pika = true

[security]
keycloak = true

[frontend]
nextjs = false

[ml]
gpu = true

[infrastructure]
docker = true
compose = true
```

## Поля

- `version` — версия схемы manifest, сейчас только `1`.
- `profile` — основной профиль.
- `rules_version` — версия rule-pack, обновляется `sync`.
- `extra_profiles` — дополнительные профили.
- `include_modules` — явное подключение canonical rule IDs.
- `exclude_modules` — явное исключение модулей, кроме mandatory core.

False-флаг не удаляет правила, пришедшие из профиля. Это сделано специально: слабый/неполный detector не должен случайно ослаблять guidance. Для явного исключения используется `exclude_modules`.

Приоритет: direct user request/project-specific rules → manifest/profile selection → generic preferences.
