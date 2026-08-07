+++
id = "messaging.rabbitmq"
title = "RabbitMQ"
severity = "preferred"
scopes = ["messaging"]
+++
# RabbitMQ

- When a message broker is actually needed and no existing broker is mandated, prefer RabbitMQ for work queues, routing, RPC-style messaging, and event delivery in this engineering profile.
- Existing broker choices take precedence; do not introduce RabbitMQ merely because this preference exists.
- Define durable topology where needed, ack/nack behavior, prefetch/backpressure, publisher confirms where loss matters, retry/DLQ policy, correlation IDs, and graceful shutdown.
