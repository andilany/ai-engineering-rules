import pytest

from ai_rules.errors import ConfigurationError
from ai_rules.models import RuleSeverity
from ai_rules.precedence import validate_catalog_integrity
from ai_rules.profiles import load_profiles, resolve_profile
from ai_rules.rules import load_rules


def test_all_profile_modules_exist_and_core_is_present() -> None:
    rules = load_rules()
    profiles = load_profiles(validate_modules=False)
    for name in profiles:
        for module in resolve_profile(name, profiles):
            assert module in rules, f"{name} references missing {module}"
    for required in ("core.agent-behavior", "core.external-actions", "core.verification"):
        assert required in rules


def test_architecture_choices_are_not_mandated() -> None:
    rules = load_rules()
    for rule_id in (
        "architecture.architecture-decisions",
        "architecture.microservices",
        "architecture.event-driven",
        "architecture.orchestration",
        "architecture.api-gateway",
        "messaging.kafka",
    ):
        assert rules[rule_id].severity in {RuleSeverity.USER_DECISION, RuleSeverity.CONDITIONAL}
        assert "approval" in rules[rule_id].body.lower() or "user" in rules[rule_id].body.lower()


def test_security_testing_and_python_safety_invariants() -> None:
    rules = load_rules()
    assert "coverage percentage is a signal" in rules["quality.testing"].body.lower()
    auth = rules["security.auth"].body.lower()
    assert "localstorage" in auth and "default" in auth
    python = rules["languages.python"].body.lower()
    assert "uv" in python and "approval" in python and "existing" in python
    django_modern = rules["backend.django-modern-rest"].body.lower()
    assert "exception" in django_modern and "alpha" in django_modern
    external = rules["core.external-actions"].body.lower()
    assert "commit" in external and "explicit user approval" in external


def test_frontend_ml_and_infra_rules_are_non_migratory() -> None:
    rules = load_rules()
    for rule_id in ("infrastructure.kubernetes", "infrastructure.helm", "infrastructure.gitops"):
        assert rules[rule_id].severity is RuleSeverity.USER_DECISION
    assert "existing" in rules["infrastructure.caddy"].body.lower()
    assert "cpu" in rules["ml.gpu-cuda"].body.lower()
    assert "vram" in rules["ml.vram"].body.lower()
    assert "increasing complexity" in rules["infrastructure.docker-compose"].body.lower()


def test_catalog_integrity_reports_all_missing_mapped_modules() -> None:
    rules = load_rules()
    profiles = load_profiles(validate_modules=False)
    reduced = {
        rule_id: rule
        for rule_id, rule in rules.items()
        if not rule_id.startswith("infrastructure.")
    }

    with pytest.raises(ConfigurationError) as exc_info:
        validate_catalog_integrity(profiles, reduced)

    message = str(exc_info.value)
    for rule_id in (
        "infrastructure.docker",
        "infrastructure.docker-compose",
        "infrastructure.kubernetes",
        "infrastructure.helm",
        "infrastructure.caddy",
        "infrastructure.nginx",
    ):
        assert rule_id in message


def test_catalog_integrity_accepts_complete_catalog() -> None:
    validate_catalog_integrity(load_profiles(validate_modules=False), load_rules())
