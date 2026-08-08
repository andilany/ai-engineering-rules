+++
id = "infrastructure.healthchecks"
title = "Health Checks"
severity = "conditional"
scopes = ["infrastructure"]
+++
# Health Checks

- Implement liveness/readiness/startup checks when the runtime/orchestrator uses them.
- Liveness should detect unrecoverable process state; readiness should reflect ability to serve traffic without causing restart loops for downstream outages.
- Keep health endpoints lightweight and avoid exposing secrets/internal diagnostics publicly.
