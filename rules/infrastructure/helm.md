+++
id = "infrastructure.helm"
title = "Helm"
severity = "user_decision"
scopes = ["infrastructure"]
+++
# Helm

- Introducing Helm requires explicit user approval and a real need for templated/reusable Kubernetes packaging.
- Do not add Helm to a simple Kubernetes deployment solely because it is common.
- Keep values schemas, defaults, secrets boundaries, and upgrade compatibility explicit.
