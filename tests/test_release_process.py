from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_metadata_uses_mit() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]

    assert project["license"] == "MIT"
    assert project["description"] == "Reusable engineering rules for AI coding agents"
    assert (ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License\n")


def test_current_version_has_changelog_and_public_readmes() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{version}]" in changelog
    assert not (ROOT / "docs" / "releases").exists()
    assert not (ROOT / "docs" / "superpowers").exists()

    for path in (ROOT / "README.md", ROOT / "README_EN.md"):
        content = path.read_text(encoding="utf-8").lower()
        assert "mit license" in content or "license](license)" in content


def test_release_check_accepts_current_version() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    result = subprocess.run(
        [sys.executable, "scripts/check_release.py", "--tag", f"v{version}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"release metadata OK: v{version}" in result.stdout


def test_release_workflow_is_tag_driven_and_updates_existing_release() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert "tags:" in workflow
    assert '"v*.*.*"' in workflow
    assert "contents: write" in workflow
    assert "scripts/check_release.py" in workflow
    assert "uv run pytest -q" in workflow
    assert "uv build" in workflow
    assert 'gh release view "$TAG"' in workflow
    assert 'gh release edit "$TAG"' in workflow
    assert 'gh release create "$TAG"' in workflow
    assert '--notes-output "$RUNNER_TEMP/release-notes.md"' in workflow
    assert '--notes-file "$RUNNER_TEMP/release-notes.md"' in workflow
    assert "docs/releases" not in workflow
    assert 'gh release upload "$TAG" dist/* --clobber' in workflow


def test_release_check_can_extract_github_release_body(tmp_path: Path) -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    notes = tmp_path / "release-notes.md"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_release.py",
            "--tag",
            f"v{version}",
            "--notes-output",
            str(notes),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    body = notes.read_text(encoding="utf-8")
    assert body.strip()
    assert body.lstrip().startswith("- ")
    assert f"## [{version}]" not in body
    assert "\n## " not in body
