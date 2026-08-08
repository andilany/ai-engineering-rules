+++
id = "security.dependencies"
title = "Dependency Security"
severity = "required"
scopes = ["security"]
+++
# Dependency Security

- Prefer current stable compatible dependencies; avoid prerelease versions unless the project explicitly accepts an exception.
- Check current documentation/release constraints before installing, upgrading, or integrating fast-moving libraries.
- Do not perform bulk dependency upgrades unrelated to the task.
- Security fixes should preserve compatibility where possible and be verified by tests/scans.
