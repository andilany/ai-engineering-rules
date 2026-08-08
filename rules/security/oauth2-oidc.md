+++
id = "security.oauth2-oidc"
title = "OAuth2 and OIDC"
severity = "conditional"
scopes = ["security"]
+++
# OAuth2 / OIDC

- Follow current OAuth2/OIDC security guidance and the chosen provider/library.
- Use Authorization Code + PKCE for browser/public-client flows where applicable; bind and validate `state`, and validate OIDC `nonce` where applicable.
- Validate redirect URIs strictly and do not move authorization codes through extra browser hops without a concrete reason.
