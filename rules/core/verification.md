+++
id = "core.verification"
title = "Verification Honesty"
severity = "required"
scopes = ["all"]
+++
# Verification Honesty

- Never claim a test, lint, type check, security scan, build, migration, deployment, or command passed unless it was actually executed successfully.
- Report skipped or unavailable verification explicitly.
- If verification fails, preserve the failure signal and fix the underlying issue rather than weakening checks.
- Distinguish observed results from assumptions.
