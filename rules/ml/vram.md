+++
id = "ml.vram"
title = "VRAM Management"
severity = "conditional"
scopes = ["ml"]
+++
# VRAM Management

- Treat VRAM as a bounded shared resource with explicit model lifecycle, allocation, cleanup, and failure recovery.
- Release references/caches when safe, observe VRAM usage, and avoid loading duplicate models per request.
- Define behavior for OOM, cancellation, partial failure, and worker restart.
