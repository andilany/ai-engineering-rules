+++
id = "security.jwt"
title = "JWT"
severity = "conditional"
scopes = ["security"]
+++
# JWT

- Validate signature, allowed algorithms, issuer, audience, expiry, not-before where used, and token purpose/type.
- Access, refresh, and ID tokens are not interchangeable.
- Prefer short-lived access tokens and replay-aware refresh/session handling; avoid logging raw tokens.
