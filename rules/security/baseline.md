+++
id = "security.baseline"
title = "Security Baseline"
severity = "required"
scopes = ["security"]
+++
# Security Baseline

- Validate untrusted input at trust boundaries and use least privilege.
- Keep authentication and authorization enforcement server-side and deny by default where access is not explicitly granted.
- Use parameterized database access, safe output encoding, secure transport, and dependency/security scanning appropriate to the project.
- Never weaken a security control merely to make tests or local development pass.
