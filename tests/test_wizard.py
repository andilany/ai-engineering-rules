from __future__ import annotations

import pytest

from ai_rules.models import Detection, DetectionConfidence
from ai_rules.wizard import (
    AREA_CHOICES,
    WizardSelection,
    _area_defaults,
    build_manifest,
    parse_multiselect,
)


def test_parse_multiselect_supports_defaults_all_none_and_deduplication() -> None:
    assert parse_multiselect("", 4, (0, 2)) == (0, 2)
    assert parse_multiselect("all", 3, ()) == (0, 1, 2)
    assert parse_multiselect("none", 3, (0,)) == ()
    assert parse_multiselect("3,1,3", 4, ()) == (2, 0)


@pytest.mark.parametrize("raw", ["x", "0", "5", "1,x"])
def test_parse_multiselect_rejects_invalid_values(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_multiselect(raw, 4, ())


def test_detected_defaults_preselect_relevant_project_areas() -> None:
    detections = (
        Detection("fastapi", DetectionConfidence.DETECTED),
        Detection("gpu-cuda", DetectionConfidence.DETECTED),
        Detection("docker-compose", DetectionConfidence.DETECTED),
    )

    selected = {AREA_CHOICES[index].key for index in _area_defaults(detections)}

    assert {"backend", "ml", "infrastructure"} <= selected


def test_build_manifest_only_includes_selected_rule_families() -> None:
    selection = WizardSelection(
        ides=("cursor",),
        backend=("fastapi",),
        ml=("gpu", "llm"),
        data=("postgresql",),
        infrastructure=("docker", "compose"),
        security=("auth",),
    )

    manifest = build_manifest(selection, rules_version="0.3.1")

    assert manifest.profile == "custom"
    assert manifest.ides == ["cursor"]
    assert manifest.language == {"python": True}
    assert manifest.backend == {"fastapi": True}
    assert manifest.data == {"postgresql": True}
    assert manifest.infrastructure == {"docker": True, "compose": True}
    assert manifest.ml == {"gpu": True}
    assert "ml.llm-integrations" in manifest.include_modules
    assert "security.auth" in manifest.include_modules
    assert "frontend.react" not in manifest.include_modules
