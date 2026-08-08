from __future__ import annotations

from dataclasses import dataclass

import typer

from ai_rules.detection import Detection, DetectionConfidence
from ai_rules.ides import SUPPORTED_IDES
from ai_rules.models import ProjectManifest


@dataclass(frozen=True, slots=True)
class Choice:
    key: str
    label: str


@dataclass(frozen=True, slots=True)
class WizardSelection:
    ides: tuple[str, ...]
    backend: tuple[str, ...] = ()
    frontend: tuple[str, ...] = ()
    ml: tuple[str, ...] = ()
    data: tuple[str, ...] = ()
    messaging: tuple[str, ...] = ()
    infrastructure: tuple[str, ...] = ()
    security: tuple[str, ...] = ()


AREA_CHOICES = (
    Choice("backend", "Backend"),
    Choice("frontend", "Frontend"),
    Choice("ml", "ML / AI / GPU"),
    Choice("data", "Databases / data stores"),
    Choice("messaging", "Messaging / task queues"),
    Choice("infrastructure", "Infrastructure / Docker / Kubernetes"),
    Choice("security", "Authentication / application security"),
)
BACKEND_CHOICES = (
    Choice("fastapi", "FastAPI"),
    Choice("django", "Django"),
    Choice("python", "Generic Python backend / API"),
)
FRONTEND_CHOICES = (
    Choice("nextjs", "Next.js (includes React + TypeScript rules)"),
    Choice("react", "React (includes TypeScript rules)"),
    Choice("typescript", "TypeScript only"),
    Choice("tailwind", "Tailwind CSS"),
    Choice("shadcn", "shadcn/ui + Radix"),
    Choice("tanstack-query", "TanStack Query"),
    Choice("zustand", "Zustand"),
    Choice("forms-zod", "React Hook Form + Zod"),
    Choice("api-client", "Frontend API client"),
)
ML_CHOICES = (
    Choice("general", "ML service boundaries, batching and pipelines"),
    Choice("gpu", "CUDA / GPU / VRAM"),
    Choice("llm", "LLM integrations"),
)
DATA_CHOICES = (
    Choice("postgresql", "PostgreSQL"),
    Choice("sqlalchemy", "SQLAlchemy"),
    Choice("alembic", "Alembic"),
    Choice("django_orm", "Django ORM + migrations"),
    Choice("redis", "Redis"),
    Choice("mongodb", "MongoDB"),
)
MESSAGING_CHOICES = (
    Choice("rabbitmq", "RabbitMQ"),
    Choice("aio_pika", "aio-pika"),
    Choice("aiormq", "aiormq"),
    Choice("celery", "Celery"),
    Choice("kafka", "Kafka"),
)
INFRA_CHOICES = (
    Choice("docker", "Docker"),
    Choice("compose", "Docker Compose"),
    Choice("kubernetes", "Kubernetes"),
    Choice("helm", "Helm"),
    Choice("caddy", "Caddy"),
    Choice("nginx", "Nginx"),
    Choice("ci-cd", "CI/CD"),
    Choice("healthchecks", "Health checks"),
    Choice("observability", "Observability"),
    Choice("opentelemetry", "OpenTelemetry"),
    Choice("prometheus-grafana", "Prometheus + Grafana"),
    Choice("gitops", "GitOps"),
    Choice("ansible", "Ansible"),
    Choice("linux", "Linux operations"),
    Choice("windows", "Windows development / operations"),
)
SECURITY_CHOICES = (
    Choice("auth", "Authentication + OAuth2/OIDC + JWT + RBAC"),
    Choice("keycloak", "Keycloak (includes auth/OIDC/JWT/RBAC rules)"),
)
IDE_CHOICES = tuple(Choice(key, label) for key, label in (
    ("codex", "OpenAI Codex"),
    ("claude", "Claude Code"),
    ("cursor", "Cursor"),
    ("copilot", "GitHub Copilot"),
    ("gemini", "Gemini CLI"),
))


def parse_multiselect(raw: str, count: int, defaults: tuple[int, ...]) -> tuple[int, ...]:
    value = raw.strip().lower()
    if not value:
        return defaults
    if value == "all":
        return tuple(range(count))
    if value == "none":
        return ()
    selected: list[int] = []
    for token in value.split(","):
        token = token.strip()
        if not token.isdigit():
            raise ValueError(f"Invalid selection: {token}")
        index = int(token) - 1
        if index < 0 or index >= count:
            raise ValueError(f"Selection out of range: {token}")
        if index not in selected:
            selected.append(index)
    return tuple(selected)


