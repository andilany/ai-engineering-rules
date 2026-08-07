+++
id = "architecture.saga"
title = "Saga"
severity = "conditional"
scopes = ["architecture"]
+++
# Saga

- Use Saga only for distributed business transactions that actually require compensation across independently committed steps.
- Make compensation, idempotency, failure states, and observability explicit.
- Introducing Saga where a local database transaction is sufficient requires user approval because it increases complexity.
