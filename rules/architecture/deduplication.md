+++
id = "architecture.deduplication"
title = "Deduplication"
severity = "conditional"
scopes = ["architecture"]
+++
# Deduplication

- For at-least-once delivery, design durable deduplication using stable message/event identifiers and appropriate retention.
- Make deduplication concurrency-safe and observable.
