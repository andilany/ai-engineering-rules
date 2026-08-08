# Release process

`main` is the stable channel. `dev` is the development channel.

Every release uses semantic versioning. `CHANGELOG.md` is the single source of user-visible release history and GitHub Release notes.

## Required release metadata

For version `X.Y.Z`:

- `pyproject.toml` contains `version = "X.Y.Z"`;
- `CHANGELOG.md` contains a non-empty `## [X.Y.Z]` section;
- the release commit is merged from `dev` into `main` and verified;
- tag `vX.Y.Z` points to the current `main` commit;
- a GitHub Release exists for tag `vX.Y.Z`.

The body of the GitHub Release is generated directly from the matching `CHANGELOG.md` section. Do not maintain a second version-specific release-notes file.

## Before merging to main

Run from the release candidate on `dev`:

```bash
python scripts/check_release.py --tag vX.Y.Z
python -m pytest -q
python -m compileall -q src
uv build
```

Review the `[X.Y.Z]` section in `CHANGELOG.md`, then merge the verified `dev` release candidate into `main`.

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
2. verifies version and changelog consistency;
3. extracts the matching changelog section as the GitHub Release body;
4. runs the test suite and `compileall`;
5. builds wheel and source distribution artifacts;
6. smoke-tests the built wheel;
7. creates the GitHub Release, or updates it when the workflow is re-run;
8. uploads the built artifacts to the Release.

The workflow uses the repository-scoped `GITHUB_TOKEN` with `contents: write`. No personal token is required.

## After release

Verify the stable channel:

```bash
uv tool install --force "git+https://github.com/andilany/ai-engineering-rules.git@main"
airules version
```

Then continue development on `dev`. Add user-visible changes to the `[Unreleased]` section as development progresses. During release preparation, move those entries into the new `[X.Y.Z]` section and update the project version.
