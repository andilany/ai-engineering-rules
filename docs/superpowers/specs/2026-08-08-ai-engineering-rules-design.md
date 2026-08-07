# AI Engineering Rules — Design Specification

Date: 2026-08-08
Status: Approved architecture, pending written-spec review

## 1. Goal

Build a private, reusable, versioned engineering rule-pack for AI coding agents. The system must provide a single canonical source of engineering rules and generate thin, agent-specific adapters for Codex, Claude Code, Cursor, and Gemini CLI.

The rule-pack must improve consistency and safety without silently redesigning projects, changing architecture, committing code, migrating dependencies, or performing other external side effects without explicit user approval.

The canonical rules are written in English. Human-facing repository documentation is written in Russian where practical.

## 2. Core Principles

1. Project reality overrides generic preferences.
2. Existing architecture is preserved by default.
3. Architecture choices are USER_DECISION, not mandatory defaults.
4. Agents may propose architectural or tooling changes with concrete trade-offs, but must not apply them without explicit user approval.
5. Existing projects preserve their current package manager and conventions unless migration is explicitly approved.
6. New Python projects prefer the latest stable Python release supported by the selected dependencies; prerelease/alpha/beta/RC packages are avoided unless explicitly approved or listed as a documented exception.
7. `django-modern-rest` is an explicit allowed exception to the stable-only dependency rule.
8. Greenfield Python projects prefer `uv` for dependency management.
9. Existing Poetry/pip/pip-tools/uv projects remain on their current package manager. The agent may propose migration to `uv`, explain benefits/costs, and must wait for approval before changing anything.
10. Git is required for project work, but all commits, pushes, branch changes, PR creation, merges, repository creation, history rewriting, and destructive Git operations require explicit user agreement. The user owns commits.
11. The rules system itself must never mutate application architecture, install infrastructure, migrate dependencies, or edit business code. It only manages AI instruction files.

## 3. Rule Severity Model

Canonical rules are classified into five semantic levels:

- REQUIRED: invariant that should be followed unless a higher-priority project/user instruction explicitly overrides it.
- PREFERRED: engineering default for greenfield work or when the project has no established convention.
- CONDITIONAL: applies only when the referenced technology or concern is already present or explicitly selected.
- OPTIONAL: useful suggestion that the agent may offer when relevant.
- USER_DECISION: the agent may analyze and recommend, but must not choose or apply the decision without explicit approval.

Examples:

REQUIRED:
- Do not expose secrets.
- Do not claim tests passed unless they were executed.
- Do not commit/push without explicit approval.
- Do not weaken security or tests merely to make CI green.

PREFERRED:
- `uv` for new Python projects.
- FastAPI for a new Python API when no framework is selected.
- PostgreSQL over MongoDB for relational domain models.
- RabbitMQ/Redis over Kafka unless Kafka has a justified need.

CONDITIONAL:
- SQLAlchemy rules when SQLAlchemy is used.
- Alembic rules when Alembic is used.
- CUDA/VRAM rules for GPU services.

OPTIONAL:
- Suggest OpenTelemetry when distributed tracing would materially help.
- Suggest `uv` migration in a Poetry project with justification.

USER_DECISION:
- monolith vs microservices
- event-driven vs request/response
- orchestration vs choreography
- RabbitMQ vs Kafka when a new broker is being selected
- adding Kubernetes
- introducing CQRS/event sourcing
- changing frontend architecture

## 4. Rule Precedence

Highest to lowest:

1. Explicit user instruction for the current task.
2. Project-specific rules in the target repository.
3. Service/module-specific instructions closer to the code being changed.
4. Active technology/profile rules.
5. Universal Core.
6. General preferences.

Additional precedence rules:

- More specific instructions override broader instructions.
- Existing project conventions override greenfield preferences.
- A PREFERRED rule never authorizes migration from an existing tool or architecture.
- USER_DECISION rules can never be silently resolved by the agent.
- Security invariants may only be relaxed when explicitly requested and when the requested change is itself acceptable and clearly understood.

