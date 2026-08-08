+++
id = "infrastructure.caddy"
title = "Caddy"
severity = "preferred"
scopes = ["infrastructure"]
+++
# Caddy

- For new simple reverse-proxy/TLS deployments when no proxy is selected, prefer Caddy for concise configuration and automatic HTTPS.
- Preserve existing Nginx, ingress, load balancer, or proxy infrastructure unless the user approves migration.
- Make forwarded headers, upstream timeouts, WebSocket behavior, TLS, and access logging explicit.