def _detected_keys(detections: tuple[Detection, ...]) -> set[str]:
    return {
        item.key
        for item in detections
        if item.confidence is not DetectionConfidence.NOT_DETECTED
    }


def _defaults_for_choices(
    choices: tuple[Choice, ...],
    keys: set[str],
    aliases: dict[str, set[str]] | None = None,
) -> tuple[int, ...]:
    aliases = aliases or {}
    defaults: list[int] = []
    for index, choice in enumerate(choices):
        signals = aliases.get(choice.key, {choice.key})
        if keys.intersection(signals):
            defaults.append(index)
    return tuple(defaults)


def _area_defaults(detections: tuple[Detection, ...]) -> tuple[int, ...]:
    keys = _detected_keys(detections)
    area_signals = {
        "backend": {"python", "fastapi", "django"},
        "frontend": {"nextjs", "react", "typescript"},
        "ml": {"ml", "gpu-cuda"},
        "data": {"postgresql", "sqlalchemy", "alembic", "redis"},
        "messaging": {"rabbitmq", "aio-pika", "aiormq", "celery", "kafka"},
        "infrastructure": {"docker", "docker-compose", "kubernetes", "helm"},
    }
    return tuple(
        index
        for index, choice in enumerate(AREA_CHOICES)
        if keys.intersection(area_signals.get(choice.key, set()))
    )


def _prompt_multiselect(
    title: str,
    choices: tuple[Choice, ...],
    *,
    defaults: tuple[int, ...] = (),
    require_one: bool = False,
) -> tuple[str, ...]:
    typer.echo(f"\n{title}")
    for index, choice in enumerate(choices, start=1):
        suffix = " [detected]" if index - 1 in defaults else ""
        typer.echo(f"  {index}. {choice.label}{suffix}")
    typer.echo("Use comma-separated numbers. You can also enter 'all' or 'none'.")
    default_text = ",".join(str(index + 1) for index in defaults)
    while True:
        raw = typer.prompt("Select", default=default_text, show_default=bool(default_text))
        try:
            selected = parse_multiselect(raw, len(choices), defaults)
        except ValueError as exc:
            typer.echo(f"Invalid selection: {exc}", err=True)
            continue
        if require_one and not selected:
            typer.echo("Select at least one option.", err=True)
            continue
        return tuple(choices[index].key for index in selected)


def _include(manifest: ProjectManifest, *modules: str) -> None:
    for module in modules:
        if module not in manifest.include_modules:
            manifest.include_modules.append(module)


def build_manifest(selection: WizardSelection, *, rules_version: str) -> ProjectManifest:
    manifest = ProjectManifest(
        profile="custom",
        rules_version=rules_version,
        ides=list(selection.ides),
    )

    if selection.backend or selection.ml:
        manifest.language["python"] = True

    for backend in selection.backend:
        if backend == "fastapi":
            manifest.backend["fastapi"] = True
        elif backend == "django":
            manifest.backend["django"] = True
            manifest.data["django_orm"] = True
        elif backend == "python":
            _include(manifest, "backend.api-design")

    for frontend in selection.frontend:
        if frontend == "nextjs":
            manifest.frontend["nextjs"] = True
            _include(manifest, "frontend.typescript", "frontend.react")
        elif frontend == "react":
            _include(manifest, "frontend.typescript", "frontend.react")
        elif frontend == "typescript":
            _include(manifest, "frontend.typescript")
        elif frontend == "tailwind":
            _include(manifest, "frontend.tailwind")
        elif frontend == "shadcn":
            _include(manifest, "frontend.shadcn-radix")
        elif frontend == "tanstack-query":
            _include(manifest, "frontend.tanstack-query")
        elif frontend == "zustand":
            _include(manifest, "frontend.zustand")
        elif frontend == "forms-zod":
            _include(manifest, "frontend.forms-zod")
        elif frontend == "api-client":
            _include(manifest, "frontend.api-client")

    if "general" in selection.ml:
        _include(
            manifest,
            "ml.service-boundaries",
            "ml.batching",
            "ml.parallel-processing",
            "ml.pipelines",
        )
    if "gpu" in selection.ml:
        manifest.ml["gpu"] = True
    if "llm" in selection.ml:
        _include(manifest, "ml.llm-integrations")

    for key in selection.data:
        manifest.data[key] = True
    for key in selection.messaging:
        manifest.messaging[key] = True

    mapped_infra = {"docker", "compose", "kubernetes", "helm", "caddy", "nginx"}
    infra_modules = {
        "ci-cd": "infrastructure.ci-cd",
        "gitops": "infrastructure.gitops",
        "healthchecks": "infrastructure.healthchecks",
        "observability": "infrastructure.observability",
        "opentelemetry": "infrastructure.opentelemetry",
        "prometheus-grafana": "infrastructure.prometheus-grafana",
        "ansible": "infrastructure.ansible",
        "linux": "infrastructure.linux",
        "windows": "infrastructure.windows",
    }
    for key in selection.infrastructure:
        if key in mapped_infra:
            manifest.infrastructure[key] = True
        elif key in infra_modules:
            _include(manifest, infra_modules[key])

    if "auth" in selection.security:
        _include(
            manifest,
            "security.auth",
            "security.oauth2-oidc",
            "security.jwt",
            "security.rbac",
        )
    if "keycloak" in selection.security:
        manifest.security["keycloak"] = True
        _include(
            manifest,
            "security.auth",
            "security.oauth2-oidc",
            "security.jwt",
            "security.rbac",
        )
    return manifest


