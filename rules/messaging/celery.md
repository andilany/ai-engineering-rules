+++
id = "messaging.celery"
title = "Celery"
severity = "conditional"
scopes = ["python", "messaging"]
+++
# Celery

- Use Celery when the project already uses it or its task semantics, scheduling, ecosystem, and operational model are a good fit.
- Keep tasks idempotent where retries are possible; define retry policy, serialization, time limits, routing, result backend needs, and worker shutdown behavior.
- Do not introduce Celery when a simpler existing async worker model is sufficient.
