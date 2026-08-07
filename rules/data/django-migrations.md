+++
id = "data.django-migrations"
title = "Django Migrations"
severity = "conditional"
scopes = ["python", "django", "data"]
+++
# Django Migrations

- Django model/schema changes require Django migrations.
- Review data migrations and deployment ordering for large tables, locks, defaults, backfills, and mixed-version operation.
