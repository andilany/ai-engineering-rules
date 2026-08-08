+++
id = "ml.service-boundaries"
title = "ML Service Boundaries"
severity = "conditional"
scopes = ["ml"]
+++
# ML Service Boundaries

- Keep ML/GPU services independently understandable with explicit input/output contracts and resource ownership.
- Gateway, orchestration, IO/DB, and model-service separation is appropriate when the project has chosen those boundaries; never split or merge services without user approval.
