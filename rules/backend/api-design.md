+++
id = "backend.api-design"
title = "API Design"
severity = "preferred"
scopes = ["backend"]
+++
# API Design

- Preserve existing API contracts unless a change is explicitly requested.
- Validate input at the boundary, use explicit response schemas, stable error contracts, and appropriate status codes.
- Keep transport concerns thin; business logic belongs in reusable application/domain services.
- Design idempotency for externally retried state-changing operations where duplicates are possible.
