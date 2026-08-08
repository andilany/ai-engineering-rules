+++
id = "security.auth"
title = "Authentication"
severity = "required"
scopes = ["security"]
+++
# Authentication

- Prefer maintained authentication/OIDC libraries over hand-rolled protocol implementations.
- Do not store long-lived refresh credentials in JavaScript-readable `localStorage` as the default browser architecture; prefer safer session/BFF or HttpOnly cookie designs when appropriate.
- Separate authentication from authorization and validate token purpose and session lifecycle explicitly.
- Never invent cryptographic protocols or custom token formats for convenience.
