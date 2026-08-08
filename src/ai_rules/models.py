from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Mapping


class RuleSeverity(StrEnum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    CONDITIONAL = "conditional"
    OPTIONAL = "optional"
    USER_DECISION = "user_decision"

    @property
    def rank(self) -> int:
        return {
            RuleSeverity.REQUIRED: 50,
            RuleSeverity.PREFERRED: 40,
            RuleSeverity.USER_DECISION: 40,
            RuleSeverity.CONDITIONAL: 30,
            RuleSeverity.OPTIONAL: 20,
        }[self]


class DetectionConfidence(StrEnum):
    DETECTED = "detected"
    PROBABLE = "probable"
    NOT_DETECTED = "not_detected"


@dataclass(frozen=True, slots=True)
class RuleDocument:
    id: str
    title: str
    severity: RuleSeverity
    scopes: tuple[str, ...]
    path: str
    body: str


@dataclass(frozen=True, slots=True)
class ProfileDefinition:
    name: str
    description: str
    extends: tuple[str, ...]
    modules: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Detection:
    key: str
    confidence: DetectionConfidence
    evidence: tuple[str, ...] = ()


@dataclass(slots=True)
class ProjectManifest:
    version: int = 1
    profile: str = "python-backend"
    rules_version: str = ""
    ides: list[str] | None = None
    language: dict[str, bool] = field(default_factory=dict)
    backend: dict[str, bool] = field(default_factory=dict)
    data: dict[str, bool] = field(default_factory=dict)
    messaging: dict[str, bool] = field(default_factory=dict)
    security: dict[str, bool] = field(default_factory=dict)
    frontend: dict[str, bool | str] = field(default_factory=dict)
    ml: dict[str, bool] = field(default_factory=dict)
    infrastructure: dict[str, bool] = field(default_factory=dict)
    extra_profiles: list[str] = field(default_factory=list)
    include_modules: list[str] = field(default_factory=list)
    exclude_modules: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class EffectiveRules:
    modules: tuple[str, ...]
    rules: tuple[RuleDocument, ...]
    sources: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class PlannedWrite:
    path: Path
    content: str
    changed: bool


@dataclass(frozen=True, slots=True)
class PlannedDelete:
    path: Path
    changed: bool


@dataclass(frozen=True, slots=True)
class DoctorFinding:
    level: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class SyncResult:
    writes: tuple[PlannedWrite, ...]
    selected_profiles: tuple[str, ...]
    detections: tuple[Detection, ...] = ()
    warnings: tuple[str, ...] = ()
    deletes: tuple[PlannedDelete, ...] = ()