## 5. Canonical Repository Structure

```text
ai-engineering-rules/
├── README.md
├── pyproject.toml
├── CHANGELOG.md
├── PRIVATE.md
├── rules/
│   ├── core/
│   │   ├── agent-behavior.md
│   │   ├── scope-discipline.md
│   │   ├── workflow.md
│   │   ├── verification.md
│   │   ├── external-actions.md
│   │   └── documentation.md
│   ├── languages/
│   │   └── python.md
│   ├── backend/
│   │   ├── async-python.md
│   │   ├── fastapi.md
│   │   ├── django.md
│   │   ├── django-modern-rest.md
│   │   ├── pydantic.md
│   │   ├── msgspec.md
│   │   ├── api-design.md
│   │   └── uvicorn-asgi.md
│   ├── architecture/
│   │   ├── architecture-decisions.md
│   │   ├── microservices.md
│   │   ├── event-driven.md
│   │   ├── saga.md
│   │   ├── orchestration.md
│   │   ├── idempotency.md
│   │   ├── retry-backoff.md
│   │   ├── deduplication.md
│   │   ├── sla-timers.md
│   │   └── api-gateway.md
│   ├── data/
│   │   ├── postgresql.md
│   │   ├── sqlalchemy.md
│   │   ├── alembic.md
│   │   ├── django-orm.md
│   │   ├── django-migrations.md
│   │   ├── redis.md
│   │   └── mongodb.md
│   ├── messaging/
│   │   ├── rabbitmq.md
│   │   ├── aio-pika.md
│   │   ├── aiormq.md
│   │   ├── celery.md
│   │   └── kafka.md
│   ├── security/
│   │   ├── baseline.md
│   │   ├── auth.md
│   │   ├── keycloak.md
│   │   ├── oauth2-oidc.md
│   │   ├── jwt.md
│   │   ├── rbac.md
│   │   ├── secrets.md
│   │   └── dependencies.md
│   ├── quality/
│   │   ├── testing.md
│   │   ├── pytest.md
│   │   ├── typing.md
│   │   ├── ruff.md
│   │   ├── bandit.md
│   │   └── anti-cheating.md
│   ├── frontend/
│   │   ├── typescript.md
│   │   ├── react.md
│   │   ├── nextjs.md
│   │   ├── tailwind.md
│   │   ├── shadcn-radix.md
│   │   ├── tanstack-query.md
│   │   ├── zustand.md
│   │   ├── forms-zod.md
│   │   └── api-client.md
│   ├── ml/
│   │   ├── service-boundaries.md
│   │   ├── gpu-cuda.md
│   │   ├── vram.md
│   │   ├── batching.md
│   │   ├── parallel-processing.md
│   │   ├── pipelines.md
│   │   └── llm-integrations.md
│   └── infrastructure/
│       ├── docker.md
│       ├── docker-compose.md
│       ├── kubernetes.md
│       ├── helm.md
│       ├── gitops.md
│       ├── caddy.md
│       ├── nginx.md
│       ├── linux.md
│       ├── windows.md
│       ├── ansible.md
│       ├── ci-cd.md
│       ├── observability.md
│       ├── prometheus-grafana.md
│       ├── opentelemetry.md
│       └── healthchecks.md
├── profiles/
│   ├── python-backend.toml
│   ├── fastapi-backend.toml
│   ├── django-backend.toml
│   ├── ml-gpu-service.toml
│   ├── frontend-nextjs.toml
│   └── fullstack-python.toml
├── adapters/
│   ├── codex/
│   ├── claude/
│   ├── cursor/
│   └── gemini/
└── src/
    └── ai_rules/
        ├── cli.py
        ├── config.py
        ├── detection.py
        ├── profiles.py
        ├── rendering.py
        ├── managed_blocks.py
        ├── doctor.py
        └── adapters/
```

