from pathlib import Path

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
