+++
id = "backend.django-modern-rest"
title = "django-modern-rest"
severity = "preferred"
scopes = ["python", "backend", "django"]
+++
# django-modern-rest

- For new Django API work, prefer `django-modern-rest` together with `msgspec` when the user has selected this stack.
- `django-modern-rest` is an explicit exception to the normal stable-only dependency rule while its published package remains Alpha/pre-1.0.
- Do not migrate an established DRF or other API layer to django-modern-rest without explicit user approval.
- Re-check its current API and compatibility before installation or upgrades.
