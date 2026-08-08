+++
id = "architecture.retry-backoff"
title = "Retry and Backoff"
severity = "conditional"
scopes = ["architecture"]
+++
# Retry and Backoff

- Retry only transient failures and use bounded attempts with backoff and jitter where appropriate.
- Preserve idempotency before retrying side effects.
- Do not retry validation, authorization, or permanent business failures.
