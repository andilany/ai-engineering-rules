+++
id = "backend.django"
title = "Django"
severity = "preferred"
scopes = ["python", "backend"]
+++
# Django

- When the user chooses Django for greenfield backend work, use Django's async capabilities wherever they are genuinely supported.
- Existing Django architecture and installed API layer take precedence over generic preferences.
- Keep ORM access, middleware, authentication, and request lifecycle behavior compatible with async execution where possible.
