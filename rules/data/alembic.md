+++
id = "data.alembic"
title = "Alembic"
severity = "conditional"
scopes = ["python", "data"]
+++
# Alembic

- SQLAlchemy schema changes require an Alembic migration unless the project has an established equivalent.
- Review generated migrations; do not assume autogenerate captures data migration, constraint, enum, index, or downgrade semantics correctly.
- Prefer backward-compatible rollout when deployments can overlap versions.
