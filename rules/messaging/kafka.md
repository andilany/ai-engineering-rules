+++
id = "messaging.kafka"
title = "Kafka"
severity = "user_decision"
scopes = ["messaging"]
+++
# Kafka

- Kafka introduction requires explicit user approval and a concrete justification such as high-throughput durable event streams, replay, partitioned ordering, or multi-consumer retention requirements.
- Prefer existing RabbitMQ/Redis infrastructure when it satisfies the actual workload.
- Never migrate queues/events to Kafka as a generic scalability upgrade.