The initial implementation may use fewer files by grouping closely related rules. The structure above defines the intended boundaries, not a requirement to create empty placeholder files.

## 6. Python Backend Defaults

### Language and dependency policy

- Python is the only backend language profile in v1.
- Prefer the latest stable Python release compatible with the project's dependencies.
- Existing projects preserve their configured Python version unless an upgrade is requested.
- Greenfield dependency manager: `uv`.
- Existing dependency manager: preserve; migration requires approval.
- Prefer latest stable compatible dependency versions.
- Avoid prerelease/alpha/beta/RC dependencies unless explicitly approved.
- Explicit exception: `django-modern-rest`.

### Backend frameworks

FastAPI:
- primary default for new Python APIs when no framework has been selected.
- Pydantic is the primary schema/validation layer.
- ASGI/Uvicorn are the default runtime model.

Django:
- valid alternative selected by user/project requirements.
- `django-modern-rest` is the required preferred REST layer for new Django API work unless the existing project uses another established API layer.
- `msgspec` is preferred for serialization/schema work where compatible with django-modern-rest and the project architecture.
- Maximize async use where Django and dependencies support it; do not force unsafe or fake async wrappers around synchronous-only operations.

### Data access

Every persistent relational data project should use an ORM unless the user/project explicitly requires otherwise:
- FastAPI/general Python: SQLAlchemy 2.x style preferred.
- Django: Django ORM.

Schema changes require migrations:
- SQLAlchemy: Alembic.
- Django ORM: Django migrations.

Direct SQL is allowed for justified performance/DB-specific needs, but must remain parameterized, reviewed for correctness, and fit the project's repository/data-access conventions.

## 7. Async-First Policy

The codebase should be asynchronous wherever I/O concurrency provides real value:

- async HTTP
- async DB drivers/ORM APIs where supported
- async RabbitMQ clients (`aio-pika`, `aiormq`)
- async Redis clients
- async filesystem/network calls where libraries permit

Do not blindly wrap synchronous libraries in async APIs. Use thread/process offloading where appropriate and document blocking boundaries.

## 8. Data Defaults

Preferred relational database: PostgreSQL.

Redis is a standard supporting technology for:
- cache
- ephemeral state
- distributed locks where appropriate
- Celery broker/backend where selected
- lightweight queue/pub-sub cases when semantics are sufficient

MongoDB is supported but not a greenfield default. Use when document-oriented schema/access patterns provide a clear benefit.

Rules should cover:
- transactions
- locking/concurrency
- indexes
- migration safety
- connection pooling
- N+1 avoidance
- query planning for performance-critical paths
- idempotency where state changes are externally repeatable

## 9. Messaging Defaults

Preferred broker: RabbitMQ.

Preferred Python clients:
- `aio-pika`
- `aiormq`

Celery is supported when task semantics fit.

Kafka is not a default. An agent proposing Kafka must explain the concrete requirement RabbitMQ/Redis do not satisfy, such as high-throughput retained event streams, partitioned ordered logs, replay, or ecosystem requirements.

Introducing Kafka is USER_DECISION.

Messaging rules cover:
- at-least-once delivery assumptions
- idempotent consumers
- publisher confirms where required
- ack/nack behavior
- retries/backoff
- poison-message/DLQ strategy
- deduplication
- correlation IDs
- graceful shutdown
- consumer concurrency limits
- backpressure

## 10. Architecture

No architecture is globally mandatory.

Agents may recommend:
- modular monolith
- microservices
- event-driven architecture
- saga
- orchestration
- choreography
- API Gateway
- distributed queues

But introducing or migrating between these is USER_DECISION.

The rules should help evaluate:
- independently deployable boundaries
- independent scaling needs
- failure isolation
- operational complexity
- transactional boundaries
- distributed consistency
- team ownership
- GPU/CPU workload isolation
- latency requirements
- data ownership

