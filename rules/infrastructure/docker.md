+++
id = "infrastructure.docker"
title = "Docker"
severity = "preferred"
scopes = ["infrastructure"]
+++
# Docker

- Prefer reproducible container builds for deployable services in this profile.
- Use minimal runtime images, non-root users where practical, explicit health/runtime config, pinned compatible base versions, and `.dockerignore`.
- Do not rewrite existing containerization unrelated to the task.
