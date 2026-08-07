+++
id = "quality.testing"
title = "Testing"
severity = "required"
scopes = ["quality"]
+++
# Testing

- Use risk-based testing. Critical authentication, authorization, payments, migrations, concurrency, idempotency, distributed messaging, and data-integrity behavior deserve strong happy/error/boundary coverage.
- Bug fixes require a regression test when practical.
- Unit and integration tests are both required where they validate different failure boundaries.
- Coverage percentage is a signal, not the goal; never add meaningless tests solely to raise a number.
- Tests should verify behavior/contracts rather than incidental implementation details.
