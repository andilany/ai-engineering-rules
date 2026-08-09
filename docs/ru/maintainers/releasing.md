# Release process

**Русский** | [English](../../en/maintainers/releasing.md)

`main` — stable channel, `dev` — development channel. `CHANGELOG.md` является единственным источником user-visible release history и GitHub Release body.

Для версии `X.Y.Z`:

- `pyproject.toml` и `ai_rules.__version__` содержат `X.Y.Z`;
- `CHANGELOG.md` содержит непустую секцию `## [X.Y.Z]`;
- verified `dev` слит в `main`;
- tag `vX.Y.Z` указывает на текущий verified commit `main`.

Перед merge:

```bash
python scripts/check_release.py --tag vX.Y.Z
python -m pytest -q
python -m compileall -q src
uv build
```

После merge создайте и отправьте tag. `.github/workflows/release.yml` повторно валидирует metadata, запускает тесты и build, smoke-тестирует wheel, создаёт/обновляет GitHub Release и загружает artifacts.

Не создавайте отдельные version-specific release-note files: release body извлекается из `CHANGELOG.md`.