When distributed/event-driven patterns are already selected, the rules should strongly enforce:
- idempotency
- retry/backoff
- deduplication
- timeout/cancellation
- SLA timers where applicable
- observability
- correlation/trace IDs
- explicit failure states

## 11. Authentication and Security

Preferred identity platform: Keycloak when centralized identity/RBAC is required and project requirements fit.

Supported concepts:
- OAuth2
- OIDC
- JWT
- RBAC

Security invariants:
- no invented crypto/auth protocols
- OAuth/OIDC state validation
- PKCE where applicable
- issuer/audience/signature/expiry validation
- distinguish access/refresh/ID token purpose
- prevent refresh token from being accepted as an access token
- avoid long-lived credentials in JS-readable storage by default
- least privilege
- deny-by-default authorization boundaries
- secrets never logged or committed
- user input validation
- parameterized SQL

## 12. Quality

Every new project profile should include:
- Ruff
- static typing
- Bandit
- unit tests
- integration tests where external boundaries exist

Python test preferences:
- pytest
- pytest-asyncio for async behavior
- mocks/fakes only at external boundaries where practical

Testing is risk-based rather than coverage-percentage-driven.

Critical areas receive stronger testing:
- authentication/authorization
- payments/credits
- concurrent state changes
- migrations
- idempotency
- retries
- event consumers
- data integrity

Bug fixes should include regression tests when practical.

Forbidden AI shortcuts:
- removing a failing test to get green
- weakening assertions without justification
- global linter disable for a local issue
- unexplained broad `noqa` / `type: ignore`
- hardcoding expected test output into production code
- claiming checks passed without execution

## 13. Frontend Profile

Greenfield preferred stack:
- TypeScript
- React
- Next.js
- HTML5/CSS3
- Tailwind CSS
- REST API
- WebSocket when required
- shadcn/ui
- Radix UI
- Lucide
- TanStack Query
- Zustand
- Axios or Fetch according to project convention
- React Hook Form
- Zod

Existing frontend frameworks are preserved. The presence of this profile does not authorize migration from another frontend framework.

## 14. ML / Data / GPU Profile

Supports:
- FastAPI model-serving services
- GPU/CUDA services
- ML/NLP microservices
- orchestration service
- API gateway
- IO/DB service
- VRAM management
- batching
- parallel processing
- task queues
- data-processing pipelines
- LLM integrations
- entity/event/relation extraction services

Rules should specifically encourage cost-safe validation:
- unit-test GPU-independent logic locally
- contract-test service boundaries
- CPU/mock/fake execution paths when meaningful
- validate model loading configuration before GPU allocation
- bound batch sizes/concurrency
- manage VRAM lifecycle explicitly
- surface empty/invalid model output as a failure state, not silently successful processing

Actual decomposition into these service types is USER_DECISION unless already established by the project.

## 15. Infrastructure

Progression model:

```text
Docker → Docker Compose → Kubernetes → Helm → GitOps
```

The arrows describe increasing deployment complexity, not an automatic migration path.

Preferred/supporting technologies:
- Caddy as preferred reverse proxy for new simple deployments
- Nginx as supported secondary/existing-project option
- Linux primary runtime environment
- Windows supported development environment
- Ansible
- CI/CD
- Prometheus
- Grafana
- OpenTelemetry
- structured logging
- healthchecks
- readiness/liveness probes

Kubernetes/Helm/GitOps are USER_DECISION for projects that do not already use them.

## 16. Distribution Model

The canonical rules live in one private Git repository and are installed as a Python CLI tool.

Suggested package/command name for v1: `airules`.

Installation concept:

```bash
uv tool install "git+ssh://git@github.com/andilany/ai-engineering-rules.git"
```

No application project needs a full copy or Git submodule of the canonical repository.

## 17. CLI Commands

### `airules bootstrap`

Installs only the small Universal Core into each supported agent's global instruction location where supported.

Requirements:
- preserve existing global user instructions
- use managed blocks or generated references where possible
- never overwrite unrelated content
- dry-run support

