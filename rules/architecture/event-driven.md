+++
id = "architecture.event-driven"
title = "Event-Driven Architecture"
severity = "user_decision"
scopes = ["architecture"]
+++
# Event-Driven Architecture

- Event-driven architecture is a user decision; never introduce it or convert synchronous flows to events without explicit approval.
- When it is selected or already exists, define event ownership, schemas, idempotency, ordering assumptions, retries, dead-letter behavior, observability, and replay strategy.
