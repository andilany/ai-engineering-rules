+++
id = "quality.typing"
title = "Typing"
severity = "required"
scopes = ["python", "quality"]
+++
# Typing

- Public and non-trivial Python code should have useful parameter and return annotations.
- Prefer precise types and protocols over `Any`; document unavoidable dynamic boundaries.
- Keep type checking compatible with the project's configured checker and strictness.
- Do not add broad type ignores to silence a local problem.
