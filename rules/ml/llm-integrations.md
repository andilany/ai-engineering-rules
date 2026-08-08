+++
id = "ml.llm-integrations"
title = "LLM Integrations"
severity = "conditional"
scopes = ["ml"]
+++
# LLM Integrations

- Prefer structured, versioned input/output schemas and deterministic parsing where practical.
- Treat model output as untrusted input: validate shape, bounds, permissions, and downstream side effects.
- Track model/provider/version, latency, cost, retries, and failure modes where operationally relevant.
- Never let an LLM directly perform privileged destructive actions without the application's authorization/confirmation boundary.
