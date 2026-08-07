+++
id = "architecture.idempotency"
title = "Idempotency"
severity = "required"
scopes = ["architecture", "backend"]
+++
# Idempotency

- Externally retried or distributed state-changing operations must be safe against duplicate delivery when duplicates are possible.
- Prefer durable idempotency keys, uniqueness constraints, transactional state transitions, or equivalent guarantees at the correct boundary.
- Do not rely only on an in-memory pre-check for correctness under concurrency.
