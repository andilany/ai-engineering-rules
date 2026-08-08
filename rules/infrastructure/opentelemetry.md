+++
id = "infrastructure.opentelemetry"
title = "OpenTelemetry"
severity = "conditional"
scopes = ["infrastructure"]
+++
# OpenTelemetry

- Prefer OpenTelemetry for portable tracing/metrics instrumentation when distributed observability is needed.
- Propagate context across HTTP and messaging boundaries, sample deliberately, and avoid high-cardinality sensitive attributes.
