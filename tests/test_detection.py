from pathlib import Path

from ai_rules.detection import detect_project, suggest_extra_profiles, suggest_profile
from ai_rules.models import DetectionConfidence

FIXTURES = Path(__file__).parent / "fixtures" / "projects"


def detected(root: str) -> dict[str, tuple[DetectionConfidence, tuple[str, ...]]]:
    return {item.key: (item.confidence, item.evidence) for item in detect_project(FIXTURES / root)}


def test_fastapi_detection_and_profile() -> None:
    items = detected("fastapi")
    for key in ("python", "fastapi", "sqlalchemy", "alembic", "postgresql", "rabbitmq", "redis"):
        assert items[key][0] is DetectionConfidence.DETECTED
    assert suggest_profile(detect_project(FIXTURES / "fastapi")) == "fastapi-backend"


def test_django_detection_and_profile() -> None:
    items = detected("django")
    for key in ("python", "django", "django-modern-rest", "msgspec"):
        assert items[key][0] is DetectionConfidence.DETECTED
    assert suggest_profile(detect_project(FIXTURES / "django")) == "django-backend"


def test_frontend_detection() -> None:
    items = detected("fullstack")
    for key in ("nextjs", "react", "typescript"):
        assert items[key][0] is DetectionConfidence.DETECTED
    assert suggest_profile(detect_project(FIXTURES / "fullstack")) == "frontend-nextjs"


def test_ml_detection_suggests_extra_profile() -> None:
    detections = detect_project(FIXTURES / "ml")
    items = {item.key: item for item in detections}
    assert items["gpu-cuda"].confidence in {DetectionConfidence.DETECTED, DetectionConfidence.PROBABLE}
    assert suggest_profile(detections) == "fastapi-backend"
    assert suggest_extra_profiles(detections) == ("ml-gpu-service",)


def test_ambiguous_rabbitmq_does_not_select_backend() -> None:
    detections = detect_project(FIXTURES / "ambiguous")
    items = {item.key: item for item in detections}
    assert items["rabbitmq"].confidence is DetectionConfidence.PROBABLE
    assert suggest_profile(detections) == ""
