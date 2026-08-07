+++
id = "ml.gpu-cuda"
title = "GPU and CUDA"
severity = "conditional"
scopes = ["ml"]
+++
# GPU / CUDA

- Isolate CUDA/GPU-specific dependencies and make device requirements explicit.
- Before expensive GPU execution, prefer CPU-safe unit tests, contract tests, mocks/fakes of model boundaries, import/startup validation, and small deterministic fixtures when they can prove correctness.
- Real GPU tests remain necessary for device-specific kernels, memory behavior, model loading, and performance-critical integration paths.
