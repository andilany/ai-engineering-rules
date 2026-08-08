+++
id = "ml.parallel-processing"
title = "ML Parallel Processing"
severity = "conditional"
scopes = ["ml"]
+++
# Parallel Processing

- Separate async I/O concurrency from CPU/GPU parallelism.
- Bound concurrency according to VRAM, RAM, CPU, downstream rate limits, and queue capacity.
- Avoid unbounded `gather`/task creation for large datasets.
