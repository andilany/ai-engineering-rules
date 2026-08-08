+++
id = "messaging.aiormq"
title = "aiormq"
severity = "conditional"
scopes = ["python", "messaging"]
+++
# aiormq

- Use `aiormq` when lower-level AMQP control is required or the existing project already relies on it.
- Do not replace a working aio-pika abstraction with aiormq without a specific need and approval.
