from pathlib import Path

import pytest

from ai_rules.errors import ConfigurationError
from ai_rules.ides import normalize_ides
from ai_rules.manifest import load_manifest, render_manifest
from ai_rules.models import ProjectManifest


def test_manifest_round_trip_preserves_comment_and_known_values(tmp_path: Path) -> None:
    source = '''# project AI rules
version = 1
profile = "fastapi-backend"
rules_version = "0.1.0"

[language]
python = true

[backend]
fastapi = true
'''
    path = tmp_path / ".ai-rules.toml"
    path.write_text(source, encoding="utf-8")

    manifest = load_manifest(path)
    rendered = render_manifest(manifest, existing=source)

    assert manifest.profile == "fastapi-backend"
    assert manifest.language["python"] is True
    assert manifest.backend["fastapi"] is True
    assert "# project AI rules" in rendered
    assert 'profile = "fastapi-backend"' in rendered


def test_manifest_round_trip_persists_ides_in_order(tmp_path: Path) -> None:
    manifest = ProjectManifest(profile="fastapi-backend", ides=["codex", "cursor"])
    rendered = render_manifest(manifest)
    path = tmp_path / ".ai-rules.toml"
    path.write_text(rendered, encoding="utf-8")

    loaded = load_manifest(path)

    assert loaded.ides == ["codex", "cursor"]
    assert 'ides = ["codex", "cursor"]' in rendered


def test_manifest_without_ides_is_legacy_and_loads_none(tmp_path: Path) -> None:
    path = tmp_path / ".ai-rules.toml"
    path.write_text('version = 1\nprofile = "python-backend"\n', encoding="utf-8")

    manifest = load_manifest(path)

    assert manifest.ides is None


def test_manifest_rejects_explicit_empty_ides(tmp_path: Path) -> None:
    path = tmp_path / ".ai-rules.toml"
    path.write_text('version = 1\nprofile = "python-backend"\nides = []\n', encoding="utf-8")

    with pytest.raises(ConfigurationError, match="ides"):
        load_manifest(path)


def test_normalize_ides_deduplicates_and_preserves_order() -> None:
    assert normalize_ides(["Codex", "cursor", "codex"], default_all=False) == (
        "codex",
        "cursor",
    )


def test_normalize_ides_rejects_unknown_value() -> None:
    with pytest.raises(ConfigurationError, match="Supported values"):
        normalize_ides(["vscode"], default_all=False)
