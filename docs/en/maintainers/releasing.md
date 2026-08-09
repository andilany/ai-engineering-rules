# Release process

[Русский](../../ru/maintainers/releasing.md) | **English**

`main` is the stable channel and `dev` is the development channel. `CHANGELOG.md` is the single source of user-visible release history and the GitHub Release body.

For version `X.Y.Z`:

- `pyproject.toml` and `ai_rules.__version__` contain `X.Y.Z`;
- `CHANGELOG.md` contains a non-empty `## [X.Y.Z]` section;
- the verified `dev` candidate is merged into `main`;
- tag `vX.Y.Z` points to the current verified `main` commit.

Before merging:

```bash
python scripts/check_release.py --tag vX.Y.Z
python -m pytest -q
python -m compileall -q src
uv build
```

After merging, create and push the tag. `.github/workflows/release.yml` revalidates metadata, runs tests and the build, smoke-tests the wheel, creates or updates the GitHub Release, and uploads artifacts.

Do not maintain separate version-specific release-note files: the release body is extracted from `CHANGELOG.md`.
