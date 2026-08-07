+++
id = "ml.batching"
title = "ML Batching"
severity = "conditional"
scopes = ["ml"]
+++
# Batching

- Use bounded batching when it measurably improves GPU/CPU throughput without violating latency/SLA constraints.
- Set maximum batch size, wait window, memory budget, backpressure, and partial-failure semantics explicitly.
