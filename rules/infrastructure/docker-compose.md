+++
id = "infrastructure.docker-compose"
title = "Docker Compose"
severity = "conditional"
scopes = ["infrastructure"]
+++
# Docker Compose

- Use Docker Compose for local/multi-service environments when it reduces setup friction.
- Treat Docker → Docker Compose → Kubernetes → Helm → GitOps as increasing complexity, not an automatic migration path.
- Keep local and production assumptions explicit; Compose is not automatically a production orchestrator.
