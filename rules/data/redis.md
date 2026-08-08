+++
id = "data.redis"
title = "Redis"
severity = "conditional"
scopes = ["data"]
+++
# Redis

- Use Redis for caching, ephemeral coordination, rate limiting, short-lived state, or selected queue/backplane use cases when those requirements exist.
- Do not treat Redis as a durable source of truth unless persistence and failure semantics were explicitly designed.
- Set TTLs, key namespaces, memory policy, serialization, and stampede protection deliberately.