def run_wizard(
    detections: tuple[Detection, ...],
    *,
    rules_version: str,
) -> tuple[ProjectManifest, WizardSelection]:
    keys = _detected_keys(detections)
    typer.echo("\nInteractive airules setup")
    typer.echo("Detected technologies are preselected where possible.")

    areas = _prompt_multiselect(
        "Which parts of this project should receive rules?",
        AREA_CHOICES,
        defaults=_area_defaults(detections),
    )

    backend: tuple[str, ...] = ()
    frontend: tuple[str, ...] = ()
    ml: tuple[str, ...] = ()
    data: tuple[str, ...] = ()
    messaging: tuple[str, ...] = ()
    infrastructure: tuple[str, ...] = ()
    security: tuple[str, ...] = ()

    if "backend" in areas:
        backend_defaults = _defaults_for_choices(BACKEND_CHOICES, keys)
        if not backend_defaults and "python" in keys:
            backend_defaults = (2,)
        backend = _prompt_multiselect(
            "Backend rules",
            BACKEND_CHOICES,
            defaults=backend_defaults,
            require_one=True,
        )
    if "frontend" in areas:
        frontend = _prompt_multiselect(
            "Frontend rules",
            FRONTEND_CHOICES,
            defaults=_defaults_for_choices(FRONTEND_CHOICES, keys),
            require_one=True,
        )
    if "ml" in areas:
        ml_defaults: list[int] = []
        if "ml" in keys:
            ml_defaults.append(0)
        if "gpu-cuda" in keys:
            ml_defaults.append(1)
        if not ml_defaults:
            ml_defaults.append(0)
        ml = _prompt_multiselect(
            "ML / AI rules",
            ML_CHOICES,
            defaults=tuple(ml_defaults),
            require_one=True,
        )
    if "data" in areas:
        data = _prompt_multiselect(
            "Database / data rules",
            DATA_CHOICES,
            defaults=_defaults_for_choices(DATA_CHOICES, keys),
            require_one=True,
        )
    if "messaging" in areas:
        messaging = _prompt_multiselect(
            "Messaging rules",
            MESSAGING_CHOICES,
            defaults=_defaults_for_choices(
                MESSAGING_CHOICES,
                keys,
                aliases={"aio_pika": {"aio-pika"}},
            ),
            require_one=True,
        )
    if "infrastructure" in areas:
        infrastructure = _prompt_multiselect(
            "Infrastructure rules",
            INFRA_CHOICES,
            defaults=_defaults_for_choices(
                INFRA_CHOICES,
                keys,
                aliases={"compose": {"docker-compose"}},
            ),
            require_one=True,
        )
    if "security" in areas:
        security = _prompt_multiselect(
            "Authentication / security rules",
            SECURITY_CHOICES,
            require_one=True,
        )

    ides = _prompt_multiselect(
        "Which AI coding agents should airules configure?",
        IDE_CHOICES,
        require_one=True,
    )
    selection = WizardSelection(
        ides=ides,
        backend=backend,
        frontend=frontend,
        ml=ml,
        data=data,
        messaging=messaging,
        infrastructure=infrastructure,
        security=security,
    )
    return build_manifest(selection, rules_version=rules_version), selection


def render_selection_summary(selection: WizardSelection) -> str:
    lines = ["Selected airules configuration:"]
    for label, values in (
        ("Backend", selection.backend),
        ("Frontend", selection.frontend),
        ("ML / AI", selection.ml),
        ("Data", selection.data),
        ("Messaging", selection.messaging),
        ("Infrastructure", selection.infrastructure),
        ("Security", selection.security),
        ("Agents", selection.ides),
    ):
        lines.append(f"  {label}: {', '.join(values) if values else 'none'}")
    return "\n".join(lines) + "\n"
