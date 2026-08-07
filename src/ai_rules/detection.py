from __future__ import annotations

import json
import re
import tomllib
from collections.abc import Sequence
from pathlib import Path

from ai_rules.models import Detection, DetectionConfidence

_MAX_TEXT = 256 * 1024
_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+")


def _dep_name(value: str) -> str:
    match = _NAME_RE.match(value.strip())
    return match.group(0).lower().replace("_", "-") if match else value.lower()


def _read_pyproject(root: Path) -> set[str]:
    path = root / "pyproject.toml"
    if not path.exists():
        return set()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return set()
    deps = data.get("project", {}).get("dependencies", [])
    result = {_dep_name(str(item)) for item in deps}
    for group in data.get("dependency-groups", {}).values():
        if isinstance(group, list):
            result.update(_dep_name(str(item)) for item in group)
    return result


def _read_package(root: Path) -> set[str]:
    path = root / "package.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    result: set[str] = set()
    for section in ("dependencies", "devDependencies"):
        values = data.get(section, {})
        if isinstance(values, dict):
            result.update(str(key).lower() for key in values)
    return result


def _bounded_text(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.read(_MAX_TEXT).lower()
    except OSError:
        return ""


def detect_project(root: Path) -> tuple[Detection, ...]:
    root = root.resolve()
    pydeps = _read_pyproject(root)
    jsdeps = _read_package(root)
    findings: dict[str, Detection] = {}

    def add(key: str, confidence: DetectionConfidence, evidence: str) -> None:
        current = findings.get(key)
        if current is None:
            findings[key] = Detection(key, confidence, (evidence,))
            return
        rank = {
            DetectionConfidence.NOT_DETECTED: 0,
            DetectionConfidence.PROBABLE: 1,
            DetectionConfidence.DETECTED: 2,
        }
        selected = confidence if rank[confidence] > rank[current.confidence] else current.confidence
        evidence_items = (*current.evidence, evidence) if evidence not in current.evidence else current.evidence
        findings[key] = Detection(key, selected, evidence_items)

    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        add("python", DetectionConfidence.DETECTED, "Python project configuration detected")

    dep_map = {
        "fastapi": "fastapi",
        "django": "django",
        "django-modern-rest": "django-modern-rest",
        "msgspec": "msgspec",
        "pydantic": "pydantic",
        "sqlalchemy": "sqlalchemy",
        "alembic": "alembic",
        "redis": "redis",
        "celery": "celery",
        "aio-pika": "aio-pika",
        "aiormq": "aiormq",
        "kafka-python": "kafka",
        "aiokafka": "kafka",
    }
    for dep, key in dep_map.items():
        if dep in pydeps:
            add(key, DetectionConfidence.DETECTED, f"pyproject.toml dependency: {dep}")

    if pydeps.intersection({"asyncpg", "psycopg", "psycopg2", "psycopg2-binary"}):
        dep = sorted(pydeps.intersection({"asyncpg", "psycopg", "psycopg2", "psycopg2-binary"}))[0]
        add("postgresql", DetectionConfidence.DETECTED, f"pyproject.toml dependency: {dep}")
    if pydeps.intersection({"aio-pika", "aiormq"}):
        dep = sorted(pydeps.intersection({"aio-pika", "aiormq"}))[0]
        add("rabbitmq", DetectionConfidence.DETECTED, f"pyproject.toml AMQP dependency: {dep}")
    if (root / "alembic.ini").exists():
        add("alembic", DetectionConfidence.DETECTED, "file exists: alembic.ini")
    if (root / "manage.py").exists():
        add("django", DetectionConfidence.DETECTED, "file exists: manage.py")

    for dep, key in {
        "next": "nextjs",
        "react": "react",
        "typescript": "typescript",
        "@tanstack/react-query": "tanstack-query",
        "zustand": "zustand",
        "zod": "zod",
    }.items():
        if dep in jsdeps:
            add(key, DetectionConfidence.DETECTED, f"package.json dependency: {dep}")

    docker_candidates = [
        root / "Dockerfile",
        root / "docker-compose.yml",
        root / "docker-compose.yaml",
        root / "compose.yml",
        root / "compose.yaml",
    ]
    for path in docker_candidates:
        if not path.exists():
            continue
        text = _bounded_text(path)
        if "rabbitmq" in text:
            add("rabbitmq", DetectionConfidence.PROBABLE, f"{path.name} contains: rabbitmq")
        if "nvidia/cuda" in text or "cuda" in text:
            add("gpu-cuda", DetectionConfidence.DETECTED, f"{path.name} contains CUDA image/config")
        if path.name == "Dockerfile":
            add("docker", DetectionConfidence.DETECTED, "file exists: Dockerfile")
        else:
            add("docker-compose", DetectionConfidence.DETECTED, f"file exists: {path.name}")

    if pydeps.intersection({"torch", "tensorflow", "onnxruntime-gpu", "cupy"}):
        dep = sorted(pydeps.intersection({"torch", "tensorflow", "onnxruntime-gpu", "cupy"}))[0]
        add("ml", DetectionConfidence.DETECTED, f"pyproject.toml ML dependency: {dep}")
        add("gpu-cuda", DetectionConfidence.PROBABLE, f"GPU-capable ML dependency: {dep}")

    for directory, key in (("helm", "helm"), ("charts", "helm"), ("k8s", "kubernetes"), ("kubernetes", "kubernetes")):
        if (root / directory).is_dir():
            add(key, DetectionConfidence.PROBABLE, f"directory exists: {directory}/")

    return tuple(findings[key] for key in sorted(findings))


def _is_detected(detections: Sequence[Detection], key: str) -> bool:
    return any(item.key == key and item.confidence is DetectionConfidence.DETECTED for item in detections)


def suggest_profile(detections: Sequence[Detection]) -> str:
    has_next = _is_detected(detections, "nextjs")
    has_fastapi = _is_detected(detections, "fastapi")
    has_django = _is_detected(detections, "django")
    has_python = _is_detected(detections, "python")
    if has_next and (has_fastapi or has_django):
        return "fullstack-python"
    if has_fastapi:
        return "fastapi-backend"
    if has_django:
        return "django-backend"
    if has_next:
        return "frontend-nextjs"
    if has_python:
        return "python-backend"
    return ""


def suggest_extra_profiles(detections: Sequence[Detection]) -> tuple[str, ...]:
    has_backend = _is_detected(detections, "fastapi") or _is_detected(detections, "python")
    has_gpu = any(
        item.key == "gpu-cuda" and item.confidence is not DetectionConfidence.NOT_DETECTED
        for item in detections
    )
    return ("ml-gpu-service",) if has_backend and has_gpu else ()


def render_detection_report(root: Path) -> str:
    detections = detect_project(root)
    lines = ["Detected project stack:"]
    if not detections:
        lines.append("  no supported signals detected")
    for item in detections:
        evidence = "; ".join(item.evidence)
        lines.append(f"  {item.key}: {item.confidence.value} ({evidence})")
    primary = suggest_profile(detections)
    extras = suggest_extra_profiles(detections)
    lines.append(f"Suggested primary profile: {primary or 'none'}")
    if extras:
        lines.append(f"Suggested extra profiles: {', '.join(extras)}")
    return "\n".join(lines) + "\n"
