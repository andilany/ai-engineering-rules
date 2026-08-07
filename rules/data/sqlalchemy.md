+++
id = "data.sqlalchemy"
title = "SQLAlchemy"
severity = "conditional"
scopes = ["python", "data"]
+++
# SQLAlchemy

- For non-Django relational Python projects, prefer current SQLAlchemy 2.x ORM style and async sessions when the driver supports async I/O.
- Keep session/transaction ownership explicit and avoid hidden global sessions.
- Direct SQL is acceptable when justified by performance or database-specific behavior, but it must be parameterized and follow project data-access conventions.
