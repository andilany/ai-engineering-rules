+++
id = "infrastructure.kubernetes"
title = "Kubernetes"
severity = "user_decision"
scopes = ["infrastructure"]
+++
# Kubernetes

- Introducing Kubernetes is a user decision requiring explicit approval and justification from scaling, availability, deployment, multi-service operations, or platform requirements.
- Never migrate a working Docker/Compose deployment to Kubernetes as a generic maturity upgrade.
- When selected, define resources, probes, security context, disruption, rollout, configuration/secrets, and observability deliberately.
