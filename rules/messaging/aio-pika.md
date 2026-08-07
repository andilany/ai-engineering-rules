+++
id = "messaging.aio-pika"
title = "aio-pika"
severity = "conditional"
scopes = ["python", "messaging"]
+++
# aio-pika

- Prefer `aio-pika` for high-level asynchronous RabbitMQ integrations in Python.
- Reuse existing connection/channel lifecycle abstractions and robust connection patterns rather than creating a new client per message.
