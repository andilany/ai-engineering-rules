# Configuration

[Русский](../ru/configuration.md) | **English**

## `.ai-rules.toml`

The manifest stores the selected profile, technology flags, extra profiles, explicit include/exclude rules, and the list of project adapters. It describes effective AI guidance; it is not an instruction to migrate the application's technology stack.

Main fields:

- `version` — manifest schema version;
- `profile` — primary profile;
- `rules_version` — rule-pack version;
- `ides` — ordered list: `codex`, `claude`, `cursor`, `copilot`, `gemini`;
- `extra_profiles` — additional profiles;
- `include_modules` / `exclude_modules` — explicit rule overrides;
- `language`, `backend`, `data`, `messaging`, `security`, `frontend`, `ml`, and `infrastructure` — technology flags.

Example:

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

`custom` is the minimal base used by the interactive wizard. It does not enable PostgreSQL, Redis, Docker, or Keycloak merely because a backend framework was selected.

Prebuilt profiles include `python-backend`, `fastapi-backend`, `django-backend`, `frontend-nextjs`, `ml-gpu-service`, and `fullstack-python`.

## Adapter selection

`airules init --ide cursor --ide claude` persists the selection in the manifest. Normal `sync` updates only selected adapters. `airules sync --ide gemini` is a temporary override and does not change the manifest.

A legacy manifest without `ides` is interpreted as enabling all supported project adapters.

## Project files

- `.ai-rules/generated.md` — generated effective snapshot;
- `.ai-rules/project.md` — user-owned project-specific instructions;
- agent adapters — generated/native projections of selected rules.

Explicit user requests and project-specific instructions take precedence over generic preferences.
