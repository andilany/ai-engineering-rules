# Release process

`main` is the stable channel. `dev` is the development channel.

Every release uses semantic versioning and must have the same version in all release metadata before the tag is created.

## Required release artifacts

For version `X.Y.Z`:

- `pyproject.toml` contains `version = "X.Y.Z"`;
- `CHANGELOG.md` contains a `## [X.Y.Z]` section;
- `docs/releases/vX.Y.Z.md` contains detailed release notes;
- the release commit is merged from `dev` into `main` and verified;
- tag `vX.Y.Z` points to the current `main` commit;
- a GitHub Release exists for tag `vX.Y.Z`.

The changelog is cumulative and remains the concise history of user-visible changes. Release notes are version-specific and may contain migration details, validation results, compatibility notes, and upgrade instructions.

## Before merging to main

Run from the release candidate on `dev`:

```bash
python scripts/check_release.py --tag vX.Y.Z
python -m pytest -q
python -m compileall -q src
uv build
```

Review `CHANGELOG.md` and `docs/releases/vX.Y.Z.md`, then merge the verified `dev` release candidate into `main`.

## Tagging and GitHub Release

After the verified release commit is on `main`:

```bash
git checkout main
git pull --ff-only
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

Pushing the tag triggers `.github/workflows/release.yml`. The workflow:

1. verifies that the tag points to the current `main` commit;
2. verifies version/changelog/release-note consistency;
3. runs the test suite and `compileall`;
4. builds wheel and source distribution artifacts;
5. smoke-tests the built wheel;
6. creates the GitHub Release, or updates it when the workflow is re-run;
7. uploads the built artifacts to the Release.

The workflow uses the repository-scoped `GITHUB_TOKEN` with `contents: write`. No personal token is required.

## After release

Verify the stable channel:

```bash
uv tool install --force "git+https://github.com/andilany/ai-engineering-rules.git@main"
airules version
```

Then continue development on `dev`. Add user-visible changes to `CHANGELOG.md` as development progresses so release preparation is a review step rather than a reconstruction step.