### `airules init`

Initializes rules for the current application project.

Behavior:
1. Inspect stack/configuration files only.
2. Detect likely technologies and existing agent files.
3. Suggest profiles.
4. Generate `.ai-rules.toml`.
5. Generate a project-level rules snapshot/adapters.
6. Preserve existing user-authored agent content.

It must not:
- install application dependencies
- migrate package managers
- modify application source code
- create Git commits
- create branches
- push
- change architecture

### `airules init --profile <name>`

Explicit profile initialization for greenfield or manually selected projects.

### `airules add <profile-or-module>`

Adds rule modules to the project manifest only. It does not install the technology into the project.

### `airules sync`

Re-renders agent adapters from the current canonical rules and `.ai-rules.toml`.

Must be idempotent.

### `airules doctor`

Reports:
- installed rule-pack version
- project manifest validity
- enabled profiles/modules
- supported-agent adapter status
- stale/missing managed blocks
- configuration conflicts

Read-only by default.

### `airules explain`

Displays active rules grouped by severity and source, so the user can understand why an agent receives a particular preference or restriction.

### `airules detect`

Optional read-only command to display stack detection results without writing any files.

## 18. Project Manifest

Each project stores a small manifest:

```text
.ai-rules.toml
```

The manifest describes active rule modules. It does not declare required application architecture.

Example:

```toml
version = 1
profile = "python-backend"

[language]
python = true

[backend]
fastapi = true
django = false

[data]
postgresql = true
sqlalchemy = true
alembic = true
redis = true

[messaging]
rabbitmq = true
celery = false
kafka = false

[security]
keycloak = true

[frontend]
enabled = false

[ml]
enabled = false

[infrastructure]
docker = true
compose = true
kubernetes = false
helm = false
```

The manifest must support manual edits and stable formatting.

## 19. Project-specific Rules

Each project may contain:

```text
.ai-rules/project.md
```

This is user-owned project-specific guidance and must never be overwritten by `airules sync`.

Examples:
- service boundaries
- expensive GPU test constraints
- project-specific repository abstractions
- logging/configuration conventions
- business-sensitive restrictions

Project rules have higher priority than canonical technology preferences.

## 20. Generated Files and Managed Blocks

Expected project integration:

```text
.ai-rules.toml
.ai-rules/generated.md
.ai-rules/project.md
AGENTS.md
CLAUDE.md
GEMINI.md
.cursor/rules/engineering.mdc
```

Adapters should be thin.

Existing agent files must be preserved. Managed content is delimited using markers such as:

```text
<!-- ai-engineering-rules:start -->
...
<!-- ai-engineering-rules:end -->
```

`airules sync` modifies only the managed section.

If an adapter supports clean file imports, the generated adapter should prefer importing/referencing `.ai-rules/generated.md` and `.ai-rules/project.md` over duplicating large text blocks.

## 21. Agent Adapters

### Codex

Generate/maintain `AGENTS.md` and preserve nested/project-specific precedence. The adapter should be concise and point to the generated project rules where compatible with Codex behavior.

### Claude Code

Generate/maintain `CLAUDE.md`, preferably using imports to `.ai-rules/generated.md` and `.ai-rules/project.md` where supported.

### Gemini CLI

Generate/maintain `GEMINI.md`, preferably using imports to generated/project rules where supported.

### Cursor

Generate `.cursor/rules/engineering.mdc` with suitable frontmatter/scope. Universal/project rules should be split only when it materially improves auto-attachment behavior.

## 22. Detection Strategy

Detection must be conservative and read-only.

Potential signals:

Python:
- `pyproject.toml`
- `.python-version`
- `requirements*.txt`

FastAPI:
- dependency declarations
- imports only when needed for ambiguous detection

Django:
- `manage.py`
- dependency declarations
- `settings.py`

SQLAlchemy/Alembic:
- dependency declarations
- `alembic.ini`

