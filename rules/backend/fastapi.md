+++
id = "backend.fastapi"
title = "FastAPI"
severity = "preferred"
scopes = ["python", "backend"]
+++
# FastAPI

- For greenfield Python APIs when no framework was chosen, prefer FastAPI.
- Existing frameworks take precedence; never migrate an established API to FastAPI without user approval.
- Use dependency injection deliberately, keep route handlers thin, and avoid blocking I/O in async endpoints.
- Follow current stable FastAPI APIs and project conventions rather than remembered outdated examples.
