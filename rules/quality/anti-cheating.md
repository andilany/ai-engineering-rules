+++
id = "quality.anti-cheating"
title = "Quality Gate Integrity"
severity = "required"
scopes = ["quality"]
+++
# Quality Gate Integrity

- Never delete or skip a failing test solely to make CI green.
- Never weaken an assertion, security check, type configuration, lint rule, or error handling merely to satisfy a tool.
- Never mock the behavior under test, hard-code test outputs into production code, or claim verification that was not executed.
- Broad `noqa`, `type: ignore`, disabled linting, or swallowed exceptions require an explicit technical reason.
