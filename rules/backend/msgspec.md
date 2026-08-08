+++
id = "backend.msgspec"
title = "msgspec"
severity = "conditional"
scopes = ["python", "backend", "django"]
+++
# msgspec

- Prefer `msgspec` for serialization/contracts in the selected django-modern-rest stack.
- Do not introduce it into an existing project that already has a stable serialization layer unless there is a measured benefit and user approval.
