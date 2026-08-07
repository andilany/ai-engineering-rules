+++
id = "quality.pytest"
title = "pytest"
severity = "preferred"
scopes = ["python", "quality"]
+++
# pytest

- Prefer pytest, pytest-asyncio for async behavior, fixtures/factories for reusable setup, and mocks only at genuine external boundaries.
- Avoid shared mutable test state and fixed sleeps; use deterministic synchronization and time controls.
- Test real error paths, transactions, retries, and integration boundaries where risk warrants it.
