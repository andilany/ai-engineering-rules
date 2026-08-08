+++
id = "backend.pydantic"
title = "Pydantic"
severity = "conditional"
scopes = ["python", "backend"]
+++
# Pydantic

- In FastAPI projects, prefer Pydantic for API validation and serialization unless the project already standardizes another contract layer.
- Keep boundary schemas separate from persistence models when their lifecycles differ.
- Use current stable Pydantic APIs and explicit validation rules.
