+++
id = "architecture.sla-timers"
title = "SLA Timers"
severity = "conditional"
scopes = ["architecture"]
+++
# SLA Timers

- When business workflows have deadlines, model SLA timers explicitly and durably rather than relying on process-local sleeps.
- Define timezone, retry, restart, missed-deadline, and cancellation semantics.
