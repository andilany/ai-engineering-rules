from __future__ import annotations

from collections.abc import Mapping

from ai_rules.errors import ConfigurationError
from ai_rules.models import (
    EffectiveRules,
    ProfileDefinition,
    ProjectManifest,
    RuleDocument,
    RuleSeverity,
)
from ai_rules.profiles import resolve_profile

REQUIRED_CORE = ("core.agent-behavior", "core.external-actions")

MANIFEST_MODULES: dict[tuple[str, str], tuple[str, ...]] = {
    ("language", "python"): ("languages.python", "backend.async-python"),
    ("backend", "fastapi"): ("backend.fastapi", "backend.pydantic", "backend.uvicorn-asgi"),
    ("backend", "django"): ("backend.django",),
    ("backend", "django_modern_rest"): ("backend.django-modern-rest",),
    ("backend", "pydantic"): ("backend.pydantic",),
    ("backend", "msgspec"): ("backend.msgspec",),
    ("data", "postgresql"): ("data.postgresql",),
    ("data", "sqlalchemy"): ("data.sqlalchemy",),
    ("data", "alembic"): ("data.alembic",),
    ("data", "django_orm"): ("data.django-orm", "data.django-migrations"),
    ("data", "redis"): ("data.redis",),
    ("data", "mongodb"): ("data.mongodb",),
    ("messaging", "rabbitmq"): ("messaging.rabbitmq",),
    ("messaging", "aio_pika"): ("messaging.aio-pika",),
    ("messaging", "aiormq"): ("messaging.aiormq",),
    ("messaging", "celery"): ("messaging.celery",),
    ("messaging", "kafka"): ("messaging.kafka",),
    ("security", "keycloak"): ("security.keycloak",),
    ("frontend", "nextjs"): ("frontend.nextjs",),
    ("ml", "gpu"): ("ml.gpu-cuda", "ml.vram"),
    ("infrastructure", "docker"): ("infrastructure.docker",),
    ("infrastructure", "compose"): ("infrastructure.docker-compose",),
    ("infrastructure", "kubernetes"): ("infrastructure.kubernetes",),
    ("infrastructure", "helm"): ("infrastructure.helm",),
    ("infrastructure", "caddy"): ("infrastructure.caddy",),
    ("infrastructure", "nginx"): ("infrastructure.nginx",),
}

_SEVERITY_ORDER = {
    RuleSeverity.REQUIRED: 0,
    RuleSeverity.USER_DECISION: 1,
    RuleSeverity.PREFERRED: 2,
    RuleSeverity.CONDITIONAL: 3,
    RuleSeverity.OPTIONAL: 4,
}


def validate_catalog_integrity(
    profiles: Mapping[str, ProfileDefinition],
    rules: Mapping[str, RuleDocument],
) -> None:
    referenced: list[str] = list(REQUIRED_CORE)

    for profile_name in profiles:
        for module in resolve_profile(profile_name, profiles):
            if module not in referenced:
                referenced.append(module)

    for mapped_modules in MANIFEST_MODULES.values():
        for module in mapped_modules:
            if module not in referenced:
                referenced.append(module)

    missing = [module for module in referenced if module not in rules]
    if missing:
        raise ConfigurationError(
            "Canonical rule catalog is incomplete; missing modules: " + ", ".join(missing)
        )


def compose_effective_rules(
    manifest: ProjectManifest,
    profiles: Mapping[str, ProfileDefinition],
    rules: Mapping[str, RuleDocument],
) -> EffectiveRules:
    modules: list[str] = []
    sources: dict[str, str] = {}

    def add(module: str, source: str) -> None:
        if module not in modules:
            modules.append(module)
            sources[module] = source

    for core in REQUIRED_CORE:
        if core in rules:
            add(core, "core:required")

    for module in resolve_profile(manifest.profile, profiles):
        add(module, f"profile:{manifest.profile}")
    for profile_name in manifest.extra_profiles:
        for module in resolve_profile(profile_name, profiles):
            add(module, f"profile:{profile_name}")

    for (section, key), mapped in MANIFEST_MODULES.items():
        values = getattr(manifest, section)
        if bool(values.get(key, False)):
            for module in mapped:
                add(module, f"manifest:{section}.{key}")

    for module in manifest.include_modules:
        add(module, "manifest:include")

    for module in manifest.exclude_modules:
        if module in REQUIRED_CORE:
            raise ConfigurationError(f"Cannot exclude required core module: {module}")
        if module in modules:
            modules.remove(module)
            sources.pop(module, None)

    missing = [module for module in modules if module not in rules]
    if missing:
        raise ConfigurationError(f"Unknown canonical modules: {', '.join(missing)}")

    original_order = {module: index for index, module in enumerate(modules)}
    ordered_rules = tuple(
        sorted(
            (rules[module] for module in modules),
            key=lambda item: (_SEVERITY_ORDER[item.severity], original_order[item.id], item.id),
        )
    )
    return EffectiveRules(tuple(modules), ordered_rules, sources)