PostgreSQL/Redis/RabbitMQ:
- dependency declarations
- Docker Compose service names/images
- configuration templates

Frontend:
- `package.json`
- Next.js/React/TypeScript dependencies

Infrastructure:
- Dockerfile
- compose files
- `helm/`, `charts/`, `k8s/`

Detection output must distinguish:
- detected
- probable
- not detected

Ambiguous detections should be suggestions, not silently enabled modules.

## 23. Versioning and Updates

The rule-pack follows semantic versioning.

- Patch: wording fixes, non-behavioral refinements.
- Minor: new rules/modules/profiles, backward-compatible adapter features.
- Major: meaningfully changed precedence, severity semantics, manifest format, or behavior that may change agent decisions.

Generated project metadata records the rules version used for the last sync.

`airules doctor` reports stale generated adapters.

## 24. Safety and External Actions

The rule CLI itself must not perform application Git operations.

It may read Git metadata to detect repository root/status if helpful.

The AI rules explicitly require user approval before:
- commit
- push
- pull/rebase/merge with modification risk
- branch creation/switch when it affects user work
- PR creation
- repository creation
- tag/release creation
- destructive reset/clean/history rewrite
- deploy
- infrastructure mutation
- irreversible migration

Read-only Git inspection is allowed unless the user explicitly forbids it.

## 25. Initial Profiles

### `python-backend`

Includes:
- core
- Python
- async-first
- ORM/migrations principles
- PostgreSQL preferred
- Redis support
- security baseline
- quality baseline
- Git/external-action rules
- Docker basics

Does not force FastAPI/Django/RabbitMQ.

### `fastapi-backend`

Extends `python-backend` with:
- FastAPI
- Pydantic
- SQLAlchemy/Alembic defaults
- Uvicorn/ASGI
- RabbitMQ/aio-pika/aiormq preferred when messaging is needed

### `django-backend`

Extends `python-backend` with:
- Django
- django-modern-rest
- msgspec
- Django ORM/migrations
- async Django guidance

### `ml-gpu-service`

Extends FastAPI/Python rules where appropriate with:
- CUDA/GPU
- VRAM lifecycle
- batching
- pipeline/orchestration
- expensive-compute validation strategy

### `frontend-nextjs`

Includes frontend preferences only.

### `fullstack-python`

Combines selected Python backend and Next.js frontend rules without forcing deployment architecture.

## 26. Non-Goals for v1

- Go rules.
- Automatic application dependency installation.
- Automatic migration to `uv`.
- Automatic architecture migration.
- Automatic commit/push/PR creation.
- Full rule compiler/YAML DSL.
- Central SaaS service.
- Remote policy enforcement.
- Automatic code rewriting based on rule violations.

## 27. Implementation Quality Requirements

The CLI itself should use:
- Python latest stable compatible release
- `uv`
- Ruff
- typing/static analysis
- Bandit
- pytest
- pytest-asyncio only where asynchronous behavior exists

Core CLI operations are deterministic and testable.

At minimum test:
- manifest parsing
- profile composition
- precedence
- managed-block insertion/update/preservation
- idempotent sync
- detection on fixture projects
- adapter rendering
- preservation of existing AGENTS/CLAUDE/GEMINI/Cursor content
- dry-run behavior
- invalid/conflicting configuration handling

## 28. Success Criteria

The design is successful when:

1. The user installs one private CLI once.
2. A new project can be connected with `airules init`.
3. No canonical rule repository is copied into application repositories.
4. Existing project agent instructions remain intact.
5. `airules sync` updates generated instructions safely and idempotently.
6. Codex, Claude Code, Cursor, and Gemini CLI receive equivalent engineering intent through native adapters.
7. Existing architecture/tooling always wins over generic preferences unless the user approves a change.
8. Git writes and external side effects never happen merely because a rule recommends them.
9. The user can run `airules explain` to understand active rules.
10. The user can run `airules doctor` to diagnose stale/conflicting adapters.

